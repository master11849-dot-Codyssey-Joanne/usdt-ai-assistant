import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

# 1. 환경 변수 및 Firebase 초기화
load_dotenv()
firebase_key_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_key_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. 지난번에 분석했던 CSV 파일 읽기
csv_file = "usdt_krw_analyzed.csv"
if not os.path.exists(csv_file):
    print(f"❌ {csv_file} 파일이 없습니다. 경로를 확인해주세요.")
    exit()

df = pd.read_csv(csv_file)
print(f"📊 총 {len(df)}개의 시계열 데이터를 Firebase로 업로드합니다...")

# 3. 데이터베이스에 일괄 추가 (Batch Write 활용)
batch = db.batch()
collection_ref = db.collection("data")

count = 0
for idx, row in df.iterrows():
    # 날짜(datetime)와 종가(close), 그리고 보조지표 요약값을 memo로 구성
    date_str = str(row['datetime'])
    close_price = float(row['close'])
    memo_str = f"괴리율:{row['premium_pct']:.2f}%, MACD_Hist:{row['macd_hist']:.2f}"
    
    doc_ref = collection_ref.document()
    batch.set(doc_ref, {
        "date": date_str,
        "value": close_price,
        "memo": memo_str
    })
    count += 1

    # Firestore 배치 제한(500개)에 맞추기 위해 400개 단위로 커밋
    if count % 400 == 0:
        batch.commit()
        batch = db.batch()

# 남은 데이터 커밋
batch.commit()
print(f"✅ 성공적으로 {count}개의 시계열 데이터가 Firebase에 업로드되었습니다!")