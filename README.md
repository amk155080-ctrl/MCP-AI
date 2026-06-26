# MCP 4.0 v1

한국 반도체·AI 중심 투자 의사결정 플랫폼 v1 골격입니다.

## 설치

```bash
cd mcp4_v1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env`에 DB 정보와 KRX_API_KEY를 입력하세요.

## DB 생성

```bash
psql -U postgres -d mcp4 -f sql/01_schema.sql
```

## 수집 / 점수계산

```bash
python -m app.batch.daily_collect --date 20250612
python -m app.batch.daily_score --date 20250612
```

## API 실행

```bash
uvicorn app.main:app --reload
```

API 문서:
http://127.0.0.1:8000/docs
