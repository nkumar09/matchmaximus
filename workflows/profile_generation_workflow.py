import os
import json
from datetime import datetime
from agents.bio_writer_agent import BioWriterAgent
from agents.photo_selector_agent import PhotoSelectorAgent

def run_profile_generation():
    print("🔧 Initializing BioWriterAgent...")
    bio_agent = BioWriterAgent()

    print("📝 Generating dating bio...")
    bio = bio_agent.generate_bio()

    print("\n✨ Generated Dating Bio:")
    print("--------------------------------")
    print(bio)
    print("--------------------------------")
    save_bio_version(bio)

    print("\n📸 Running PhotoSelectorAgent...")
    photo_agent = PhotoSelectorAgent()
    best_images = photo_agent.select_best_images()

    if best_images:
        print("\n✅ Top Selected Images:")
        for img, score in best_images:
            print(f"{img} → Score: {score}")
        photo_agent.save_selected_images(best_images)
    else:
        print("⚠️ No suitable images found.")

def save_bio_version(bio_text: str):
    version_dir = "data/profile_versions"
    os.makedirs(version_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{version_dir}/bio_{timestamp}.json"

    version_data = {
        "generated_at": timestamp,
        "bio": bio_text
    }

    with open(filename, "w") as f:
        json.dump(version_data, f, indent=2)

    print(f"\n💾 Bio saved to {filename}")