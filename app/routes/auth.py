from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Session as UserSession, User, UserRole, Role
from ..schemas import AuthOut, LoginIn, ProfileUpdateIn, RegisterIn, UserOut
from ..security import generate_session_token, hash_password, session_expiry, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])



def to_user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        last_name=user.last_name,
        first_name=user.first_name,
        middle_name=user.middle_name,
        email=user.email,
        is_active=user.is_active,
        roles=[role.code for role in user.roles],
    )


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if payload.password != payload.password_repeat:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        last_name=payload.last_name,
        first_name=payload.first_name,
        middle_name=payload.middle_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        is_active=True,
    )
    db.add(user)
    db.flush()

    default_role = db.query(Role).filter(Role.code == "user").first()
    db.add(UserRole(user_id=user.id, role_id=default_role.id))
    db.commit()
    db.refresh(user)
    return to_user_out(user)


@router.post("/login", response_model=AuthOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    token = generate_session_token()
    db.add(UserSession(token=token, user_id=user.id, expires_at=session_expiry(), is_active=True))
    db.commit()
    db.refresh(user)
    return AuthOut(access_token=token, user=to_user_out(user))


@router.post("/logout", status_code=204)
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    token = authorization.split(" ", 1)[1]
    session = db.query(UserSession).filter(UserSession.token == token, UserSession.user_id == current_user.id, UserSession.is_active.is_(True)).first()
    if session:
        session.is_active = False
        db.commit()


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return to_user_out(current_user)


@router.patch("/me", response_model=UserOut)
def update_profile(payload: ProfileUpdateIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(current_user, key, value)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return to_user_out(current_user)


@router.delete("/me", status_code=204)
def delete_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    current_user.is_active = False
    db.add(current_user)
    token = authorization.split(" ", 1)[1]
    db.query(UserSession).filter(UserSession.user_id == current_user.id, UserSession.token == token).update({"is_active": False})
    db.commit()
