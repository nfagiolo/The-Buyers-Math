import os
import google.generativeai as genai
from datetime import date

api_key = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
prompt = "Write a short, engaging 150-word daily tip about the math behind buying real estate or businesses. Format it as an HTML <div> with a bold header and standard paragraph text. Do not include markdown formatting. Also include an Amazon affiliate link using tag YOUR_AMAZON_TAG-20 and a Google AdSense script block with client ca-pub-1199906473460957 and slot YOUR_AD_SLOT_ID."
response = model.generate_content(prompt)
new_content = response.text
date_str = date.today().strftime('%B %d, %Y')
html_injection = f"""
<!-- GEMINI_TIP_PLACEHOLDER -->
<div class="daily-tip">
    <h3>Buyer's Math Tip of the Day - {date_str}</h3>
    {new_content}
</div>
"""

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as file: html_content = file.read()
updated_html = html_content.replace('<!-- GEMINI_TIP_PLACEHOLDER -->', html_injection)
with open(file_path, 'w', encoding='utf-8') as file: file.write(updated_html)
