import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET")
)

def upload_image(file):
    try:
        print(f"Uploading to Cloudinary...")
        print(f"Cloud name: {os.environ.get('CLOUDINARY_CLOUD_NAME')}")
        result = cloudinary.uploader.upload(file)
        print(f"Upload success: {result['secure_url']}")
        return result["secure_url"]
    except Exception as e:
        print(f"Upload FAILED: {e}")
        return ""
