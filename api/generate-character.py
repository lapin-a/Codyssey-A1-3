# api/generate-character.py
# 사용자 입력(이름/장르/키워드)을 받아 Gemini API를 호출하고
# 구조화된 캐릭터 설정(JSON)을 반환합니다.

import os
import json
from http.server import BaseHTTPRequestHandler

from google import genai
from google.genai import types


SYSTEM_INSTRUCTION = """당신은 창작자를 돕는 캐릭터 설정 작가입니다.
사용자는 이름/성별/나이/종족/종교/장르/키워드/추가 정보 중 원하는 항목만 채워서 보냅니다.
비어 있는 항목은 이미 채워진 다른 항목들과 어울리도록 당신이 자유롭게 창작해서 채우세요.
"추가 정보"에는 세계관 설정이나 캐릭터의 특징, 사연이 자유 서술 형태로 들어올 수 있습니다.
이 내용이 있다면 반드시 배경 이야기(backstory)와 성격(personality)에 자연스럽게 녹여내세요.
나이는 사용자가 숫자(예: 27)로 줬으면 숫자를 그대로 쓰고, "20대 후반"처럼 애매하게 줬으면 그 표현을 그대로 유지하세요.
사용자가 나이를 비워뒀다면 다른 설정과 어울리는 나이를 숫자 또는 "OO대 초반/중반/후반" 형태로 자유롭게 정하세요.

반드시 아래 JSON 형식으로만 응답하세요. 다른 설명이나 코드블록 표시(```)는 절대 포함하지 마세요.

{
  "name": "캐릭터 이름",
  "gender": "성별",
  "age": "나이 (숫자 또는 '20대 후반' 같은 표현)",
  "species": "종족",
  "religion": "종교 (없다면 '무교' 등으로)",
  "genre": "장르/분위기",
  "personality": "성격 요약 (2~3문장)",
  "speech_style": "말투를 보여주는 예시 대사 1~2개",
  "backstory": "짧은 배경 이야기 (3~5문장)",
  "strengths": "강점 (1~2문장)",
  "weaknesses": "약점 (1~2문장)",
  "likes": "좋아하는 것 (짧게)",
  "dislikes": "싫어하는 것 (짧게)"
}
"""


def build_user_prompt(fields):
    lines = []
    labels = {
        "name": "이름",
        "gender": "성별",
        "age": "나이",
        "species": "종족",
        "religion": "종교",
        "genre": "장르/분위기",
        "keywords": "핵심 키워드",
        "extra_info": "추가 정보 (세계관/특징/사연)",
    }
    for key, label in labels.items():
        value = fields.get(key)
        if value:
            lines.append(f"{label}: {value}")
        else:
            lines.append(f"{label}: (비워둠 - AI가 자유롭게 정해주세요)")

    return (
        "\n".join(lines)
        + "\n\n위 정보를 바탕으로 캐릭터 설정을 JSON으로 작성해주세요."
    )


def call_gemini(fields):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("서버에 AI API 키가 설정되어 있지 않습니다.")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=build_user_prompt(fields),
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

            fields = {
                "name": (payload.get("name") or "").strip(),
                "gender": (payload.get("gender") or "").strip(),
                "age": (payload.get("age") or "").strip(),
                "species": (payload.get("species") or "").strip(),
                "religion": (payload.get("religion") or "").strip(),
                "genre": (payload.get("genre") or "").strip(),
                "keywords": (payload.get("keywords") or "").strip(),
                "extra_info": (payload.get("extra_info") or "").strip(),
            }

            if not any(fields.values()):
                self._send_json(400, {
                    "success": False,
                    "error": "입력 내용을 확인해주세요. 최소 1개 이상의 항목을 입력해주세요.",
                })
                return

            result = call_gemini(fields)
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