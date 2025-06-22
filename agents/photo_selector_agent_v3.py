#photo_selector_agent_v3.py
import os
import json
from datetime import datetime
from PIL import Image
import torch
import asyncio
from concurrent.futures import ThreadPoolExecutor
from transformers import (
    CLIPProcessor,
    CLIPModel,
    BlipProcessor,
    BlipForConditionalGeneration,
)
from tools.image_optim_tool import optimize_image
from tools.storage_helper import get_version_folder
import openai


class PhotoSelectorAgent:
    def __init__(self, image_dir="data/images"):
        self.image_dir = image_dir
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # CLIP for scoring
        self.clip_model = CLIPModel.from_pretrained(
            "openai/clip-vit-base-patch32", torch_dtype=torch.float32
        ).to(self.device)
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        # BLIP-Large for detailed captions
        self.caption_model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-large"
        ).to(self.device)
        self.caption_processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-large"
        )

        # Negative prompts for contrastive scoring
        self.negatives = [
            "a blurry image",
            "a group photo",
            "a low-quality selfie",
            "a messy background",
            "a poorly lit photo",
        ]

    # ---------- Public API -------------------------------------------------- #

    # def select_best_images(self, max_images: int = 6):
    #     if not os.path.exists(self.image_dir):
    #         print(f"⚠️  Image directory '{self.image_dir}' not found.")
    #         return []

    #     image_files = [
    #         f
    #         for f in os.listdir(self.image_dir)
    #         if f.lower().endswith((".jpg", ".jpeg", ".png"))
    #     ][: max_images]

    #     if not image_files:
    #         print("⚠️  No image files found.")
    #         return []

    #     loop = asyncio.get_event_loop()
    #     executor = ThreadPoolExecutor()

    #     async def run_async(f):  # helper
    #         return await loop.run_in_executor(executor, self._process_single_image, f)

    #     results = loop.run_until_complete(
    #         asyncio.gather(*(run_async(f) for f in image_files))
    #     )
    #     results = [r for r in results if r]
    #     results.sort(key=lambda r: r["score"], reverse=True)

    #     # Pretty print
    #     print("\n✅ Top Selected Images:")
    #     for r in results:
    #         print(f"{r['filename']} → Score: {r['score']}")
    #         print(f"   🖼️  {r['caption']}")
    #         for tip in r["tips"]:
    #             print(f"   💡 {tip}")

    #     return results

    async def select_best_images(self, max_images: int = 6):
        if not os.path.exists(self.image_dir):
            print(f"⚠️  Image directory '{self.image_dir}' not found.")
            return []

        image_files = [
            f
            for f in os.listdir(self.image_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ][:max_images]

        if not image_files:
            print("⚠️  No image files found.")
            return []

        loop = asyncio.get_running_loop()
        executor = ThreadPoolExecutor()

        async def run_async(f):
            return await loop.run_in_executor(executor, self._process_single_image, f)

        results = await asyncio.gather(*(run_async(f) for f in image_files))
        results = [r for r in results if r]
        results.sort(key=lambda r: r["score"], reverse=True)

        print("\n✅ Top Selected Images:")
        for r in results:
            print(f"{r['filename']} → Score: {r['score']}")
            print(f"   🖼️  {r['caption']}")
            for tip in r["tips"]:
                print(f"   💡 {tip}")

        return results

    def save_selected_images(self, selected):
        version_dir = get_version_folder()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"{version_dir}/photos_{ts}.json"

        data = {
            "generated_at": ts,
            "primary_image": selected[0]["filename"] if selected else None,
            "selected_images": selected,
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"💾 Image selection saved to {path}")

        # thumbnails
        thumbs = os.path.join(version_dir, "thumbs")
        os.makedirs(thumbs, exist_ok=True)
        for img in selected:
            try:
                src = os.path.join(self.image_dir, img["filename"])
                dst = os.path.join(thumbs, f"thumb_{img['filename']}")
                thumb = optimize_image(src)
                thumb.thumbnail((300, 300))
                thumb.save(dst)
            except Exception as e:
                print(f"⚠️  Thumbnail failure for {img['filename']}: {e}")

    # ---------- Internal helpers ------------------------------------------- #

    def _process_single_image(self, fname: str):
        try:
            path = os.path.join(self.image_dir, fname)
            image = optimize_image(path)

            caption = self._generate_caption(image)
            score = self._clip_score(image, caption)
            # tips = self._generate_tips(caption)
            tips = self._enrich_tip_llm(caption)

            return {
                "filename": fname,
                "score": score,
                "caption": caption,
                "tips": tips,
            }
        except Exception as e:
            print(f"❌ Error processing {fname}: {e}")
            return None

    # -- caption ------------------------------------------------------------ #

    def _enrich_caption_llm(self, caption: str) -> str:
        """Send BLIP caption to OpenAI GPT-3.5/GPT-4 for dating-profile enrichment using the new v1 API."""
        import openai

        # Make sure you have set your key in the env: OPENAI_API_KEY
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        prompt = (
            "You are an expert dating profile assistant. "
            "Given a plain, brief image description, rewrite it into a detailed, human-like sentence for a dating app. "
            "Mention the person’s outfit, expression, vibe, and setting if possible. "
            f"Description: \"{caption}\"\n"
            "Rich Caption:"
        )
        try:
            response = client.chat.completions.create(
                model="gpt-4.1",  # or "gpt-4o" if you have access
                messages=[
                    {"role": "system", "content": "You are an expert dating profile assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=60,
                temperature=0.8,
            )
            rich_caption = response.choices[0].message.content.strip().replace('"', "")
            return rich_caption
        except Exception as e:
            print(f"⚠️  LLM enrichment failed: {e}")
            return caption  # fallback to BLIP caption

    def _generate_caption(self, image: Image.Image) -> str:
        """Generate a zero-shot BLIP caption, then enrich with LLM for dating profiles."""
        inputs = self.caption_processor(images=image, text="", return_tensors="pt").to(self.device)
        out_ids = self.caption_model.generate(
            **inputs,
            max_new_tokens=80,
            num_beams=5,
            length_penalty=1.2,
            early_stopping=True,
        )
        blip_caption = self.caption_processor.decode(out_ids[0], skip_special_tokens=True).strip().capitalize()
        # Use LLM enrichment for all captions, or set a threshold for short/generic ones
        rich_caption = self._enrich_caption_llm(blip_caption)
        return rich_caption

    # -- scoring ------------------------------------------------------------ #

    def _clip_score(self, image: Image.Image, caption: str) -> float:
        texts = [caption] + self.negatives
        inputs = self.clip_processor(
            text=texts, images=[image], return_tensors="pt", padding=True
        ).to(self.device)

        with torch.no_grad():
            logits = self.clip_model(**inputs).logits_per_image
            probs = logits.softmax(dim=1)[0]
        return round(probs[0].item() * 100, 1)

    # -- tips --------------------------------------------------------------- #

    def _enrich_tip_llm(self, caption: str) -> list:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        prompt = (
            "You are an expert in online dating profiles. "
            "Based on this detailed photo description, generate 3 short, actionable tips to improve the photo for a dating profile. "
            "Focus on pose, facial expression, outfit, and background. Each tip should be 1 friendly sentence, written in the second person."
            f"\nPhoto Description: \"{caption}\""
            "\nTips:"
        )
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Or gpt-4o if available
                messages=[
                    {"role": "system", "content": "You are a dating profile expert."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=100,
                temperature=0.8,
            )
            raw = response.choices[0].message.content.strip()
            # Split into tips (handles both numbered and bulleted formats)
            tips = [
                tip.lstrip("•-1234567890. ").strip()
                for tip in raw.split("\n")
                if tip.strip()
            ]
            # Only keep lines that look like real tips (not headers)
            tips = [t for t in tips if len(t.split()) > 3]
            return tips[:3]
        except Exception as e:
            print(f"⚠️  LLM tip enrichment failed: {e}")
            return []

    def _generate_tips(self, caption: str):
        """Return a list of detailed, context-aware tips."""
        c = caption.lower()
        tips = []

        # expression
        if "smile" in c:
            tips.append(
                "Your smile creates instant warmth — let this be your primary photo."
            )
        elif "neutral" in c or "serious" in c:
            tips.append(
                "Consider a gentle smile to make the profile feel more welcoming."
            )

        # clothes
        casual = any(k in c for k in ("t-shirt", "jeans", "hoodie", "shorts"))
        smart = any(k in c for k in ("shirt", "jacket", "coat", "blazer"))
        if casual:
            tips.append(
                "Casual outfit is relatable — include one polished look for variety."
            )
        if smart:
            tips.append("Sharp outfit adds sophistication — great for first impression.")

        # setting
        if any(k in c for k in ("park", "tree", "greenery", "sunlight", "balcony")):
            tips.append(
                "Natural settings radiate trust — maintain soft, even lighting like this."
            )
        if any(k in c for k in ("city", "street", "building", "crosswalk")):
            tips.append(
                "Urban backdrop projects confidence — try a candid walking shot for energy."
            )

        # posture / hands
        if "hands in pocket" in c or "relaxed posture" in c:
            tips.append(
                "Relaxed stance works — experiment with visible hand gestures for openness."
            )

        # background / composition
        if "wall" in c or "plain background" in c:
            tips.append(
                "Neutral background keeps focus on you — try textured walls for depth."
            )
        if "potted plants" in c or "plants" in c:
            tips.append(
                "Plants add freshness — ensure they don't distract from your face."
            )

        if not tips:
            tips.append(
                "Solid photo! Ensure you're well-lit, expressive, and the clear focal point."
            )
        return tips