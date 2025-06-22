# ## Test for Tone Analysis Tool
# from tools.tone_analysis_tool import ToneAnalysisTool

# tool = ToneAnalysisTool()
# text = "I love traveling to weird places and making people laugh along the way. Dogs > humans."
# print(tool.analyze_tone(text))  # Expected: "funny"


# ## Test for Bio Writer Agent
# from agents.bio_writer_agent import BioWriterAgent

# agent = BioWriterAgent()
# bio = agent.generate_bio()
# print("Generated Bio:\n", bio)


# ## Test for Photo Selector Agent
# from agents.photo_selector_agent import PhotoSelectorAgent

# agent = PhotoSelectorAgent()
# results = agent.select_best_images()

# print("\n📸 Top Selected Images:")
# for img, score in results:
#     print(f"{img} -> Score: {score}")

# ## Test for Tone Style Agent
# from agents.tone_style_agent import ToneStyleAgent

# bio = "I love hiking, photography, and dogs. Let’s trade terrible puns and go on random adventures."
# agent = ToneStyleAgent()
# updated_bio = agent.adjust_tone_if_needed(bio)

# print("\n🎨 Final Bio with Adjusted Tone:\n", updated_bio)

## Test for Platform Optimizer Agent
from agents.platform_optimizer_agent import PlatformOptimizerAgent

raw_bio = "Swipe right if you like deep convos, bad puns, and spontaneous midnight drives. No drama, just vibes."
agent = PlatformOptimizerAgent()
final_bio = agent.optimize_for_platform(raw_bio)

print("\n📱 Platform-Optimized Bio:\n", final_bio)