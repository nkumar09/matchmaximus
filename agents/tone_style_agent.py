import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from tools.tone_analysis_tool import ToneAnalysisTool

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ToneStyleAgent:
    def __init__(self, user_data_path='data/user_inputs.json'):
        self.tone_tool = ToneAnalysisTool()
        with open(user_data_path, 'r') as f:
            self.user_data = json.load(f)
        self.preferred_tone = self.user_data.get("preferred_tone", "casual")

    def adjust_tone_if_needed(self, bio: str) -> str:
        detected_tone = self.tone_tool.analyze_tone(bio)
        print(f"🧠 Detected tone: {detected_tone}")
        print(f"🎯 Preferred tone: {self.preferred_tone}")

        if detected_tone == self.preferred_tone:
            print("✅ Bio tone matches preference. No changes needed.")
            return bio

        print("⚠️ Tone mismatch. Adjusting tone...")

        prompt = (
            f"You are rewriting a short dating profile bio to match a {self.preferred_tone} tone. "
            "Write like a real person—not a professional writer. Avoid fancy words, overthinking, or trying too hard. "
            "Use natural, casual phrasing. Make it feel authentic, like something someone would actually write on Tinder or Bumble. "
            f"Here’s the original bio:\n\n\"{bio}\"\n\nRewrite it to sound more human, keeping the meaning intact."
        )

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You're just a regular person helping a friend improve their dating bio."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.75
        )

        return response.choices[0].message.content.strip()