MatchMaxima

One-liner: A multi-agent AI system that crafts, tests, and iterates dating profiles to maximize your matches across modern dating apps.

---
<pre>
## 1. Project Purpose
<code>
MatchMaxima leverages CrewAI agents combined with OpenAI models and lightweight vision tools to generate engaging bios, pick the best photos, optimize everything per platform rules, and learn from real-world feedback.
</code>
</pre>
---

<pre>
## 2. High-Level Architecture

<code>
/MatchMaxima
├── agents/
│   ├── bio_writer_agent.py          # Generates initial bios
│   ├── tone_style_agent.py         # Adjusts tone to user preference
│   ├── platform_optimizer_agent.py # Fits bios to app-specific limits
│   ├── photo_selector_agent.py     # Ranks photos heuristically
│   └── analytics_agent.py          # Reads swipe/match stats
├── tools/
│   └── tone_analysis_tool.py       # Detects tone via OpenAI
├── workflows/
│   ├── profile_generation_workflow.py   # Full generation pipeline
│   ├── optimization_feedback_loop.py    # Performance feedback loop
│   └── ab_testing_workflow.py           # A/B test bio variants
├── data/
│   ├── user_inputs.json
│   ├── platform_metadata.json
│   ├── performance_feedback.json
│   ├── images/
│   └── profile_versions/
├── prompts/
├── config/
├── main.py
└── README.md
</code>
</pre>
---
<pre>
## 3. Prerequisites
<code>
Requirement	Version
Python	≥ 3.9
macOS/Linux	Tested on macOS 15
OpenAI API	Valid key in .env

# Core libraries
pip install crewai openai langchain langchain-core langchain-community python-dotenv

# Vision / ML (optional for future photo scoring)
pip install torch torchvision pillow scikit-learn
</code>
</pre>
---

<pre>
##4. Quick Setup

<code>
# 1 — clone / navigate
cd /Users/nischaykumar/Documents/AIAgent
mkdir MatchMaxima && cd MatchMaxima

# 2 — create venv
python3 -m venv venv && source venv/bin/activate

# 3 — lay out folders
python - <<'PY'
import os, pathlib
folders=[
 "agents","tools","data","data/images","data/profile_versions",
 "workflows","prompts","config"]
for f in folders: pathlib.Path(f).mkdir(parents=True, exist_ok=True)
PY

# 4 — copy / paste the code files from this repo

# 5 — add your OpenAI key
echo "OPENAI_API_KEY=sk-..." > .env
</code>
</pre>
---

<pre>
## 5. Running Workflows

<code>
5.1 Generate a New Profile

python main.py            # default runs profile_generation_workflow

Outputs:
	•	Final platform-ready bio (console)
	•	data/profile_versions/bio_<timestamp>.json
	•	data/profile_versions/bio_platform_<timestamp>.json
	•	data/profile_versions/photos_<timestamp>.json

5.2 Analyse Performance Feedback

# In main.py uncomment:
# run_feedback_analysis()
python main.py

Generates feedback_<timestamp>.json with engagement score + suggestions.

5.3 Run A/B Test

# In main.py uncomment:
# run_ab_test()
python main.py

Creates ab_test_<timestamp>.json holding Variant A & B bios + photos.
</code>
</pre>
---

<pre>
## 6. Data Flow Diagram

<code>
graph TD
A[User Inputs] -->|user_inputs.json| B(BioWriterAgent)
B --> C(ToneStyleAgent)
C --> D(PlatformOptimizerAgent)
D -->|Final Bio| E[profile_versions]
A --> F(PhotoSelectorAgent)
F -->|Top photos| E
E -->|Profile live| G[Dating App]
G -->|Swipes/Matches| H[performance_feedback.json]
H --> I(AnalyticsAgent)
I -->|Suggestions| developer
</code>
</pre>
---

<pre>
## 7. Customisation

<code>
	•	Change tone: Edit preferred_tone in user_inputs.json (e.g., “witty”, “casual”).
	•	Platform switch: Set platform + max_bio_length accordingly.
	•	Add new agent: Place file in agents/, import into a workflow, and keep folder names intact.
</code>
</pre>
---

<pre>
## 8. Contributing Guidelines

<code>
	1.	Follow existing naming conventions.
	2.	Never rename or delete locked folders/files.
	3.	Commit readable, well-commented Python (PEP 8) – keep prompts human-like.
	4.	Update this README if you add significant functionality.
</code>
</pre>
---

<pre>
## 9. License

<code>
MIT — see LICENSE (to add).
</code>
</pre>
---

<pre>
## 10. Credits
<code>
	•	CrewAI for multi-agent orchestration
	•	OpenAI GPT-4o for text generation and tone analysis
</code>
</pre>