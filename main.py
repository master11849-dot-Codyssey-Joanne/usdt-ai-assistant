import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI


# 1. 환경 변수 로드 (.env 파일에서 API 키와 파일 경로를 읽어옵니다)
load_dotenv()

# 2. FastAPI 앱 생성 및 이름 설정
app = FastAPI(
    title="USDT AI Trading Assistant API",
    description="내 상황을 아는 AI 비서 백엔드 서버입니다."
)

# CORS 설정: 프론트엔드(웹 화면)에서 이 서버로 요청을 보낼 수 있도록 허용합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 나중에 실제 배포 시에는 Vercel 도메인으로 제한하는 것이 안전합니다.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Firebase Firestore 연동
firebase_key_env = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

# Firebase가 중복으로 실행되지 않도록 체크한 뒤 초기화합니다.
if not firebase_admin._apps:
    try:
        # 환경 변수 값이 JSON 텍스트 문자열인 경우 (Render 클라우드 환경)
        if firebase_key_env and firebase_key_env.strip().startswith("{"):
            cred_dict = json.loads(firebase_key_env)
            cred = credentials.Certificate(cred_dict)
        else:
            # 환경 변수 값이 파일 경로이거나 없는 경우 (로컬 컴퓨터 환경)
            key_path = firebase_key_env or "firebase_key.json"
            cred = credentials.Certificate(key_path)
            
        firebase_admin.initialize_app(cred)
        print("✅ Firebase 연동 성공!")
    except Exception as e:
        print(f"❌ Firebase 연동 실패: {e}")

# 데이터베이스(Firestore)를 제어할 수 있는 객체를 만듭니다.
db = firestore.client()

# 4. 서버 동작 확인용 엔드포인트 (API 주소)
@app.get("/")
def read_root():
    return {"message": "🚀 AI 트레이딩 비서 서버가 정상적으로 작동 중입니다!"}

# --- 데이터 모델(Schema) 정의 ---
class TimeSeriesData(BaseModel):
    date: str
    value: float
    memo: Optional[str] = None

class TimeSeriesDataUpdate(BaseModel):
    value: Optional[float] = None
    memo: Optional[str] = None

# --- 1. 데이터 추가 (POST) ---
@app.post("/api/data")
def add_data(data: TimeSeriesData):
    doc_ref = db.collection("data").document() # 새 문서(ID 자동생성)
    doc_ref.set(data.dict())
    return {"id": doc_ref.id, "message": "데이터가 성공적으로 추가되었습니다."}

# --- 2. 데이터 목록 조회 (GET) ---
@app.get("/api/data")
def get_data():
    docs = db.collection("data").stream()
    result = []
    for doc in docs:
        item = doc.to_dict()
        item['id'] = doc.id
        result.append(item)
    return result

# --- 3. 데이터 수정 (PUT) ---
@app.put("/api/data/{id}")
def update_data(id: str, data: TimeSeriesDataUpdate):
    doc_ref = db.collection("data").document(id)
    # 입력된 값(None이 아닌 값)만 필터링해서 업데이트
    update_dict = {k: v for k, v in data.dict().items() if v is not None}
    doc_ref.update(update_dict)
    return {"message": "데이터가 수정되었습니다."}

# --- 4. 데이터 삭제 (DELETE) ---
@app.delete("/api/data/{id}")
def delete_data(id: str):
    db.collection("data").document(id).delete()
    return {"message": "데이터가 삭제되었습니다."}

# --- 5. 데이터 요약 (GET - AI 프롬프트 주입용) ---
@app.get("/api/data/summary")
def get_summary():
    docs = db.collection("data").stream()
    data_list = [doc.to_dict() for doc in docs]
    
    if not data_list:
        return {"period": "데이터 없음", "count": 0, "metrics": {}, "trend": "알 수 없음"}
        
    values = [d.get("value", 0) for d in data_list]
    dates = [d.get("date", "") for d in data_list]
    
    count = len(values)
    metrics = {
        "total": sum(values),
        "average": round(sum(values) / count, 2) if count > 0 else 0,
        "max": max(values),
        "min": min(values)
    }
    
    period = f"{min(dates)} ~ {max(dates)}" if dates else "기간 미상"
    
    # 단순 트렌드 계산 (처음과 끝 비교)
    trend = "유지"
    if count >= 2:
        if values[-1] > values[0]: trend = "상승 추세"
        elif values[-1] < values[0]: trend = "하락 추세"
        
    return {
        "period": period,
        "count": count,
        "metrics": metrics,
        "trend": trend
    }

# --- OpenAI 클라이언트 초기화 (.env 파일의 OPENAI_API_KEY 자동 인식)
client = OpenAI()

# --- 데이터 모델 추가 (대화 저장 및 채팅용)
class ConversationSave(BaseModel):
    title: str
    messages: list

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


# --- 1. 대화 기록 저장 (POST) ---
@app.post("/api/conversations")
def save_conversation(conv: ConversationSave):
    doc_ref = db.collection("conversations").document()
    doc_ref.set(conv.dict())
    return {"id": doc_ref.id, "message": "대화가 저장되었습니다."}


# --- 2. 대화 기록 목록 조회 (GET) ---
@app.get("/api/conversations")
def get_conversations():
    docs = db.collection("conversations").stream()
    result = []
    for doc in docs:
        item = doc.to_dict()
        item['id'] = doc.id
        # 목록에서는 속도를 위해 무거운 messages 내용은 제외하고 ID와 제목만 반환할 수도 있습니다.
        result.append({"id": item['id'], "title": item.get('title', '제목 없음')})
    return result


# --- 3. 특정 대화 불러오기 (GET) ---
@app.get("/api/conversations/{id}")
def get_conversation_detail(id: str):
    doc = db.collection("conversations").document(id).get()
    if not doc.exists:
        return {"error": "해당 대화를 찾을 수 없습니다."}, 404
    return doc.to_dict()


# --- 4. 대화 삭제 (DELETE) ---
@app.delete("/api/conversations/{id}")
def delete_conversation(id: str):
    db.collection("conversations").document(id).delete()
    return {"message": "대화가 삭제되었습니다."}


# --- 5. AI 챗봇 API (핵심: 컨텍스트 주입 및 자동 저장) ---
@app.post("/api/chat")
def chat_with_ai(chat_req: ChatRequest):
    # (1) 데이터 요약 정보 가져오기 (/api/data/summary 내부 로직 활용)
    summary_data = get_summary()
    
    # (2) AI에게 부여할 시스템 프롬프트(성격 및 데이터 맥락) 구성
    system_prompt = f"""
당신은 데이터 분석 비서입니다. 
[사용자 데이터 요약]
- 데이터 기간: {summary_data.get('period')}
- 총 레코드: {summary_data.get('count')}개
- 주요 지표(총합/평균/최대/최소): {summary_data.get('metrics')}
- 최근 트렌드: {summary_data.get('trend')}

위 데이터를 기반으로 사용자의 질문에 맞춤형 답변을 제공하세요. 수치에 기반하여 정확하고 친절하게 답변해야 합니다.
"""

    try:
        # (3) OpenAI 최신 모델 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini", # 빠르고 경제적인 최신 모델 사용
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chat_req.message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        ai_reply = response.choices[0].message.content
        
        # (4) 대화 내용을 자동으로 Firebase 'conversations'에 저장
        chat_history = [
            {"role": "user", "content": chat_req.message},
            {"role": "assistant", "content": ai_reply}
        ]
        
        # 제목은 첫 번째 질문의 앞부분 15글자로 자동 생성
        title_text = chat_req.message[:15] + ("..." if len(chat_req.message) > 15 else "")
        
        db.collection("conversations").add({
            "title": title_text,
            "messages": chat_history
        })

        return {
            "reply": ai_reply,
            "summary_used": summary_data
        }

    except Exception as e:
        return {"error": str(e)}, 500

    