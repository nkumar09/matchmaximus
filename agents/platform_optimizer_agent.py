import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class PlatformOptimizerAgent:
    def __init__(self, user_data_path='data/user_inputs.json', rules_path='config/platform_rules.yaml'):
        with open(user_data_path, 'r') as f:
            self.user_data = json.load(f)
        self.platform = self.user_data.get("platform", "Tinder")
        self.max_length = self.user_data.get("max_bio_length", 500)

    def optimize_for_platform(self, bio: str) -> str:
        prompt = (
            f"You're optimizing a dating profile bio for {self.platform}. "
            f"Ensure the bio is engaging and feels natural, but under {self.max_length} characters. "
            "Keep the tone casual and real. Don't use emojis unless already present. "
            "Avoid sounding like an ad or too try-hard. Trim fluff. If it's already short and solid, return as-is.\n\n"
            f"Bio:\n\"{bio}\""
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are optimizing bios for {self.platform}'s algorithm and character limits."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6
        )

        return response.choices[0].message.content.strip()