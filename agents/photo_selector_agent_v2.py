import os
import json
from datetime import datetime
from PIL import Image
import torch
import asyncio
from concurrent.futures import ThreadPoolExecutor
from transformers import CLIPProcessor, CLIPModel
from tools.image_optim_tool import optimize_image
from tools.storage_helper import get_version_folder

class PhotoSelectorAgent:
    def __init__(self, image_dir='data/images'):
        self.image_dir = image_dir
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32", torch_dtype=torch.float32)
        self.model.to(self.device)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        self.prompt_categories = {
            "expression": {
                "natural smile": 2,
                "confident body language": 1.5,
                "natural and confident expression": 2,
                "relaxed posture": 1.2
            },
            "composition": {
                "clear profile photo": 2,
                "sharp focus face": 1.5,
                "professional headshot": 1.8,
                "shoulders visible": 1.2
            },
            "lighting": {
                "bright background": 1,
                "outdoor lighting": 1.5,
                "indoor soft lighting": 1.2
            },
            "engagement": {
                "eye contact with camera": 2,
                "friendly looking person": 1.5,
                "inviting gesture": 1
            },
            "style & setting": {
                "well-groomed appearance": 1.3,
                "trendy outfit": 1,
                "tidy background": 1,
                "neutral background": 0.8
            }
        }

        self.prompts = list({p for cat in self.prompt_categories.values() for p in cat})

        self.tips_map = {
            "natural smile": "Use a relaxed, candid smile instead of forced grins.",
            "confident body language": "Stand tall or sit comfortably, avoid crossed arms.",
            "natural and confident expression": "Avoid looking too posed—look relaxed and sincere.",
            "relaxed posture": "Angle your shoulders and avoid stiff body language.",
            "clear profile photo": "Use high-resolution, clean images with no overlays or filters.",
            "sharp focus face": "Make sure your face is well-lit and crisp, not blurry.",
            "professional headshot": "Frame the photo at chest-level or higher with clear lighting.",
            "shoulders visible": "Avoid extreme close-ups—show upper body for context.",
            "bright background": "Take photos during the day or in well-lit environments.",
            "outdoor lighting": "Natural sunlight helps create vibrant, realistic photos.",
            "indoor soft lighting": "Use warm lighting; avoid harsh shadows or direct flash.",
            "eye contact with camera": "Looking into the lens creates a stronger connection.",
            "friendly looking person": "Let your expression reflect warmth and openness.",
            "inviting gesture": "Small waves or open arms help convey friendliness.",
            "well-groomed appearance": "Style your hair and groom facial hair cleanly.",
            "trendy outfit": "Wear outfits that are flattering and reflect your style.",
            "tidy background": "Avoid clutter—clean, minimalistic settings work best.",
            "neutral background": "Plain walls or natural settings keep the focus on you."
        }

    def select_best_images(self, max_images=6):
        if not os.path.exists(self.image_dir):
            print(f"⚠️ Image directory '{self.image_dir}' not found.")
            return []

        image_files = [
            f for f in os.listdir(self.image_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ][:max_images]

        if not image_files:
            print("⚠️ No image files found.")
            return []

        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor()

        async def process_image_async(img_file):
            return await loop.run_in_executor(executor, self._process_single_image, img_file)

        tasks = [process_image_async(img) for img in image_files]
        results = loop.run_until_complete(asyncio.gather(*tasks))

        results = [res for res in results if res]
        results.sort(key=lambda x: x["score"], reverse=True)

        print(f"\n✅ Top Selected Images:")
        for result in results:
            print(f"{result['filename']} → Score: {result['score']}")
            for reason, tip in zip(result["reasons"], result["tips"]):
                print(f"   ✔ Reason: {reason}")
                print(f"   💡 Tip: {tip}")

        return results

    def _process_single_image(self, img_file):
        image_path = os.path.join(self.image_dir, img_file)
        try:
            optimized_image = optimize_image(image_path)

            inputs = self.processor(
                text=self.prompts,
                images=[optimized_image],
                return_tensors="pt",
                padding=True
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)[0]

            score = self._score_image(probs)
            top_indices = torch.topk(probs, k=5).indices.tolist()
            reasons = [self.prompts[i] for i in top_indices]
            tips = [self.tips_map.get(r, "No tip available.") for r in reasons]

            return {
                "filename": img_file,
                "score": score,
                "reasons": reasons,
                "tips": tips
            }

        except Exception as e:
            print(f"❌ Error processing {img_file}: {e}")
            return None

    def _score_image(self, probs):
        weighted_total = 0
        weight_sum = 0

        for prompt, prob in zip(self.prompts, probs):
            for category_prompts in self.prompt_categories.values():
                if prompt in category_prompts:
                    weight = category_prompts[prompt]
                    weighted_total += prob.item() * weight
                    weight_sum += weight

        if weight_sum == 0:
            return 0.0

        raw_score = (weighted_total / weight_sum) * 100
        return round(raw_score, 1)

    def save_selected_images(self, selected_images):
        version_dir = get_version_folder()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{version_dir}/photos_{timestamp}.json"

        data = {
            "generated_at": timestamp,
            "primary_image": selected_images[0]["filename"] if selected_images else None,
            "selected_images": selected_images
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"💾 Image selection saved to {filename}")

        # Save thumbnails
        thumb_dir = os.path.join(version_dir, "thumbs")
        os.makedirs(thumb_dir, exist_ok=True)

        for img in selected_images:
            try:
                src = os.path.join(self.image_dir, img["filename"])
                dst = os.path.join(thumb_dir, f"thumb_{img['filename']}")
                optimized = optimize_image(src)
                optimized.thumbnail((300, 300))
                optimized.save(dst)
            except Exception as e:
                print(f"⚠️ Failed to save thumbnail for {img['filename']}: {e}")