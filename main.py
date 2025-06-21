#main.py
from workflows.profile_generation_workflow import run_profile_generation

if __name__ == '__main__':
    run_profile_generation()

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