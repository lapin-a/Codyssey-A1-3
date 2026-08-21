# api/save-character.py
# 프론트에서 받은 캐릭터 데이터를 Vercel Postgres의 characters 테이블에 저장합니다.
#
# 사전 준비: Vercel Postgres 콘솔의 Query 탭에서 아래 SQL을 한 번 실행해야 합니다.
#
# CREATE TABLE characters (
#     id SERIAL PRIMARY KEY,
#     name TEXT NOT NULL,
#     gender TEXT,
#     age TEXT,
#     species TEXT,
#     religion TEXT,
#     genre TEXT,
#     keywords TEXT,
#     extra_info TEXT,
#     personality TEXT,
#     speech_style TEXT,
#     backstory TEXT,
#     strengths TEXT,
#     weaknesses TEXT,
#     likes TEXT,
#     dislikes TEXT,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );

import os
import json
from http.server import BaseHTTPRequestHandler

import psycopg2


def get_connection():
    conn_string = os.environ.get("STORAGE_URL")
    if not conn_string:
        raise RuntimeError("서버에 데이터베이스 연결 정보가 설정되어 있지 않습니다.")
    return psycopg2.connect(conn_string)


def insert_character(data):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO characters
                    (name, gender, age, species, religion, genre, keywords,
                     extra_info, personality, speech_style, backstory,
                     strengths, weaknesses, likes, dislikes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    data.get("name"),
                    data.get("gender"),
                    data.get("age"),
                    data.get("species"),
                    data.get("religion"),
                    data.get("genre"),
                    data.get("keywords"),
                    data.get("extra_info"),
                    data.get("personality"),
                    data.get("speech_style"),
                    data.get("backstory"),
                    data.get("strengths"),
                    data.get("weaknesses"),
                    data.get("likes"),
                    data.get("dislikes"),
                ),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"
            payload = json.loads(body_bytes or b"{}")

            name = (payload.get("name") or "").strip()
            if not name:
                self._send_json(400, {
                    "success": False,
                    "error": "저장할 캐릭터 이름이 없습니다.",
                })
                return

            new_id = insert_character(payload)
            self._send_json(200, {"success": True, "result": {"id": new_id}})

        except json.JSONDecodeError:
            self._send_json(400, {
                "success": False,
                "error": "요청 형식이 올바르지 않습니다.",
            })
        except Exception:
            self._send_json(500, {
                "success": False,
                "error": "저장 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            })

    def _send_json(self, status_code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)