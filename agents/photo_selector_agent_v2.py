import os
import json
from datetime import datetime
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch
from tools.image_optim_tool import optimize_image
from tools.storage_helper import get_version_folder

class PhotoSelectorAgent:
    def __init__(self, image_dir='data/images'):
        self.image_dir = image_dir
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        self.prompts = [
            "clear profile photo",
            "natural smile",
            "friendly looking person",
            "sharp focus face",
            "bright background",
            "outdoor lighting",
            "indoor soft lighting",
            "eye contact with camera",
            "professional headshot",
            "natural and confident expression"
        ]

        self.tips_map = {
            "clear profile photo": "Use a high-resolution image without blur.",
            "natural smile": "Smile gently or candidly to look approachable.",
            "friendly looking person": "Avoid blank or serious expressions.",
            "sharp focus face": "Ensure your face is in focus with no distractions.",
            "bright background": "Use well-lit environments, avoid shadows.",
            "outdoor lighting": "Daylight improves color and clarity.",
            "indoor soft lighting": "Use warm light sources, avoid harsh shadows.",
            "eye contact with camera": "Look directly at the camera to build trust.",
            "professional headshot": "Crop above chest level with good posture.",
            "natural and confident expression": "Look relaxed and confident, not posed."
        }

    def select_best_images(self, top_k=3):
        if not os.path.exists(self.image_dir):
            print(f"⚠️ Image directory '{self.image_dir}' not found.")
            return []

        image_files = [
            f for f in os.listdir(self.image_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]

        if not image_files:
            print("⚠️ No image files found.")
            return []

        results = []

        for img_file in image_files:
            image_path = os.path.join(self.image_dir, img_file)
            try:
                optimized_image = optimize_image(image_path)

                inputs = self.processor(
                    text=self.prompts,
                    images=optimized_image,
                    return_tensors="pt",
                    padding=True
                ).to(self.device)

                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)[0]

                top_k_values = torch.topk(probs, k=3)
                top_score = top_k_values.values.mean().item()

                # Scale and round to nearest 0.5
                raw_score = min(top_score * 12.5, 10)
                score = round(raw_score * 2) / 2  # nearest 0.5

                top_indices = top_k_values.indices.tolist()
                reasons = [self.prompts[i] for i in top_indices]
                tips = [self.tips_map.get(reason, "") for reason in reasons]

                results.append({
                    "filename": img_file,
                    "score": score,
                    "reasons": reasons,
                    "tips": tips
                })
            except Exception as e:
                print(f"❌ Error processing {img_file}: {e}")

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def save_selected_images(self, selected_images):
        version_dir = get_version_folder()
        os.makedirs(version_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{version_dir}/photos_{timestamp}.json"

        data = {
            "generated_at": timestamp,
            "selected_images": selected_images
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"💾 Image selection saved to {filename}")
