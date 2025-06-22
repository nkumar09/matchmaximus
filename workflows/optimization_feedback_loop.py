import os
import json
from datetime import datetime
from agents.analytics_agent import AnalyticsAgent
from tools.storage_helper import get_version_folder

def run_feedback_analysis():
    print("\n🔁 Running Optimization Feedback Loop...")
    analytics_agent = AnalyticsAgent()
    feedback = analytics_agent.feedback
    metadata = analytics_agent.metadata

    engagement_score = analytics_agent.calculate_engagement_score()
    suggestions = analytics_agent.generate_recommendations()
    platform = feedback.get("platform", "unknown")
    swipes = feedback.get("swipes", 0)
    matches = feedback.get("matches", 0)

    print("\n📊 MatchMaxima Profile Feedback Summary")
    print("----------------------------------------")
    print(f"Platform: {platform}")
    print(f"Total Swipes: {swipes}")
    print(f"Matches: {matches}")
    print(f"Engagement Score: {engagement_score}%")
    print("\n💡 Suggestions:")
    for s in suggestions:
        print(f"- {s}")

    save_feedback_summary(platform, swipes, matches, engagement_score, suggestions)

def save_feedback_summary(platform, swipes, matches, engagement_score, suggestions):
    version_dir = get_version_folder()
    os.makedirs(version_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{version_dir}/feedback_{timestamp}.json"

    summary = {
        "generated_at": timestamp,
        "platform": platform,
        "swipes": swipes,
        "matches": matches,
        "engagement_score_percent": engagement_score,
        "suggestions": suggestions
    }

    with open(filename, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n💾 Feedback summary saved to {filename}")