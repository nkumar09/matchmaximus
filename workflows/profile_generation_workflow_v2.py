#profile_generation_workflow_v2.py
from crewai import Agent, Task, Crew, Process
from textwrap import dedent

import dotenv
dotenv.load_dotenv()

bio_agent = Agent(
    role='Bio Writer',
    goal='Create an engaging dating bio',
    backstory='Uses AI to synthesize user information into a compelling profile bio.',
    allow_delegation=False
)

tone_agent = Agent(
    role='Tone Stylist',
    goal='Adjust bio tone to match user preference',
    backstory='Analyzes and modifies tone of the bio using AI tone analysis.',
    allow_delegation=False
)

platform_agent = Agent(
    role='Platform Optimizer',
    goal='Optimize bio for the selected dating platform',
    backstory='Tailors bio length and formatting to suit platform algorithms.',
    allow_delegation=False
)

photo_agent = Agent(
    role='Photo Selector',
    goal='Pick best images for user dating profile',
    backstory='Uses vision-language models to caption, score and enrich photos for profile use.',
    allow_delegation=False
)

bio_task = Task(
    description=dedent("""\
        Generate a dating bio based on user input data: name, age, location, interests,
        personality traits, goal, and preferred tone. Save this as `initial_bio`.
    """),
    expected_output='A concise and engaging dating bio',
    agent=bio_agent
)

tone_task = Task(
    description=dedent("""\
        Analyze the tone of the `initial_bio` and adjust it if it doesn't match the user’s `preferred_tone`.
        Save the result as `tone_adjusted_bio`.
    """),
    expected_output='A tone-adjusted version of the bio',
    agent=tone_agent
)

platform_task = Task(
    description=dedent("""\
        Optimize the `tone_adjusted_bio` to meet platform constraints like character limits and tone.
        Use `platform` and `max_bio_length` inputs for this.
        Save the final result as `platform_optimized_bio`.
    """),
    expected_output='A platform-ready final bio',
    agent=platform_agent
)

photo_task = Task(
    description=dedent("""\
        Analyze the uploaded images using vision-language models. Generate captions and match tips.
        Rank and return the top images with base64 thumbnails as `selected_photos`.
    """),
    expected_output='A list of top photo selections with scores, captions, and thumbnails',
    agent=photo_agent
)

crew = Crew(
    agents=[bio_agent, tone_agent, platform_agent, photo_agent],
    tasks=[bio_task, tone_task, platform_task, photo_task],
    process=Process.sequential
)

if __name__ == "__main__":
    result = crew.kickoff()
    print(result)