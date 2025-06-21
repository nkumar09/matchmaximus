import os
import json
from datetime import datetime

class PhotoSelectorAgent:
    def __init__(self, image_dir='data/images'):
        self.image_dir = image_dir
        self.selection_criteria = {
            "keywords": ["smile", "natural", "clear", "outdoor"],
            "avoid": ["blurry", "dark", "group", "meme"]
        }

    def score_image(self, filename: str) -> int:
        score = 0
        name = filename.lower()

        for keyword in self.selection_criteria["keywords"]:
            if keyword in name:
                score += 2

        for badword in self.selection_criteria["avoid"]:
            if badword in name:
                score -= 2

        return score

    def select_best_images(self, top_k=3):
        if not os.path.exists(self.image_dir):
            print(f"⚠️ Image directory '{self.image_dir}' not found.")
            return []

        image_files = [f for f in os.listdir(self.image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not image_files:
            print("⚠️ No images found in the image directory.")
            return []

        scored_images = [(f, self.score_image(f)) for f in image_files]
        scored_images.sort(key=lambda x: x[1], reverse=True)

        best_images = scored_images[:top_k]
        return best_images

    def save_selected_images(self, selected_images):
        version_dir = "data/profile_versions"
        os.makedirs(version_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{version_dir}/photos_{timestamp}.json"

        data = {
            "generated_at": timestamp,
            "selected_images": [
                {"filename": img, "score": score}
                for img, score in selected_images
            ]
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"💾 Image selection saved to {filename}")