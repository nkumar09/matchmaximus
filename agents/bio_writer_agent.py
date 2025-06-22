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
            f"Write a short dating bio for someone named {name}, who's {self.user_data['age']} years old and lives in {self.user_data['location']}. "
            f"They're into {interests} and described as {traits}. The goal is: '{goal}'. "
            f"Use a {preferred_tone} tone, and keep it under {self.user_data['max_bio_length']} characters. "
            "It should sound real—not like it was written by AI or a copywriter. Keep it casual, clear, and friendly."
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