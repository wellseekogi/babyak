from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from typing import List

# 1. Firebase 초기화
# 이미 초기화되어 있는지 확인 (FastAPI 재실행 시 에러 방지)
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

# 2. DB 클라이언트 (Firestore)
db = firestore.client()

app = FastAPI()

# --- 데이터 모델 (Schema) ---
class BobYakCreate(BaseModel):
    title: str      # 제목 (예: 오늘 학식 드실 분)
    menu: str       # 메뉴
    location: str   # 장소
    author: str     # 작성자 (나중에 로그인 연동하면 자동화 가능)

class BobYakResponse(BobYakCreate):
    id: str         # DB에 저장된 문서 ID

# --- API 엔드포인트 ---

@app.get("/")
def read_root():
    return {"message": "Firebase와 연결된 밥약 서버 ON!"}

# 1. 밥약 글 쓰기
@app.post("/bobyak", response_model=dict)
def create_bobyak(item: BobYakCreate):
    # 'bobyaks'라는 컬렉션(폴더)에 데이터 저장
    # add()를 쓰면 ID가 자동으로 생성됩니다.
    doc_ref = db.collection("bobyaks").document()
    doc_ref.set(item.dict())
    
    return {"id": doc_ref.id, "message": "성공적으로 저장되었습니다."}

# 2. 밥약 글 전체 조회
@app.get("/bobyak", response_model=List[BobYakResponse])
def get_bobyaks():
    docs = db.collection("bobyaks").stream()
    
    bobyak_list = []
    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id  # 문서 ID도 같이 보내줌
        bobyak_list.append(data)
        
    return bobyak_list