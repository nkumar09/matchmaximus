import os
import json
from datetime import datetime
from agents.bio_writer_agent import BioWriterAgent
from agents.tone_style_agent import ToneStyleAgent
from agents.platform_optimizer_agent import PlatformOptimizerAgent
from agents.photo_selector_agent import PhotoSelectorAgent

def run_ab_test():
    print("\n🧪 Starting A/B Test Profile Generation...")

    # Initialize agents
    bio_agent = BioWriterAgent()
    tone_agent = ToneStyleAgent()
    platform_agent = PlatformOptimizerAgent()
    photo_agent = PhotoSelectorAgent()

    variants = {}

    for variant in ["A", "B"]:
        print(f"\n🔹 Generating Variant {variant}...")

        # Step 1: Generate new bio
        raw_bio = bio_agent.generate_bio()

        # Step 2: Tone adjust
        adjusted_bio = tone_agent.adjust_tone_if_needed(raw_bio)

        # Step 3: Optimize for platform
        final_bio = platform_agent.optimize_for_platform(adjusted_bio)

        # Step 4: Get top photos (simulate minor variation by shuffling or reordering)
        photos = photo_agent.select_best_images()
        shuffled_photos = photos[::-1] if variant == "B" else photos

        variants[variant] = {
            "bio": final_bio,
            "photos": [{"filename": img, "score": score} for img, score in shuffled_photos]
        }

    save_ab_test_results(variants)

def save_ab_test_results(variants):
    version_dir = "data/profile_versions"
    os.makedirs(version_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{version_dir}/ab_test_{timestamp}.json"

    payload = {
        "generated_at": timestamp,
        "variant_A": variants["A"],
        "variant_B": variants["B"]
    }

    with open(filename, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"\n📊 A/B Test profiles saved to {filename}")