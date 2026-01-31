from fastapi import APIRouter
from app.db.firebase_client import db
from datetime import datetime

router = APIRouter(prefix="/firebase-test", tags=["firebase"])

@router.get("/ping")
def firebase_ping():
    # write test doc
    ref = db.collection("connection_tests").add({
        "status": "connected",
        "time": datetime.utcnow().isoformat()
    })

    # read back count
    docs = list(db.collection("connection_tests").stream())

    return {
        "write_id": ref[1].id,
        "total_docs": len(docs)
    }
