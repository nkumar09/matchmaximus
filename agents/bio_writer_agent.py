import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from tools.tone_analysis_tool import ToneAnalysisTool

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class BioWriterAgent:
    def __init__(self, user_data_path='data/user_inputs.json'):
        self.tone_tool = ToneAnalysisTool()
        with open(user_data_path, 'r') as f:
            self.user_data = json.load(f)

    def generate_bio(self) -> str:
        interests = ", ".join(self.user_data["interests"])
        traits = ", ".join(self.user_data["personality_traits"])
        goal = self.user_data["goal"]
        name = self.user_data["name"]
        preferred_tone = self.user_data.get("preferred_tone", "casual")

        prompt = (
            f"Write a dating profile bio for {name}, a {self.user_data['age']}-year-old "
            f"from {self.user_data['location']}. The bio should reflect these traits: {traits}, "
            f"mention interests like {interests}, and align with the goal: '{goal}'. "
            f"Keep the tone {preferred_tone}, and format it as a short, engaging paragraph "
            f"under {self.user_data['max_bio_length']} characters."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert at writing attractive dating bios."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return response.choices[0].message.content.strip()