# apply_calculator_updates.py
# Automatically adds <link rel="stylesheet" href="/styles.css"> to all 11 calculators

import os

CALCULATOR_FILES = [
    "roofing-cost-calculator.html",
    "hvac-roi-calculator.html",
    "basement-cost-calculator.html",
    "solar-payback-calculator.html",
    "kitchen-remodel-calculator.html",
    "driveway-paving-calculator.html",
    "window-replacement-estimator.html",
    "pool.html",
    "mini-split-calculator.html",
    "generator-calculator.html",
    "water-heater-calculator.html"
]

def update_file(filename):
    if not os.path.exists(filename):
        return
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    if 'href="/styles.css"' not in content and 'href="styles.css"' not in content:
        content = content.replace("</head>", '  <link rel="stylesheet" href="/styles.css">\n</head>', 1)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {filename}")
    else:
        print(f"{filename} already linked")

def main():
    for filename in CALCULATOR_FILES:
        update_file(filename)
    print("Done linking styles.css to all calculators.")

if __name__ == "__main__":
    main()
