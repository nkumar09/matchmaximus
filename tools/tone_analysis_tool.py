import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ToneAnalysisTool:
    def __init__(self):
        self.label_set = ["funny", "confident", "romantic", "witty", "mysterious", "professional", "casual"]

    def analyze_tone(self, text: str) -> str:
        system_prompt = (
            "You are a language expert. Given a user's bio or dating profile text, "
            "identify the dominant tone from the following options: "
            + ", ".join(self.label_set) + 
            ". Only return the most likely label. No explanation needed."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.2
        )

        tone = response.choices[0].message.content.strip().lower()
        if tone in self.label_set:
            return tone
        return "unknown"