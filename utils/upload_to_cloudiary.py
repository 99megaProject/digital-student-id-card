# utils/cloudinary_utils.py
import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()  # loads .env file


# print(os.getenv("CLOUDINARY_CLOUD_NAME"))
# Configure Cloudinary - set env vars CLOUDINARY_URL or set credentials directly.
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_file(file_obj, folder='tmp', public_id=None, overwrite=False, remove_bg=False):
    """
    Uploads a werkzeug FileStorage (file-like) to Cloudinary.
    Returns the Cloudinary upload response dict.
    """
    # file_obj can be a werkzeug FileStorage (request.files['...'])
    # result = cloudinary.uploader.upload(
    #     file_obj,
    #     folder=folder,
    #     public_id=public_id,
    #     overwrite=overwrite,
    #     resource_type="image"
    # )

    upload_options = {
        "folder": folder,
        "public_id": public_id,
        "overwrite": overwrite,
        "resource_type": "image"
    }

    # Add background removal transformation if requested
    if remove_bg:
        upload_options["effect"] = "background_removal"

    result = cloudinary.uploader.upload(file_obj, **upload_options)
    return result


