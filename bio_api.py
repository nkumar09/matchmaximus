#bio_api.py
from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from pydantic import BaseModel
from agents.bio_writer_agent import BioWriterAgent
import uvicorn
import tempfile
import json
import os

app = FastAPI()

class UserInput(BaseModel):
    name: str
    age: int
    location: str
    interests: list[str]
    personality_traits: list[str]
    goal: str
    preferred_tone: str = "casual"

@app.post("/generate-bio")
def generate_bio(input_data: UserInput):
    try:
        # Save temp user input to mimic local JSON loading
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".json") as tmp_file:
            json.dump(input_data.dict(), tmp_file)
            tmp_file_path = tmp_file.name

        # Instantiate agent with the temp file
        agent = BioWriterAgent(user_data_path=tmp_file_path)
        generated_bio = agent.generate_bio()

        # Clean up temp file
        os.remove(tmp_file_path)

        return {"generated_bio": generated_bio}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
from agents.tone_style_agent import ToneStyleAgent

class ToneAdjustInput(BaseModel):
    bio: str
    preferred_tone: str

@app.post("/adjust-tone")
def adjust_tone(input_data: ToneAdjustInput):
    try:
        # Prepare a minimal temp user data file
        temp_data = {
            "preferred_tone": input_data.preferred_tone
        }

        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".json") as tmp_file:
            json.dump(temp_data, tmp_file)
            tmp_file_path = tmp_file.name

        # Use the tone agent with dynamic tone input
        tone_agent = ToneStyleAgent(user_data_path=tmp_file_path)
        adjusted_bio = tone_agent.adjust_tone_if_needed(input_data.bio)

        os.remove(tmp_file_path)

        return {
            "adjusted_bio": adjusted_bio
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
from agents.platform_optimizer_agent import PlatformOptimizerAgent

class PlatformOptimizeInput(BaseModel):
    bio: str
    platform: str = "Tinder"
    max_bio_length: int = 500

@app.post("/optimize-platform")
def optimize_bio(input_data: PlatformOptimizeInput):
    try:
        # Create temp user data with platform info
        temp_data = {
            "platform": input_data.platform,
            "max_bio_length": input_data.max_bio_length
        }

        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".json") as tmp_file:
            json.dump(temp_data, tmp_file)
            tmp_file_path = tmp_file.name

        # Run optimization
        optimizer = PlatformOptimizerAgent(user_data_path=tmp_file_path)
        optimized_bio = optimizer.optimize_for_platform(input_data.bio)

        os.remove(tmp_file_path)

        return {"optimized_bio": optimized_bio}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
from typing import List
import shutil
from agents.photo_selector_agent_v3 import PhotoSelectorAgent

@app.post("/select-photos")
async def select_photos(files: List[UploadFile] = File(...)):
    upload_dir = "data/images"
    os.makedirs(upload_dir, exist_ok=True)
    saved_files = []

    try:
        # Save uploaded files
        for file in files:
            file_path = os.path.join(upload_dir, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            saved_files.append(file_path)

        # Run the agent
        agent = PhotoSelectorAgent(image_dir=upload_dir)
        selected = await agent.select_best_images()

        return {
            "selected_photos": [
                {
                    "filename": img["filename"],
                    "score": img["score"],
                    "caption": img["caption"],
                    "tips": img["tips"]
                }
                for img in selected
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 🧹 Clean up all uploaded files
        for file_path in saved_files:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"⚠️  Cleanup failed for {file_path}: {e}")

from agents.bio_writer_agent import BioWriterAgent
from agents.tone_style_agent import ToneStyleAgent
from agents.platform_optimizer_agent import PlatformOptimizerAgent
from agents.photo_selector_agent_v3 import PhotoSelectorAgent

@app.post("/generate-complete-profile")
async def generate_complete_profile(
    name: str = Form(...),
    age: int = Form(...),
    location: str = Form(...),
    interests: str = Form(...),  # comma-separated
    personality_traits: str = Form(...),  # comma-separated
    goal: str = Form(...),
    preferred_tone: str = Form("casual"),
    platform: str = Form("Tinder"),
    max_bio_length: int = Form(280),
    files: List[UploadFile] = File(...)
):
    try:
        # Step 1: Save temporary user data
        user_data = {
            "name": name,
            "age": age,
            "location": location,
            "interests": [i.strip() for i in interests.split(",")],
            "personality_traits": [t.strip() for t in personality_traits.split(",")],
            "goal": goal,
            "preferred_tone": preferred_tone,
            "platform": platform,
            "max_bio_length": max_bio_length
        }

        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".json") as tmp_file:
            json.dump(user_data, tmp_file)
            tmp_file_path = tmp_file.name

        # Step 2: Generate raw bio
        bio_agent = BioWriterAgent(user_data_path=tmp_file_path)
        raw_bio = bio_agent.generate_bio()

        # Step 3: Adjust tone
        tone_agent = ToneStyleAgent(user_data_path=tmp_file_path)
        adjusted_bio = tone_agent.adjust_tone_if_needed(raw_bio)

        # Step 4: Optimize for platform
        platform_agent = PlatformOptimizerAgent(user_data_path=tmp_file_path)
        final_bio = platform_agent.optimize_for_platform(adjusted_bio)

        # Step 5: Process photos
        upload_dir = "data/images"
        os.makedirs(upload_dir, exist_ok=True)
        saved_files = []

        for file in files:
            file_path = os.path.join(upload_dir, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            saved_files.append(file_path)

        photo_agent = PhotoSelectorAgent(image_dir=upload_dir)
        selected_photos = await photo_agent.select_best_images()

        import base64
        from io import BytesIO
        from PIL import Image

        def generate_base64_thumbnail(image_path: str, size=(300, 300)) -> str:
            try:
                img = Image.open(image_path)
                img.thumbnail(size)
                buffered = BytesIO()
                img.save(buffered, format="JPEG")
                return base64.b64encode(buffered.getvalue()).decode("utf-8")
            except Exception as e:
                print(f"⚠️ Failed to create thumbnail for {image_path}: {e}")
                return ""

        # 👉 Step 6: Attach thumbnails before cleanup
        final_photos = []
        for img in selected_photos:
            img_path = os.path.join(upload_dir, img["filename"])
            base64_thumb = generate_base64_thumbnail(img_path)
            final_photos.append({
                "filename": img["filename"],
                "score": img["score"],
                "caption": img["caption"],
                "tips": img["tips"],
                "thumbnail_base64": base64_thumb
            })

        # 🧹 Step 7: Now safely clean up
        os.remove(tmp_file_path)
        for file_path in saved_files:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"⚠️  Failed to remove {file_path}: {e}")

        # ✅ Step 8: Return response
        return {
            "final_bio": final_bio,
            "selected_photos": final_photos
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run("bio_api:app", host="0.0.0.0", port=8000, reload=True)

