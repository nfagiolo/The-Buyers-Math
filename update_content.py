import os
from google import genai
from datetime import date

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

prompt = """
Write a short, engaging 150-word daily tip focusing on the math and ROI behind one of the following topics: Basement remodeling, driveway paving, HVAC replacement, kitchen remodeling, roofing, solar panel payback, or window replacement.

Format the output strictly as an HTML <div> with a bold <h3> header and standard paragraph text.

Monetization Requirements:
1. Seamlessly integrate a relevant product recommendation contextually within the text using an Amazon Associates affiliate link structure: <a href="https://amazon.com/dp/ASIN_HERE/?tag=nfagiolo-20" target="_blank" rel="nofollow">
2. Below the paragraph, insert this exact Google AdSense responsive ad unit block:
<div style="margin-top: 20px; text-align: center;">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1199906473460957" crossorigin="anonymous"></script>
    <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-1199906473460957" data-ad-slot="5190114395" data-ad-format="auto" data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</div>
Do not include any markdown formatting like ```html. Output raw HTML only.
"""

response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
new_content = response.text


def update_index_with_articles():
    with open('index.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    grid = soup.find(class_='guides-grid') or soup.find(class_='calculator-grid')
    if not grid:
        return

    existing_links = {a['href'] for a in grid.find_all('a', href=True)}

    for filepath in glob.glob('articles/*.html'):
        normalized_path = filepath.replace('\\', '/')
        if normalized_path not in existing_links:
            with open(filepath, 'r', encoding='utf-8') as af:
                art_soup = BeautifulSoup(af.read(), 'html.parser')

            title_el = art_soup.find('title') or art_soup.find('h1')
            title = title_el.get_text(strip=True) if title_el else 'Untitled Article'

            card = soup.new_tag('div', attrs={'class': 'card'})
            a_tag = soup.new_tag('a', href=normalized_path)
            a_tag.string = title
            card.append(a_tag)
            grid.append(card)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))

update_index_with_articles()
date_str = date.today().strftime("%B %d, %Y")
html_injection = f"""
<!-- GEMINI_TIP_PLACEHOLDER -->
<div class="daily-tip-container" style="padding: 20px; background: #f9f9f9; border-radius: 8px; margin-bottom: 30px;">
    <h3>Buyer's Math Tip of the Day - {date_str}</h3>
    {new_content}
</div>
"""

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

updated_html = html_content.replace('<!-- GEMINI_TIP_PLACEHOLDER -->', html_injection)
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(updated_html)
