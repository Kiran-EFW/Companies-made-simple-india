from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.user import User
from src.schemas.auth import UserCreate, UserLogin, UserOut, UserUpdate, PasswordChange, Token
from src.utils.security import get_password_hash, verify_password, create_access_token, get_current_user
from src.utils.validators import validate_phone
from src.services.email_service import email_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        phone=user_data.phone,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send welcome email
    email_service.send_welcome_email(
        user_name=new_user.full_name,
        user_email=new_user.email,
    )

    # Generate token
    access_token = create_access_token(data={"sub": str(new_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/profile", response_model=UserOut)
def update_profile(
    updates: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if updates.phone is not None and not validate_phone(updates.phone):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid Indian phone number",
        )
    if updates.full_name is not None:
        current_user.full_name = updates.full_name
    if updates.phone is not None:
        current_user.phone = updates.phone
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/password")
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}
