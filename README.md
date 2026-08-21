# 캐릭토 (Chartcoto)

키워드 몇 개만 입력하면 AI가 이름ㆍ성격ㆍ말투ㆍ배경 스토리까지 갖춘 캐릭터 설정을 만들어주는 캐릭터 생성 서비스입니다.

## 서비스 소개

- **서비스 이름**: 캐릭토
- **서비스 목적**: 웹소설/웹툰/TRPG/게임 기획을 위한 캐릭터를 만들 때 가장 막막한 "내면 설정"(성격, 말투, 배경 이야기)을 AI가 초안으로 채워주어 창작의 첫 문턱을 낮춥니다.
- **주요 기능**
  - 이름(선택)ㆍ장르ㆍ키워드를 입력하면 AI가 캐릭터 설정을 생성
  - 마음에 들지 않으면 재생성
  - 완성된 캐릭터를 보관함에 저장하고 목록으로 다시 확인

## 기술 스택

- Frontend: HTML / CSS / JavaScript (프레임워크 미사용)
- Backend: Vercel Serverless Functions (Python)
- AI: Gemini API (`google-genai`)
- Database: Vercel Postgres

## 프로젝트 구조

```text
character-maker/
├── index.html              # 홈
├── create.html              # 캐릭터 만들기 (AI 기능 페이지)
├── gallery.html              # 내 캐릭터 보관함
├── about.html               # 서비스 소개 & 가이드
│
├── css/
│   └── style.css            # 전체 반응형 스타일
│
├── js/
│   ├── main.js               # 공통 네비게이션(모바일 메뉴)
│   ├── create.js             # 입력 검증, AI 호출, 로딩/오류 처리, 저장
│   └── gallery.js            # 보관함 목록 조회 및 렌더링
│
├── api/
│   ├── generate-character.py # Gemini 호출 → 캐릭터 생성
│   ├── save-character.py     # Postgres에 캐릭터 저장
│   └── get-characters.py     # Postgres에서 캐릭터 목록 조회
│
├── requirements.txt          # Python 의존 패키지
├── vercel.json                # Vercel 배포 설정 (Python 런타임)
├── .gitignore
└── README.md
```

## 실행 방법 (로컬)

이 프로젝트는 Vercel Serverless Functions를 사용하므로, 로컬에서 API까지 함께 테스트하려면 [Vercel CLI](https://vercel.com/docs/cli)를 사용하는 것을 권장합니다.

```bash
npm install -g vercel
cd character-maker
vercel dev
```

`vercel dev`를 실행하면 정적 파일과 `api/` 폴더의 Python 함수가 함께 로컬 서버(기본 `http://localhost:3000`)에서 동작합니다.

## 환경 변수 설정

프로젝트 루트에 `.env` 파일을 만들거나 Vercel 프로젝트 설정의 Environment Variables에 아래 값을 등록해야 합니다. **실제 키 값은 절대 GitHub에 커밋하지 마세요.**

```text
GEMINI_API_KEY=your_api_key_here
STORAGE_URL=your_vercel_postgres_connection_string_here
```

- `GEMINI_API_KEY`: Google AI Studio에서 발급받은 Gemini API 키
- `STORAGE_URL`: Vercel Postgres(Neon 기반) 생성 후 프로젝트에 연결하면 `.env.local` 탭에서 자동으로 제공되는 연결 문자열

### 데이터베이스 테이블 생성

Vercel Postgres 콘솔의 Query 탭에서 아래 SQL을 한 번 실행해야 합니다.

```sql
CREATE TABLE characters (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    gender TEXT,
    age TEXT,
    species TEXT,
    religion TEXT,
    genre TEXT,
    keywords TEXT,
    extra_info TEXT,
    personality TEXT,
    speech_style TEXT,
    backstory TEXT,
    strengths TEXT,
    weaknesses TEXT,
    likes TEXT,
    dislikes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Vercel 배포 방법

1. GitHub 저장소에 프로젝트를 push합니다.
2. [Vercel](https://vercel.com)에서 New Project로 해당 GitHub 저장소를 연결합니다.
3. 프로젝트 설정의 Environment Variables에 `GEMINI_API_KEY`, `POSTGRES_URL`을 등록합니다. (Postgres는 Vercel Storage 탭에서 먼저 생성 후 프로젝트에 연결하면 `POSTGRES_URL`이 자동 등록됩니다.)
4. Deploy를 실행합니다.
5. 배포가 완료되면 발급된 URL로 접속해 캐릭터 생성 → 저장 → 보관함 조회까지 정상 동작하는지 테스트합니다.

## 배포 URL

```text
배포 URL: (배포 완료 후 여기에 입력)
```