import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "dlovcfdar"),
    api_key=os.getenv("CLOUDINARY_API_KEY", "535447897778991"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", "zyBsfx15um1j5Fst3qocTKRkUpk")
)