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
            f"You're helping someone get better matches on {self.platform}. Take this dating bio and make sure it fits within {self.max_length} characters. "
            "Keep it friendly, relaxed, and like something a real person would write—not too polished. "
            "Only make small edits if needed. Avoid buzzwords or overly clever stuff. No emojis unless already present.\n\n"
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