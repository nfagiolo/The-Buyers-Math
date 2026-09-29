import os
import datetime
import re
import urllib.parse
import time
from google import genai

# Configure Gemini API using the new SDK
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# A rotating list pairing the article topic with a highly relevant Amazon search keyword
topics = [
    {"title": "Are variable speed pool pumps worth the investment in 2026?", "keyword": "robotic pool cleaner"},
    {"title": "How to safely size a backup generator for a well pump and AC", "keyword": "heavy duty generator extension cord"},
    {"title": "Heat Pump vs Gas Furnace: Operating costs compared", "keyword": "smart thermostat ecobee nest"},
    {"title": "Is a tankless water heater worth the installation cost?", "keyword": "smart water leak detector wifi"},
    {"title": "Understanding the 30% Federal Tax Credit for residential solar", "keyword": "portable power station solar generator"},
    {"title": "Retrofit vs Full-Frame Window Replacement: What you need to know", "keyword": "thermal leak detector"},
    {"title": "Asphalt vs Concrete Driveways: Lifespan and maintenance costs", "keyword": "electric pressure washer"},
    {"title": "How to plan a basement finishing project with a bathroom addition", "keyword": "smart dehumidifier with pump basement"},
    {"title": "Cabinet tiers explained: RTA vs Semi-Custom vs Custom", "keyword": "digital laser measure"},
    {"title": "How to calculate roofing materials by the square", "keyword": "magnetic nail sweeper with wheels"}
]

# Pick a topic based on the day of the year so it rotates sequentially
day_of_year = datetime.datetime.now().timetuple().tm_yday
selected_topic = topics[day_of_year % len(topics)]
topic = selected_topic["title"]
keyword = selected_topic["keyword"]

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
        break # Exit loop if successful
    except Exception as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt < max_retries - 1:
            print("Google API is busy. Waiting 60 seconds before retrying...")
            time.sleep(60)
        else:
            print("Max retries reached. Exiting script.")
            raise e

# Generate the file name and URL path
date_str = datetime.datetime.now().strftime("%Y-%m-%d")
slug = re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')
filename = f"articles/{date_str}-{slug}.html"

# Ensure the articles directory exists
os.makedirs("articles", exist_ok=True)

# URL Encode the KEYWORD (not the title) for Amazon using quote_plus (adds '+' for spaces)
amazon_query = urllib.parse.quote_plus(keyword)

# Build the complete HTML file
template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Google tag (gtag.js) -->
    <script async defer src="[https://www.googletagmanager.com/gtag/js?id=G-V4GTQSCFW6](https://www.googletagmanager.com/gtag/js?id=G-V4GTQSCFW6)"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', 'G-V4GTQSCFW6');
    </script>
    <!-- Google AdSense -->
    <script async defer src="[https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1199906473460957](https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1199906473460957)" crossorigin="anonymous"></script>
    
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic} | The Buyer's Math</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8fafc; color: #1e293b; padding: 2rem; max-width: 800px; margin: 0 auto; line-height: 1.6; }}
        article {{ background: #fff; padding: 2.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
        h2, h3 {{ color: #0369a1; margin-top: 2rem; }}
        a.back-link {{ display: inline-block; margin-bottom: 2rem; color: #0284c7; text-decoration: none; font-weight: bold; }}
        a.back-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <a href="../index.html" class="back-link">&larr; Back to Calculators</a>
    
    <article>
        {html_content}
    </article>

    <!-- Affiliate Monetization Section -->
    <div style="margin-top: 2rem; padding: 1.5rem; background: #fff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;">
        <h3 style="margin-top: 0; color: #0f172a; border: none;">Ready to start your project?</h3>
        <p style="color: #475569;">Find the best tools and materials to get the job done right.</p>
        <a href="[https://www.amazon.com/s?k=](https://www.amazon.com/s?k=){amazon_query}&tag=nfagiolo-20" target="_blank" style="display: inline-block; padding: 0.75rem 1.5rem; background: #f59e0b; color: #fff; text-decoration: none; font-weight: bold; border-radius: 6px; margin-top: 0.5rem;">Shop Related Tools on Amazon</a>
    </div>

    <footer style="margin-top: 40px; text-align: center; color: #64748b;">
        <p>&copy; 2026 The Buyer's Math. All rights reserved.</p>
    </footer>
</body>
</html>"""

# Save the new article file
with open(filename, "w", encoding="utf-8") as f:
    f.write(template)

# Inject the link into the homepage safely to prevent duplicates
with open("index.html", "r", encoding="utf-8") as f:
    index_html = f.read()

# Only add the link if today's date isn't already in the list
if date_str not in index_html:
    link_html = f'<li><span style="color:#64748b; font-size:0.85em; margin-right:10px;">{date_str}</span> <a href="{filename}" style="color:#0f172a; font-weight:600; text-decoration:none;">{topic}</a></li>\n                <!-- ARTICLES_LIST_MARKER -->'
    index_html = index_html.replace('<!-- ARTICLES_LIST_MARKER -->', link_html, 1)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"Successfully generated {filename} and added link to index.html")
else:
    print(f"Successfully updated {filename}. Link already exists on homepage, skipping injection.")
