import os
import datetime
import re
import urllib.parse
import time
from google import genai

# Configure Gemini API using the new SDK
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# A rotating list of highly-searchable long-tail topics related to your tools
topics = [
    "Are variable speed pool pumps worth the investment in 2026?",
    "How to safely size a backup generator for a well pump and AC",
    "Heat Pump vs Gas Furnace: Operating costs compared",
    "Is a tankless water heater worth the installation cost?",
    "Understanding the 30% Federal Tax Credit for residential solar",
    "Retrofit vs Full-Frame Window Replacement: What you need to know",
    "Asphalt vs Concrete Driveways: Lifespan and maintenance costs",
    "How to plan a basement finishing project with a bathroom addition",
    "Cabinet tiers explained: RTA vs Semi-Custom vs Custom",
    "How to calculate roofing materials by the square"
]

# Pick a topic based on the day of the year so it rotates sequentially
day_of_year = datetime.datetime.now().timetuple().tm_yday
topic = topics[day_of_year % len(topics)]

# Generate the SEO article content
prompt = f"""
Write an authoritative, SEO-optimized home improvement guide about: "{topic}".
Format the output strictly in HTML. 
Include an <h2> title, several <h3> subheadings, <p> paragraphs, and <ul> lists where appropriate.
Keep it factual, professional, and around 800 words. 
Do NOT include ```html markdown blocks, head, or body tags, just the raw inner HTML content.
"""

# Retry logic for handling temporary server overloads
max_retries = 3
html_content = ""

for attempt in range(max_retries):
    try:
        # Call the model using the new syntax
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt
        )
        html_content = response.text.replace("```html", "").replace("```", "").strip()
