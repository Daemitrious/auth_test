from sqlalchemy.orm import Session

from .models import AccessRule, Resource, Role, User, UserRole
from .security import hash_password


RESOURCES = [
    ("users", "Users"),
    ("profiles", "Profiles"),
    ("documents", "Documents"),
    ("rules", "Access rules"),
]

ROLES = [
    ("admin", "Administrator"),
    ("manager", "Manager"),
    ("user", "User"),
]

USERS = [
    {
        "last_name": "Adminov",
        "first_name": "Admin",
        "middle_name": None,
        "email": "admin@example.com",
        "password": "Admin123!",
        "role": "admin",
    },
    {
        "last_name": "Managerov",
        "first_name": "Manager",
        "middle_name": None,
        "email": "manager@example.com",
        "password": "Manager123!",
        "role": "manager",
    },
    {
        "last_name": "Userov",
        "first_name": "User",
        "middle_name": None,
        "email": "user@example.com",
        "password": "User12345!",
        "role": "user",
    },
]

RULES = {
    "admin": {
        "users": dict(can_read=True, can_read_all=True, can_create=True, can_update=True, can_update_all=True, can_delete=True, can_delete_all=True),
        "profiles": dict(can_read=True, can_read_all=True, can_create=False, can_update=True, can_update_all=True, can_delete=False, can_delete_all=False),
        "documents": dict(can_read=True, can_read_all=True, can_create=True, can_update=True, can_update_all=True, can_delete=True, can_delete_all=True),
        "rules": dict(can_read=True, can_read_all=True, can_create=True, can_update=True, can_update_all=True, can_delete=False, can_delete_all=False),
    },
    "manager": {
        "users": dict(can_read=False, can_read_all=False, can_create=False, can_update=False, can_update_all=False, can_delete=False, can_delete_all=False),
        "profiles": dict(can_read=True, can_read_all=False, can_create=False, can_update=True, can_update_all=False, can_delete=False, can_delete_all=False),
        "documents": dict(can_read=True, can_read_all=True, can_create=True, can_update=True, can_update_all=True, can_delete=False, can_delete_all=False),
        "rules": dict(can_read=False, can_read_all=False, can_create=False, can_update=False, can_update_all=False, can_delete=False, can_delete_all=False),
    },
    "user": {
        "users": dict(can_read=False, can_read_all=False, can_create=False, can_update=False, can_update_all=False, can_delete=False, can_delete_all=False),
        "profiles": dict(can_read=True, can_read_all=False, can_create=False, can_update=True, can_update_all=False, can_delete=False, can_delete_all=False),
        "documents": dict(can_read=True, can_read_all=False, can_create=True, can_update=True, can_update_all=False, can_delete=True, can_delete_all=False),
        "rules": dict(can_read=False, can_read_all=False, can_create=False, can_update=False, can_update_all=False, can_delete=False, can_delete_all=False),
    },
}


def seed_data(db: Session) -> None:
    if db.query(Role).first():
        return

    resources = {}
    for code, name in RESOURCES:
        resource = Resource(code=code, name=name)
        db.add(resource)
        db.flush()
        resources[code] = resource

    roles = {}
    for code, name in ROLES:
        role = Role(code=code, name=name)
        db.add(role)
        db.flush()
        roles[code] = role

    for role_code, resource_rules in RULES.items():
        for resource_code, flags in resource_rules.items():
            db.add(AccessRule(role_id=roles[role_code].id, resource_id=resources[resource_code].id, **flags))

    for item in USERS:
        user = User(
            last_name=item["last_name"],
            first_name=item["first_name"],
            middle_name=item["middle_name"],
            email=item["email"],
            password_hash=hash_password(item["password"]),
            is_active=True,
        )
        db.add(user)
        db.flush()
        db.add(UserRole(user_id=user.id, role_id=roles[item["role"]].id))

    db.commit()
