import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import OrganizationProgram, StrategyProfile, CreatedResponse

app = FastAPI(title="GrowthSphere API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "GrowthSphere backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else ("✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set")
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# -----------------------------
# Helpers
# -----------------------------
class ObjectIdStr(BaseModel):
    id: str


def _ensure_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")


# -----------------------------
# Organization Program Endpoints
# -----------------------------
@app.post("/api/programs", response_model=CreatedResponse)
def create_program(program: OrganizationProgram):
    new_id = create_document("organizationprogram", program)
    return {"id": new_id}


@app.get("/api/programs")
def list_programs(limit: Optional[int] = 50):
    docs = get_documents("organizationprogram", {}, limit)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return {"items": docs}


@app.get("/api/programs/{program_id}")
def get_program(program_id: str):
    oid = _ensure_object_id(program_id)
    doc = db["organizationprogram"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Program not found")
    doc["id"] = str(doc.pop("_id"))
    return doc


# -----------------------------
# Strategy Profiles Endpoints
# -----------------------------
@app.post("/api/strategies", response_model=CreatedResponse)
def create_strategy(strategy: StrategyProfile):
    # Basic existence check for parent program
    _ = get_program(strategy.program_id)
    new_id = create_document("strategyprofile", strategy)
    return {"id": new_id}


@app.get("/api/strategies")
def list_strategies(program_id: Optional[str] = None, limit: Optional[int] = 50):
    query = {"program_id": program_id} if program_id else {}
    docs = get_documents("strategyprofile", query, limit)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return {"items": docs}
