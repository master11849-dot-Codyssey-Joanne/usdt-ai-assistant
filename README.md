# 🤖 USDT AI 트레이딩 비서 (USDT AI Trading Assistant)

> 실시간 USDT/KRW 시계열 데이터 관리와 AI 기반 맞춤형 트레이딩 인사이트를 제공하는 지능형 웹 어시스턴트 서비스입니다.

---

## 📌 1. 서비스 소개 (무엇을 해결하는지)
암호화폐 시장 및 환율(USDT/KRW) 변동성에 대응하는 트레이더와 분석가들은 방대한 시계열 데이터를 실시간으로 모니터링하고 빠르게 해석해야 하는 어려움을 겪습니다. 
* **문제 해결:** 본 서비스는 사용자가 입력하거나 마이그레이션한 시계열 데이터를 **Firebase Firestore**에 안전하게 저장하고, **FastAPI 백엔드**를 통해 통계 지표(총합, 평균, 최댓값, 최솟값, 트렌드)를 자동으로 산출합니다.
* **AI 인사이트:** 산출된 데이터 맥락을 **OpenAI GPT-4o-mini** 모델의 시스템 프롬프트에 실시간으로 주입(`Context Injection`)하여, 사용자가 트레이딩 상황과 데이터 상태에 대해 자연어로 질문했을 때 수치 기반의 정확하고 전문적인 맞춤형 답변을 즉시 제공합니다.

---

## 🛠️ 2. 기술 스택

### **Backend**
* **Language:** Python 3.14
* **Framework:** FastAPI, Uvicorn
* **Database & BaaS:** Firebase Firestore
* **AI Integration:** OpenAI API (`gpt-4o-mini`)
* **Environment Config:** Python-dotenv, Requests, Pydantic

### **Frontend**
* **UI Structure:** HTML5, Modern CSS, JavaScript (Vanilla JS)
* **Design Concept:** Apple-inspired clean light-mode dashboard interface with responsive card layouts

### **Deployment & Cloud**
* **Backend Hosting:** Render (Cloud Web Service)
* **Frontend Hosting:** Vercel (Static Web Deployment)
* **Version Control:** Git & GitHub

---

## 🌐 3. 배포 URL
* **프론트엔드 웹 서비스 (Vercel):** `https://usdt-ai-assistant.vercel.app/`
* **백엔드 API 서버 (Render):** `https://usdt-ai-assistant-1.onrender.com`
* **API 문서 (Swagger UI):** `https://usdt-ai-assistant-1.onrender.com/docs`

---

## 💻 4. 로컬 실행 방법

프로젝트를 로컬 환경에서 직접 실행하여 테스트하는 방법입니다.

### **1. 저장소 클론 및 이동**
```bash
git clone [https://github.com/master11849-dot-Codyssey-Joanne/usdt-ai-assistant.git](https://github.com/master11849-dot-Codyssey-Joanne/usdt-ai-assistant.git)
cd usdt-ai-assistant

### **2. 가상환경 생성 및 활성화**
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

### **3. 라이브러리 설치**
pip install -r requirements.txt

### **4. 환경 변수 설정 (.env 파일 생성)**
프로젝트 루트 폴더에 .env 파일을 만들고 아래 내용을 입력합니다.
OPENAI_API_KEY=sk-your_openai_api_key_here
FIREBASE_SERVICE_ACCOUNT_JSON=firebase_key.json
(루트 폴더에 Firebase 서비스 계정 파일인 firebase_key.json을 위치시켜야 합니다)

### **5. 백엔드 서버 실행**
uvicorn main:app --reload --port 8000
브라우저에서 http://127.0.0.1:8000/docs에 접속하여 API 정상 동작을 확인할 수 있습니다.

## 💻 5. 환경 변수 목록 (최소 세트)

프로젝트를 로컬 환경에서 직접 실행하여 테스트하는 방법입니다.

클라우드 배포(Render) 및 로컬 실행 시 반드시 설정해야 하는 필수 환경 변수입니다.
변수명                             설명                                            예시 / 비고
OPENAI_API_KEY                   OpenAI API 연동을 위한 시크릿 키                  sk-Proj-...
FIREBASE_SERVICE_ACCOUNT_JSON    Firebase 관리자 인증 JSON 전문 (또는 파일 경로)    { "type": "service_account", ... }
