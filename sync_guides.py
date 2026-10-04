#!/usr/bin/env python3
"""
sync_guides.py - The Buyer's Math Universal Sitemap, RSS 2.0 & Guides Synchronizer
Scans the entire repository:
  - 16 Core Empirical Calculators
  - Flagship Guides in guides/
  - Daily Articles in articles/
  - Daily Market & Contractor Intelligence Reports in intel/
  - Essential Pages (Home, Privacy, Terms, Contact)

Generates:
  1. sitemap.xml - Complete XML sitemap for Google Search Console & Bing Webmaster
  2. feed.xml    - RSS 2.0 syndication feed for all articles and daily market dispatches
  3. index.html  - Synchronizes recent articles list
"""

import os
import re
import datetime
from email.utils import format_datetime

SITE_DOMAIN = "thebuyersmath.com"
SITE_URL = f"https://{SITE_DOMAIN}"

# 16 Core Calculators always indexed
CALCULATORS = [
    ("roofing-cost-calculator.html", "Roof Replacement Cost Estimator", 0.9),
    ("attic-insulation-calculator.html", "Attic Insulation & Air Sealing ROI Calculator", 0.9),
    ("window-replacement-estimator.html", "Window Replacement Estimator", 0.9),
    ("siding-cost-calculator.html", "Home Siding Replacement Cost Estimator", 0.9),
    ("driveway-paving-calculator.html", "Driveway Paving Calculator", 0.9),
    ("fence-cost-calculator.html", "Fence Cost & Linear Footage Estimator", 0.9),
    ("hvac-roi-calculator.html", "Heat Pump vs. Gas Furnace ROI Calculator", 0.9),
    ("mini-split-calculator.html", "Ductless Mini-Split Cost Estimator", 0.9),
    ("water-heater-calculator.html", "Water Heater Replacement Cost Estimator", 0.9),
    ("solar-payback-calculator.html", "Solar Panel Payback Timeline Calculator", 0.9),
    ("pool.html", "Pool Pump Energy Calculator", 0.9),
    ("bathroom-remodel-calculator.html", "Bathroom Remodel Cost Estimator", 0.9),
    ("kitchen-remodel-calculator.html", "Kitchen Remodel Cost Estimator", 0.9),
    ("basement-cost-calculator.html", "Basement Finishing Cost Estimator", 0.9),
    ("ev-charger-calculator.html", "EV Home Charger Installation Estimator", 0.9),
    ("generator-calculator.html", "Backup Generator Sizing Guide", 0.9)
]

def extract_meta(filepath):
    """Extracts title and description from an HTML file."""
    title = ""
    desc = ""
    if not os.path.exists(filepath):
        return title, desc
        
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    t_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
    if t_match:
        title = t_match.group(1).replace("&amp;", "&").replace(" | The Buyer's Math", "").strip()

    d_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
    if not d_match:
        d_match = re.search(r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']', content, re.IGNORECASE)
    if d_match:
        desc = d_match.group(1).replace("&amp;", "&").strip()

    return title, desc

def get_file_date(filepath, filename):
    """Derives a publication date from YYYY-MM-DD filename prefix or file mtime."""
    date_match = re.match(r"^(\d{4}-\d{2}-\d{2})", filename)
    if date_match:
        try:
            return datetime.datetime.strptime(date_match.group(1), "%Y-%m-%d")
        except ValueError:
            pass
    if os.path.exists(filepath):
        mtime = os.path.getmtime(filepath)
        return datetime.datetime.fromtimestamp(mtime)
    return datetime.datetime.now()

def generate_sitemap(all_items):
    """Builds a complete, valid sitemap.xml."""
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # 1. Homepage
    xml.append(f"""  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>{today_str}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""")

    # 2. Daily Intel Hub
    xml.append(f"""  <url>
    <loc>{SITE_URL}/intel/index.html</loc>
    <lastmod>{today_str}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>""")

    # 3. Core Calculators (Always included)
    for slug, _, priority in CALCULATORS:
        f_date = today_str
        if os.path.exists(slug):
            f_date = datetime.date.fromtimestamp(os.path.getmtime(slug)).strftime("%Y-%m-%d")
        xml.append(f"""  <url>
    <loc>{SITE_URL}/{slug}</loc>
    <lastmod>{f_date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>{priority}</priority>
  </url>""")

    # 4. Guides, Articles & Daily Intel Reports
    for item in all_items:
        xml.append(f"""  <url>
    <loc>{item['url']}</loc>
    <lastmod>{item['date_str']}</lastmod>
    <changefreq>{item['changefreq']}</changefreq>
    <priority>{item['priority']}</priority>
  </url>""")

    # 5. Core Informational / Legal Pages
    for page in ["privacy-policy.html", "terms.html", "contact.html"]:
        xml.append(f"""  <url>
    <loc>{SITE_URL}/{page}</loc>
    <lastmod>{today_str}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.3</priority>
  </url>""")

    xml.append('</urlset>')
    
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(xml))
    print(f"Generated sitemap.xml with {len(all_items) + len(CALCULATORS) + 5} URLs.")

def generate_rss_feed(feed_items):
    """Builds an RSS 2.0 feed.xml containing the latest articles and daily intelligence dispatches."""
    now_dt = datetime.datetime.now(datetime.timezone.utc)
    build_date_rfc822 = format_datetime(now_dt)

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">')
    xml.append('  <channel>')
    xml.append('    <title>The Buyer\'s Math — Daily Homeowner &amp; Contractor Intelligence</title>')
    xml.append(f'    <link>{SITE_URL}</link>')
    xml.append('    <description>Empirical home improvement cost estimators, daily commodity spot prices, contractor quote teardowns, and federal tax credit guides.</description>')
    xml.append('    <language>en-us</language>')
    xml.append(f'    <lastBuildDate>{build_date_rfc822}</lastBuildDate>')
    xml.append(f'    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>')

    # Sort descending by publication date
    feed_items.sort(key=lambda x: x["dt"], reverse=True)

    for item in feed_items[:25]:
        pub_date_rfc822 = format_datetime(item["dt"].replace(tzinfo=datetime.timezone.utc))
        safe_title = item['title'].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe_desc = item['desc'].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        xml.append('    <item>')
        xml.append(f'      <title>{safe_title}</title>')
        xml.append(f'      <link>{item["url"]}</link>')
        xml.append(f'      <guid isPermaLink="true">{item["url"]}</guid>')
        xml.append(f'      <pubDate>{pub_date_rfc822}</pubDate>')
        xml.append(f'      <description>{safe_desc}</description>')
        xml.append('    </item>')

    xml.append('  </channel>')
    xml.append('</rss>')

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write("\n".join(xml))
    print(f"Generated feed.xml with {min(len(feed_items), 25)} syndication items.")

def sync_index_articles(article_items):
    """Ensures articles in articles/ are properly linked in index.html without duplicates."""
    if not os.path.exists("index.html"):
        return

    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()

    if "<!-- ARTICLES_LIST_MARKER -->" not in content and '<ul id="article-list">' not in content:
        return

    article_items.sort(key=lambda x: x["dt"], reverse=True)

    new_list_items = ""
    for item in article_items:
        rel_path = item["rel_path"]
        if rel_path not in content:
            new_list_items += f"""          <li>
            <span class="article-date">{item['date_str']}</span>
            <a href="/{rel_path}">{item['title']}</a>
          </li>\n"""

    if new_list_items and "<!-- ARTICLES_LIST_MARKER -->" in content:
        content = content.replace("<!-- ARTICLES_LIST_MARKER -->", new_list_items + "          <!-- ARTICLES_LIST_MARKER -->")
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated index.html with new article links.")

def main():
    all_sitemap_items = []
    all_feed_items = []
    article_items = []

    # 1. Scan Flagship Guides (guides/)
    if os.path.exists("guides"):
        for fname in os.listdir("guides"):
            if fname.endswith(".html"):
                fpath = os.path.join("guides", fname)
                title, desc = extract_meta(fpath)
                dt = get_file_date(fpath, fname)
                date_str = dt.strftime("%Y-%m-%d")
                item = {
                    "title": title or fname.replace(".html", "").replace("-", " ").title(),
                    "desc": desc or "In-depth homeowner guide and empirical cost breakdown.",
                    "url": f"{SITE_URL}/guides/{fname}",
                    "rel_path": f"guides/{fname}",
                    "date_str": date_str,
                    "dt": dt,
                    "changefreq": "monthly",
                    "priority": 0.8
                }
                all_sitemap_items.append(item)
                all_feed_items.append(item)

    # 2. Scan Daily Articles (articles/)
    if os.path.exists("articles"):
        for fname in os.listdir("articles"):
            if fname.endswith(".html") and fname != "index.html":
                fpath = os.path.join("articles", fname)
                title, desc = extract_meta(fpath)
                dt = get_file_date(fpath, fname)
                date_str = dt.strftime("%Y-%m-%d")
                item = {
                    "title": title or fname.replace(".html", "").replace("-", " ").title(),
                    "desc": desc or "Daily home improvement cost analysis, labor rates, and buying guide.",
                    "url": f"{SITE_URL}/articles/{fname}",
                    "rel_path": f"articles/{fname}",
                    "date_str": date_str,
                    "dt": dt,
                    "changefreq": "monthly",
                    "priority": 0.7
                }
                all_sitemap_items.append(item)
                all_feed_items.append(item)
                article_items.append(item)

    # 3. Scan Daily Market & Contractor Intelligence (intel/)
    if os.path.exists("intel"):
        for fname in os.listdir("intel"):
            if fname.endswith(".html") and fname != "index.html":
                fpath = os.path.join("intel", fname)
                title, desc = extract_meta(fpath)
                dt = get_file_date(fpath, fname)
                date_str = dt.strftime("%Y-%m-%d")
                item = {
                    "title": title or f"Daily Market Intelligence — {date_str}",
                    "desc": desc or "Daily material spot prices, contractor quote teardowns, and building code briefs.",
                    "url": f"{SITE_URL}/intel/{fname}",
                    "rel_path": f"intel/{fname}",
                    "date_str": date_str,
                    "dt": dt,
                    "changefreq": "daily",
                    "priority": 0.8
                }
                all_sitemap_items.append(item)
                all_feed_items.append(item)

    # Generate Feeds and Sync
    generate_sitemap(all_sitemap_items)
    generate_rss_feed(all_feed_items)
    sync_index_articles(article_items)

    print("Synchronization of sitemap.xml, feed.xml, and index.html completed.")

if __name__ == "__main__":
    main()
