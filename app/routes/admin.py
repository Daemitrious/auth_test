from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_admin
from ..models import AccessRule
from ..schemas import RuleOut, RuleUpdateIn

router = APIRouter(prefix="/admin", tags=["admin"])



def to_rule_out(rule: AccessRule) -> RuleOut:
    return RuleOut(
        id=rule.id,
        role=rule.role.code,
        resource=rule.resource.code,
        can_read=rule.can_read,
        can_read_all=rule.can_read_all,
        can_create=rule.can_create,
        can_update=rule.can_update,
        can_update_all=rule.can_update_all,
        can_delete=rule.can_delete,
        can_delete_all=rule.can_delete_all,
    )


@router.get("/rules", response_model=list[RuleOut])
def list_rules(_: object = Depends(require_admin), db: Session = Depends(get_db)):
    return [to_rule_out(rule) for rule in db.query(AccessRule).all()]


@router.patch("/rules/{rule_id}", response_model=RuleOut)
def update_rule(rule_id: int, payload: RuleUpdateIn, _: object = Depends(require_admin), db: Session = Depends(get_db)):
    rule = db.query(AccessRule).filter(AccessRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for key, value in payload.model_dump().items():
        setattr(rule, key, value)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return to_rule_out(rule)
