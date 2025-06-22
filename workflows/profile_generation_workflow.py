import os
import json
from datetime import datetime
from agents.bio_writer_agent import BioWriterAgent
from agents.tone_style_agent import ToneStyleAgent
from agents.photo_selector_agent_v2 import PhotoSelectorAgent
from agents.platform_optimizer_agent import PlatformOptimizerAgent

def run_profile_generation():
    print("🔧 Initializing BioWriterAgent...")
    bio_agent = BioWriterAgent()

    print("📝 Generating initial dating bio...")
    raw_bio = bio_agent.generate_bio()

    print("\n🎨 Adjusting tone with ToneStyleAgent...")
    tone_agent = ToneStyleAgent()
    adjusted_bio = tone_agent.adjust_tone_if_needed(raw_bio)

    print("\n📱 Optimizing bio for platform with PlatformOptimizerAgent...")
    platform_agent = PlatformOptimizerAgent()
    final_bio = platform_agent.optimize_for_platform(adjusted_bio)

    print("\n✨ Final Platform-Ready Bio:")
    print("--------------------------------")
    print(final_bio)
    print("--------------------------------")

    save_bio_version(final_bio)
    save_platform_bio_version(final_bio)

    print("\n📸 Running PhotoSelectorAgent...")
    photo_agent = PhotoSelectorAgent()
    best_images = photo_agent.select_best_images()

    if best_images:
        print("\n✅ Top Selected Images:")
        for img_data in best_images:
            print(f"{img_data['filename']} → Score: {img_data['score']}")
            for reason, tip in zip(img_data["reasons"], img_data["tips"]):
                print(f"   ✔ Reason: {reason}")
                print(f"   💡 Tip: {tip}")
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

def save_platform_bio_version(bio_text: str):
    version_dir = "data/profile_versions"
    os.makedirs(version_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{version_dir}/bio_platform_{timestamp}.json"

    version_data = {
        "generated_at": timestamp,
        "platform_ready_bio": bio_text
    }

    with open(filename, "w") as f:
        json.dump(version_data, f, indent=2)

    print(f"💾 Platform-ready bio saved to {filename}")