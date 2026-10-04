import os

CALCULATOR_FILES = [
    "roofing-cost-calculator.html",
    "hvac-roi-calculator.html",
    "attic-insulation-calculator.html",
    "bathroom-remodel-calculator.html",
    "ev-charger-calculator.html",
    "fence-cost-calculator.html",
    "siding-cost-calculator.html",
    "kitchen-remodel-calculator.html",
    "solar-payback-calculator.html",
    "basement-cost-calculator.html",
    "driveway-paving-calculator.html",
    "window-replacement-estimator.html",
    "mini-split-calculator.html",
    "generator-calculator.html",
    "water-heater-calculator.html",
    "pool.html"
]

def update_file(filename):
    if not os.path.exists(filename):
        return

    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    modified = False

    if 'href="/styles.css"' not in content and 'href="styles.css"' not in content:
        content = content.replace("</head>", '  <link rel="stylesheet" href="/styles.css">\n</head>', 1)
        modified = True

    if "calculator-enhancements.js" not in content:
        enhancement_tag = '  <script src="/calculator-enhancements.js"></script>\n</body>'
        if "</body>" in content:
            content = content.replace("</body>", enhancement_tag, 1)
            modified = True

    if modified:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Enhanced {filename}")
    else:
        print(f"{filename} already up to date")

def main():
    print("Checking and enhancing all 16 calculators...")
    for filename in CALCULATOR_FILES:
        update_file(filename)
    print("Completed calculator enhancements update.")

if __name__ == "__main__":
    main()
