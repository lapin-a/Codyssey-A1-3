# api/get-characters.py
# Vercel Postgres의 characters 테이블에서 저장된 캐릭터 목록을 최신순으로 조회합니다.

import os
import json
from http.server import BaseHTTPRequestHandler

import psycopg2
import psycopg2.extras


def get_connection():
    conn_string = os.environ.get("POSTGRES_URL")
    if not conn_string:
        raise RuntimeError("서버에 데이터베이스 연결 정보가 설정되어 있지 않습니다.")
    return psycopg2.connect(conn_string)


def fetch_characters():
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, name, gender, age, species, religion, genre,
                       extra_info, personality, speech_style, backstory,
                       strengths, weaknesses, likes, dislikes, created_at
                FROM characters
                ORDER BY created_at DESC;
                """
            )
            rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            characters = fetch_characters()
            # datetime 객체는 JSON으로 바로 직렬화되지 않으므로 문자열로 변환합니다.
            for c in characters:
                if c.get("created_at"):
                    c["created_at"] = str(c["created_at"])

            self._send_json(200, {"success": True, "result": characters})

        except Exception:
            self._send_json(500, {
                "success": False,
                "error": "캐릭터를 불러오는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            })

    def _send_json(self, status_code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)