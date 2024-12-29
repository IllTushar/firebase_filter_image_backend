from PIL import Image, ImageOps, ImageFilter
from io import BytesIO
import os
from sketch.pencil_sketch import pencil_sketch
from fastapi import APIRouter, UploadFile, HTTPException
from uuid import uuid4
from firebase.FirebaseDB import cred
from blackWhiteImage.images import Model
import requests
from firebase_admin import storage, db

router = APIRouter(prefix="/image", tags=["Image"])

bucket = storage.bucket()


@router.post("/upload-images/{phone_number}")
async def upload_images(file: UploadFile, phone_number: str):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400, detail="File type not supported. Only JPEG and PNG are allowed."
        )

    # Validate file size (example: 5 MB limit)
    file_size = len(await file.read())  # Read the file to check its size
    if file_size > 5 * 1024 * 1024:  # 5 MB limit
        raise HTTPException(
            status_code=400, detail="File size exceeds the limit of 5 MB."
        )

    # Reset the file pointer
    file.file.seek(0)

    # Generate a unique filename
    file_name = f"uploads/{phone_number}/normal_image/{uuid4()}.{file.filename.split('.')[-1]}"
    bucket = storage.bucket()
    blob = bucket.blob(file_name)

    try:
        # Upload image to Firebase Storage
        blob.upload_from_file(file.file, content_type=file.content_type)
        blob.make_public()  # Make the file publicly accessible

        # Get the file's public URL
        file_url = blob.public_url

        # Save file path in Realtime Database
        ref = db.reference("images").child(phone_number).child("normal_image")
        ref.set({"file_name": file_name, "file_url": file_url})  # Directly set the values

        # Response in desired format
        return {
            "images": {
                phone_number: {
                    "normal_image": {
                        "file_name": file_name,
                        "file_url": file_url
                    }
                }
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to upload image: {str(e)}"
        )


@router.post("/process-images/black-white/{phone_number}")
async def black_white(data: Model, phone_number: str):
    try:
        updated_images = {}

        for key, value in data.images.items():
            normal_image = value.get("normal_image")
            if not normal_image:
                raise HTTPException(
                    status_code=400,
                    detail=f"No 'normal_image' found for key '{key}'"
                )

            file_name = normal_image["file_name"]
            file_url = normal_image["file_url"]
            # Extract UUID from file_name (assuming format 'uploads/{uuid}.jpg')
            uuid = file_name.split('/')[1]

            # Download the image
            response = requests.get(file_url)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Failed to download image: {file_name}")

            image = Image.open(BytesIO(response.content))

            # Convert to black and white
            bw_image = image.convert("L")

            # Save locally
            bw_file_name = f"uploads/{phone_number}/blackwhite/{uuid}.jpg"
            local_path = f"/tmp/{bw_file_name}"
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            bw_image.save(local_path)

            # Upload to Firebase Storage
            blob = bucket.blob(bw_file_name)
            blob.upload_from_filename(local_path)
            bw_url = blob.public_url

            # Clean up local file
            os.remove(local_path)

            # Update Firebase Realtime Database under the existing UUID
            db.reference(f"images/{key}").update({
                "blackwhite": {
                    "file_name": bw_file_name,
                    "file_url": bw_url
                }
            })

            # Prepare the response
            updated_images[key] = {
                "normal_image": {
                    "file_name": file_name,
                    "file_url": file_url,
                },
                "blackwhite": {
                    "file_name": bw_file_name,
                    "file_url": bw_url
                }
            }

        return {"images": updated_images}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-images/sketch/{phone_number}")
async def process_images_in_sketch(data: Model, phone_number: str):
    try:
        updated_images = {}

        for key, value in data.images.items():
            normal_image = value.get("normal_image")
            if not normal_image:
                raise HTTPException(
                    status_code=400,
                    detail=f"No 'normal_image' found for key '{key}'"
                )

            file_name = normal_image["file_name"]
            file_url = normal_image["file_url"]

            # Extract UUID from file_name (assuming format 'uploads/{uuid}.jpg')
            uuid = file_name.split('/')[1]

            # Download the image
            response = requests.get(file_url)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Failed to download image: {file_name}")

            # Convert the image to sketch
            sketch_bytes = pencil_sketch(response.content)

            # Define Firebase Storage path for the sketch
            sketch_file_name = f"uploads/{phone_number}/sketch/{uuid4()}.jpg"
            blob = bucket.blob(sketch_file_name)

            # Upload sketch to Firebase Storage
            blob.upload_from_string(sketch_bytes, content_type="image/jpeg")
            sketch_url = blob.public_url

            # Update Firebase Realtime Database under the existing UUID
            db.reference(f"images/{key}").update({
                "sketch": {
                    "file_name": sketch_file_name,
                    "file_url": sketch_url
                }
            })

            # Prepare the response
            updated_images[key] = {
                "normal_image": {
                    "file_name": file_name,
                    "file_url": file_url,
                },
                "sketch": {
                    "file_name": sketch_file_name,
                    "file_url": sketch_url
                }
            }

        return {"images": updated_images}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-image/gif")
async def process_image_gif():
    pass
