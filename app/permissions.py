from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .models import AccessRule, Resource, User


ACTION_TO_FLAGS = {
    "read": ("can_read", "can_read_all"),
    "create": ("can_create", None),
    "update": ("can_update", "can_update_all"),
    "delete": ("can_delete", "can_delete_all"),
}



def check_permission(
    db: Session,
    user: User,
    resource_code: str,
    action: str,
    owner_id: int | None = None,
) -> None:
    resource = db.query(Resource).filter(Resource.code == resource_code).first()
    if not resource:
        raise HTTPException(status_code=500, detail="Unknown resource")

    role_ids = [role.id for role in user.roles]
    rules = db.query(AccessRule).filter(AccessRule.role_id.in_(role_ids), AccessRule.resource_id == resource.id).all()

    own_flag, all_flag = ACTION_TO_FLAGS[action]
    can_own = any(getattr(rule, own_flag) for rule in rules)
    can_all = any(getattr(rule, all_flag) for rule in rules if all_flag)

    if can_all:
        return
    if action == "create" and can_own:
        return
    if owner_id is not None and owner_id == user.id and can_own:
        return

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
