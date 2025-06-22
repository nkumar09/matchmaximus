prompt = (
            f"Write a short dating bio for someone named {name}, who's {self.user_data['age']} years old and lives in {self.user_data['location']}. "
            f"They're into {interests} and described as {traits}. The goal is: '{goal}'. "
            f"Use a {preferred_tone} tone, and keep it under {self.user_data['max_bio_length']} characters. "
            "It should sound real—not like it was written by AI or a copywriter. Keep it casual, clear, and friendly."
        )