from datetime import datetime
from pydantic import BaseModel, Field
from pydantic.networks import EmailStr
from typing import Optional, Literal, List


class User(BaseModel):
    email: EmailStr
    password: str


class UserCreate(User):
    fullName: str
    photo: Optional[str] = Field(
        default="https://res.cloudinary.com/dlovcfdar/image/upload/w_100/v1752399063/p3img_r9qqsr.jpg",
        description="Profile photo of the post's owner",
    )
    changePerMonth: Optional[int] = Field(
        default=0, description="Number of changes per month"
    )
    postCount: Optional[int] = Field(
        default=0, description="Number of posts"
    )


class UserLogin(User):
    pass


class UserOut(BaseModel):
    id: str
    email: EmailStr
    photo: Optional[str] = Field(
        default="",
        description="Profile photo of the post's owner",
    )


class UserInfo(BaseModel):
    id: str
    name: str
    email: EmailStr
    photo: Optional[str] = Field(
        default="",
        description="Profile photo of the user",
    )

class PhotoChangeOut(BaseModel):
    result : Literal['success', 'error', 'limit_reached']
    other: Optional[UserOut]
    success: Optional[bool]

class Token(BaseModel):
    access_token: str
    token_type: str
    user_photo: str
    user_id: str


class PostBase(BaseModel):
    title: str
    category: str
    mainImage: Optional[str]
    content: str
    summary: str


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: str
    date: datetime
    owner_id: str
    readTime: str
    summary: str
    likes: Optional[int] = Field(default=0, description="Number of likes")
    whoLiked: Optional[List[str]] = Field(default=[], description="List of user IDs who liked the post")


class PostOut(BaseModel):
    id: str
    title: str
    content: str
    owner_id: str


class PostWithUser(PostResponse):
    owner_name: str
    owner_photo: Optional[str] = Field(
        default="https://res.cloudinary.com/dlovcfdar/image/upload/w_100/v1752399063/p3img_r9qqsr.jpg",
        description="Profile photo of the post's owner",
    )


# Alias for backward compatibility
Post = PostWithUser
