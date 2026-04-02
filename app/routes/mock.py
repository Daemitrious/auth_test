from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import User
from ..permissions import check_permission
from ..schemas import MockObjectOut

router = APIRouter(prefix="/mock", tags=["mock resources"])

DOCUMENTS = [
    {"id": 1, "owner_id": 1, "title": "Admin strategy"},
    {"id": 2, "owner_id": 2, "title": "Manager plan"},
    {"id": 3, "owner_id": 3, "title": "User note"},
]


@router.get("/documents", response_model=list[MockObjectOut])
def list_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_permission(db, current_user, "documents", "read")
    visible = []
    for item in DOCUMENTS:
        try:
            check_permission(db, current_user, "documents", "read", owner_id=item["owner_id"])
            visible.append(item)
        except Exception:
            continue
    return visible


@router.get("/documents/{doc_id}", response_model=MockObjectOut)
def get_document(doc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = next((x for x in DOCUMENTS if x["id"] == doc_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Document not found")
    check_permission(db, current_user, "documents", "read", owner_id=item["owner_id"])
    return item


@router.post("/documents", response_model=MockObjectOut, status_code=201)
def create_document(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    check_permission(db, current_user, "documents", "create")
    new_id = max(item["id"] for item in DOCUMENTS) + 1
    item = {"id": new_id, "owner_id": current_user.id, "title": f"Document #{new_id}"}
    DOCUMENTS.append(item)
    return item


@router.patch("/documents/{doc_id}", response_model=MockObjectOut)
def update_document(doc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = next((x for x in DOCUMENTS if x["id"] == doc_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Document not found")
    check_permission(db, current_user, "documents", "update", owner_id=item["owner_id"])
    item["title"] = item["title"] + " (updated)"
    return item


@router.delete("/documents/{doc_id}", status_code=204)
def delete_document(doc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = next((x for x in DOCUMENTS if x["id"] == doc_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Document not found")
    check_permission(db, current_user, "documents", "delete", owner_id=item["owner_id"])
    DOCUMENTS.remove(item)
