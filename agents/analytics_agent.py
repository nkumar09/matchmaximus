import json
from datetime import datetime

class AnalyticsAgent:
    def __init__(self,
                 feedback_data_path='data/performance_feedback.json',
                 metadata_path='data/platform_metadata.json'):
        self.feedback_data_path = feedback_data_path
        self.metadata_path = metadata_path
        self.feedback = self.load_feedback()
        self.metadata = self.load_metadata()

    def load_feedback(self):
        try:
            with open(self.feedback_data_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Feedback file not found: {self.feedback_data_path}")
            return {}

    def load_metadata(self):
        try:
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Metadata file not found: {self.metadata_path}")
            return {}

    def calculate_engagement_score(self):
        if not self.feedback:
            return 0

        matches = self.feedback.get("matches", 0)
        swipes = self.feedback.get("swipes", 1)
        return round((matches / swipes) * 100, 2)

    def generate_recommendations(self):
        if not self.feedback:
            return ["⚠️ No feedback data to analyze."]

        platform = self.feedback.get("platform", "unknown")
        score = self.calculate_engagement_score()
        suggestions = []

        avg_rate = self.metadata.get(platform, {}).get("average_engagement_rate")
        if avg_rate:
            if score < avg_rate:
                suggestions.append(f"📉 You're below {platform}'s average engagement rate ({avg_rate}%). Try improving your first photo or bio hook.")
            else:
                suggestions.append(f"📈 You're performing better than average on {platform}. Keep it up!")

        if score < 10:
            suggestions.append("⬆️ Try using a different primary photo—smiling or candid works best.")
            suggestions.append("📝 Consider shortening your bio or using simpler, playful language.")
        elif score < 25:
            suggestions.append("💡 Your profile is decent—try rotating a new photo or tweaking one line in your bio.")
        else:
            suggestions.append("🔥 Strong engagement! You could test alternate versions just for fun.")

        return suggestions

    def summarize(self):
        print("\n📊 MatchMaxima Profile Feedback Summary")
        print("----------------------------------------")
        print(f"Platform: {self.feedback.get('platform', 'unknown')}")
        print(f"Total Swipes: {self.feedback.get('swipes', 'N/A')}")
        print(f"Matches: {self.feedback.get('matches', 'N/A')}")
        print(f"Engagement Score: {self.calculate_engagement_score()}%")
        print("\n💡 Suggestions:")
        for s in self.generate_recommendations():
            print(f"- {s}")