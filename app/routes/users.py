from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas import UserCreate, UserOut, Token, PhotoChangeOut, UserInfo
from app.database import db
from app.utils import hash_password, verify_password
from app.auth import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import UploadFile, File
from app.dependencies import get_current_user
from app.cloudinary_utils import cloudinary
from bson import ObjectId

router = APIRouter(prefix="/users", tags=["Users", "Authentication"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    # Check if email already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password before saving
    hashed_pw = hash_password(user.password)

    user_doc = {
        "name": user.fullName,
        "email": user.email,
        "password": hashed_pw,
        "postCount": 0,
        "changePerMonth": 0,
        "photo": (
            user.photo
            if user.photo
            else "https://res.cloudinary.com/dlovcfdar/image/upload/w_100/v1752399063/p3img_r9qqsr.jpg"
        ),
    }

    result = await db.users.insert_one(user_doc)

    return {
        "id": str(result.inserted_id),
        "email": user.email,
        "photo": user_doc["photo"],
    }


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_photo = user.get("photo", "")
    token = create_access_token(data={"sub": user["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_photo": user_photo,
        "user_id": str(user["_id"]),
    }


@router.post("/change-photo", response_model=PhotoChangeOut)
async def change_photo(
    photo: UploadFile = File(...), current_user: dict = Depends(get_current_user)
):
    user = await db.users.find_one({"email": current_user["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user["changePerMonth"] >= 5:
        return {"result": "limit_reached", "other": None, "success": False}
    try:
        result = cloudinary.uploader.upload(photo.file, folder="profilePhoto")
        result["secure_url"] = result["secure_url"].replace("upload/", "upload/w_100/")
        await db.users.update_one(
            {"email": current_user["email"]}, {"$set": {"photo": result["secure_url"]}}
        )
        await db.users.update_one(
            {"email": current_user["email"]}, {"$inc": {"changePerMonth": 1}}
        )
        print(result["secure_url"])
        return {
            "result": "success",
            "other": {
                "id": str(user["_id"]),
                "email": user["email"],
                "photo": result["secure_url"],
            },
            "success": True,
        }
    except Exception as e:
        return {"result": "error", "other": None, "success": False}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Returns the current user's info if the token is valid.
    """
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "photo": current_user.get("photo", ""),
    }


@router.get("/{user_id}", response_model=UserInfo)
async def get_user_by_id(user_id: str):
    """
    Returns user information by user_id.
    """
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": str(user["_id"]),
            "name": user.get("name", "Unknown User"),
            "email": user["email"],
            "photo": user.get("photo", ""),
        }
    except Exception as e:
        if "invalid ObjectId" in str(e):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        raise HTTPException(status_code=500, detail="Internal server error")
