from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.database import db
from app.schemas import PostCreate, PostOut, Post, PostWithUser
from app.dependencies import get_current_user
from bson import ObjectId
from typing import List, Dict, Any
from datetime import datetime
from app.utils import replace_nbsp_in_post

router = APIRouter(prefix="/posts", tags=["Posts"])

categoryDefault = [
    {
        "name": "Business",
        "summary": "Insights into markets, companies, and strategies shaping the global economy.",
        "image": "https://res.cloudinary.com/dlovcfdar/image/upload/v1752399515/business_zzx4wx.jpg",
    },
    {
        "name": "Health",
        "summary": "Tips and information to maintain physical and mental well-being.",
        "image": "https://res.cloudinary.com/dlovcfdar/image/upload/v1752399517/health_f6jysd.jpg",
    },
    {
        "name": "Lifestyle",
        "summary": "Ideas and trends to enhance everyday living and personal style.",
        "image": "https://res.cloudinary.com/dlovcfdar/image/upload/v1752399516/lifestyle_d3ofgl.jpg",
    },
    {
        "name": "Technology",
        "summary": "Updates on innovations, gadgets, and the digital world.",
        "image": "https://res.cloudinary.com/dlovcfdar/image/upload/v1752399518/technology_z3uzsg.jpg",
    },
    {
        "name": "Sports",
        "summary": "News, analysis, and stories from the world of athletics.",
        "image": "https://res.cloudinary.com/dlovcfdar/image/upload/v1753523965/sports_g1v2l6.jpg",
    },
    {
        "name": "Education",
        "summary": "Resources and insights for learning and personal development.",
        "image": "https://res.cloudinary.com/dlovcfdar/image/upload/v1752399516/education_jyfggg.jpg",
    },
    {
        "name": "Food",
        "summary": "Recipes, culinary trends, and everything delicious.",
        "image": "https://res.cloudinary.com/dlovcfdar/image/upload/v1752399518/food1_moanwe.jpg",
    },
    {
        "name": "Entertainment",
        "summary": "Movies, music, TV, and celebrity updates.",
        "image": "https://res.cloudinary.com/dlovcfdar/image/upload/v1753523965/entertainment_tkjypc.jpg",
    },
    {
        "name": "Travel",
        "summary": "Guides and inspiration for exploring new destinations.",
        "image": "https://res.cloudinary.com/dlovcfdar/image/upload/v1752399516/travel_r57pso.jpg",
    },
    {
        "name": "Finance",
        "summary": "Advice and news on money management and investments.",
        "image": "https://res.cloudinary.com/dlovcfdar/image/upload/v1752399516/finance_cvjstx.jpg",
    },
    {
        "name": "Fitness",
        "summary": "Workouts, routines, and tips for a healthier lifestyle.",
        "image": "https://res.cloudinary.com/dlovcfdar/image/upload/v1752399516/fitness_kezxra.jpg",
    },
    {
        "name": "Environment",
        "summary": "Information and actions to protect our planet.",
        "image": "https://res.cloudinary.com/dlovcfdar/image/upload/v1752399516/environment_lvrght.jpg",
    },
    {
        "name": "General",
        "summary": "Miscellaneous topics and general updates.",
        "image": "https://res.cloudinary.com/dlovcfdar/image/upload/v1753523965/general_nzk5kz.jpg",
    },
]


async def get_user_info(user_id: str) -> Dict[str, Any]:
    """Helper function to get user information by user_id"""
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        return {
            "name": user.get("name", "Unknown User"),
            "photo": user.get(
                "photo",
                "https://res.cloudinary.com/dlovcfdar/image/upload/w_100/v1752399063/p3img_r9qqsr.jpg",
            ),
        }
    return {
        "name": "Unknown User",
        "photo": "https://res.cloudinary.com/dlovcfdar/image/upload/w_100/v1752399063/p3img_r9qqsr.jpg",
    }


@router.post("/", response_model=PostWithUser)
async def create_post(post: PostCreate, current_user: dict = Depends(get_current_user)):
    # Check if user's post count is less than 50
    if current_user.get("postCount", 0) >= 50:
        raise HTTPException(
            status_code=400,
            detail="Post limit reached. You can only create up to 50 posts.",
        )

    post_dict = post.dict()
    post_dict = replace_nbsp_in_post(post_dict)
    post_dict["owner_id"] = str(current_user["_id"])
    post_dict["likes"] = 0
    post_dict["whoLiked"] = []
    post_dict["readTime"] = "1 min read"
    post_dict["date"] = datetime.utcnow()

    # Check if mainImage and summary are empty and assign default values
    if not post_dict.get("mainImage"):
        post_dict["mainImage"] = next((item["image"] for item in categoryDefault if item["name"] == post_dict["category"]), None)
    if not post_dict.get("summary"):
        post_dict["summary"] = next((item["summary"] for item in categoryDefault if item["name"] == post_dict["category"]), None)

    result = await db.posts.insert_one(post_dict)

    # Increment user's post count after successful post creation
    await db.users.update_one({"_id": current_user["_id"]}, {"$inc": {"postCount": 1}})

    # Fetch the inserted document and format it for response_model
    created_post = await db.posts.find_one({"_id": result.inserted_id})

    if not created_post:
        raise HTTPException(status_code=500, detail="Post creation failed")

    # Get user information
    user_info = await get_user_info(str(current_user["_id"]))

    created_post["id"] = str(created_post.pop("_id"))
    created_post["owner_name"] = user_info["name"]
    created_post["owner_photo"] = user_info["photo"]
    return created_post


@router.get("/", response_model=List[PostWithUser])
async def get_all_posts(skip: int = Query(0, ge=0), limit: int = Query(10, le=100)):
    posts = []
    cursor = db.posts.find().sort("date", -1).skip(skip).limit(limit)

    async for post in cursor:
        # Get user information for this post
        user_info = await get_user_info(post["owner_id"])

        posts.append(
            PostWithUser(
                id=str(post["_id"]),
                title=post["title"],
                content=post["content"],
                date=post["date"],
                category=post["category"],
                mainImage=post.get("mainImage"),
                owner_id=post["owner_id"],
                owner_name=user_info["name"],
                owner_photo=user_info["photo"],
                readTime=post["readTime"],
                summary=post["summary"],
                likes=post.get("likes", 0),
                whoLiked=post.get("whoLiked", []),
            )
        )
    return posts


# 🔐 Get My Posts
@router.get("/mine", response_model=List[PostWithUser])
async def get_my_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    current_user: dict = Depends(get_current_user),
):
    posts = []
    try:
        async for post in (
            db.posts.find({"owner_id": str(current_user["_id"])})
            .sort("date", -1)
            .skip(skip)
            .limit(limit)
        ):
            posts.append(
                PostWithUser(
                    id=str(post["_id"]),
                    title=post["title"],
                    content=post["content"],
                    date=post["date"],
                    category=post["category"],
                    mainImage=post.get("mainImage"),
                    owner_id=post["owner_id"],
                    owner_name=current_user["name"],
                    owner_photo=current_user.get(
                        "photo",
                        "https://res.cloudinary.com/dlovcfdar/image/upload/w_100/v1752399063/p3img_r9qqsr.jpg",
                    ),
                    readTime=post["readTime"],
                    summary=post["summary"],
                    likes=post.get("likes", 0),
                    whoLiked=post.get("whoLiked", []),
                )
            )
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{post_id}", response_model=PostWithUser)
async def get_one_posts(post_id: str):
    try:
        post = await db.posts.find_one({"_id": ObjectId(post_id)})

        if post:
            # Get user information for this post
            user_info = await get_user_info(post["owner_id"])

            post["id"] = str(post["_id"])
            del post["_id"]
            post["owner_name"] = user_info["name"]
            post["owner_photo"] = user_info["photo"]
            return post
        else:
            raise HTTPException(status_code=404, detail="Post not found")
    except Exception as e:
        if "invalid ObjectId" in str(e):
            raise HTTPException(status_code=400, detail="Invalid post ID format")
        raise HTTPException(status_code=500, detail="Internal server error")


# 🔐 Update Post
@router.put("/{post_id}", response_model=str)
async def update_post(
    post_id: str,
    updated_post: PostCreate,
    current_user: dict = Depends(get_current_user),
):
    try:
        post = await db.posts.find_one({"_id": ObjectId(post_id)})

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post["owner_id"] != str(current_user["_id"]):
            raise HTTPException(
                status_code=403, detail="You are not the owner of this post"
            )

        update_data = replace_nbsp_in_post(updated_post.dict())
        await db.posts.update_one({"_id": ObjectId(post_id)}, {"$set": update_data})
        return "updated"
    except Exception as e:
        if "invalid ObjectId" in str(e):
            raise HTTPException(status_code=400, detail="Invalid post ID format")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{post_id}")
async def delete_post(post_id: str, current_user: dict = Depends(get_current_user)):
    try:
        post = await db.posts.find_one({"_id": ObjectId(post_id)})

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post["owner_id"] != str(current_user["_id"]):
            raise HTTPException(status_code=403, detail="You can't delete this post")

        await db.posts.delete_one({"_id": ObjectId(post_id)})

        # Decrement user's post count after successful post deletion
        await db.users.update_one(
            {"_id": current_user["_id"]}, {"$inc": {"postCount": -1}}
        )

        return {"message": "Post deleted successfully"}
    except Exception as e:
        if "invalid ObjectId" in str(e):
            raise HTTPException(status_code=400, detail="Invalid post ID format")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{post_id}/like")
async def like_post(post_id: str, current_user: dict = Depends(get_current_user)):
    """
    Like or unlike a post. If the user has already liked the post, it will unlike it.
    If the user hasn't liked the post, it will like it.
    """
    try:
        post = await db.posts.find_one({"_id": ObjectId(post_id)})

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        user_id = str(current_user["_id"])
        who_liked = post.get("whoLiked", [])
        current_likes = post.get("likes", 0)

        if user_id in who_liked:
            # Unlike the post
            who_liked.remove(user_id)
            current_likes -= 1
            message = "Post unliked successfully"
        else:
            # Like the post
            who_liked.append(user_id)
            current_likes += 1
            message = "Post liked successfully"

        # Update the post with new like count and whoLiked list
        await db.posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {"likes": current_likes, "whoLiked": who_liked}}
        )

        return {
            "message": message,
            "likes": current_likes,
            "whoLiked": who_liked,
            "userLiked": user_id in who_liked
        }

    except Exception as e:
        if "invalid ObjectId" in str(e):
            raise HTTPException(status_code=400, detail="Invalid post ID format")
        raise HTTPException(status_code=500, detail="Internal server error")
