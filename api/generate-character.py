# api/generate-character.py
# 사용자 입력(이름/장르/키워드)을 받아 Gemini API를 호출하고
# 구조화된 캐릭터 설정(JSON)을 반환합니다.

import os
import json
from http.server import BaseHTTPRequestHandler

from google import genai
from google.genai import types


SYSTEM_INSTRUCTION = """당신은 창작자를 돕는 캐릭터 설정 작가입니다.
사용자가 준 이름(선택), 장르, 키워드를 바탕으로 캐릭터 설정을 만듭니다.
반드시 아래 JSON 형식으로만 응답하세요. 다른 설명이나 코드블록 표시(```)는 절대 포함하지 마세요.

{
  "name": "캐릭터 이름 (사용자가 이름을 주지 않았다면 장르/키워드에 어울리는 이름을 새로 지어주세요)",
  "personality": "성격 요약 (2~3문장)",
  "speech_style": "말투를 보여주는 예시 대사 1~2개",
  "backstory": "짧은 배경 이야기 (3~5문장)",
  "strengths": "강점 (1~2문장)",
  "weaknesses": "약점 (1~2문장)",
  "likes": "좋아하는 것 (짧게)",
  "dislikes": "싫어하는 것 (짧게)"
}
"""


def build_user_prompt(name, genre, keywords):
    name_part = f'이름 힌트: "{name}"' if name else "이름: 사용자가 정하지 않았으니 AI가 새로 지어주세요."
    return (
        f"{name_part}\n"
        f"장르/분위기: {genre}\n"
        f"핵심 키워드: {keywords}\n\n"
        "위 정보를 바탕으로 캐릭터 설정을 JSON으로 작성해주세요."
    )


def call_gemini(name, genre, keywords):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("서버에 AI API 키가 설정되어 있지 않습니다.")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=build_user_prompt(name, genre, keywords),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            temperature=0.9,
        ),
    )

    raw_text = response.text
    return json.loads(raw_text)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"
            payload = json.loads(body_bytes or b"{}")

            name = (payload.get("name") or "").strip()
            genre = (payload.get("genre") or "").strip()
            keywords = (payload.get("keywords") or "").strip()

            if not keywords:
                self._send_json(400, {
                    "success": False,
                    "error": "입력 내용을 확인해주세요. 핵심 키워드를 입력해주세요.",
                })
                return

            result = call_gemini(name, genre, keywords)
            self._send_json(200, {"success": True, "result": result})

        except json.JSONDecodeError:
            self._send_json(400, {
                "success": False,
                "error": "요청 형식이 올바르지 않습니다.",
            })
        except Exception:
            # 상세 원인은 서버 로그로만 남기고, 사용자에게는 일반 메시지만 노출합니다.
            self._send_json(500, {
                "success": False,
                "error": "AI 요청 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            })

    def _send_json(self, status_code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)