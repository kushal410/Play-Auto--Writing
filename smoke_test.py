import os
import json
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_URL = "https://agentdev.keepme.ai"

PAGES = [
    "/clients",
    "/accounting",
    "/audit",
    "/workspace",
    "/insights",
    "/conversations",
    "/leads",
    "/agent-training",
    "/automations",
    "/re-engage-campaign",
    "/report",
    "/beacon",
    "/knowledge-base",
    "/pulse",
    "/account",
    "/team",
    "/integrations",
    "/api-keys-webhooks",
    "/billing",
    "/theme",
    "/support",
    "/release-notes",
    "/tickets"
]

# ---------------------------
# Setup folders
# ---------------------------
os.makedirs("screenshots/pass", exist_ok=True)
os.makedirs("screenshots/fail", exist_ok=True)
os.makedirs("report", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# ---------------------------
# Logging
# ---------------------------
logging.basicConfig(
    filename="logs/automation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

report_data = {
    "timestamp": str(datetime.now()),
    "results": []
}

def add_result(status, path, message=""):
    report_data["results"].append({
        "status": status,
        "page": path,
        "message": message
    })

# ---------------------------
# MAIN TEST
# ---------------------------
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        page.goto(BASE_URL + "/clients")
        page.wait_for_load_state("networkidle")

        logging.info("Login page opened")

        print("LOGIN STEP SKIPPED (add your secure login here)")

        # -----------------------
        # PAGE LOOP
        # -----------------------
        for path in PAGES:
            url = BASE_URL + path
            name = path.strip("/").replace("/", "_")

            try:
                page.goto(url)
                page.wait_for_load_state("networkidle")

                screenshot_path = f"screenshots/pass/{name}.png"
                page.screenshot(path=screenshot_path, full_page=True)

                add_result("PASS", path)
                logging.info(f"PASS - {path}")

                print("PASS:", path)

            except Exception as e:
                screenshot_path = f"screenshots/fail/{name}.png"
                page.screenshot(path=screenshot_path, full_page=True)

                add_result("FAIL", path, str(e))
                logging.error(f"FAIL - {path} - {e}")

                print("FAIL:", path)

    except Exception as e:
        logging.error(f"Critical error: {e}")

    finally:
        browser.close()

# ---------------------------
# JSON REPORT
# ---------------------------
with open("report/report.json", "w") as f:
    json.dump(report_data, f, indent=4)

# ---------------------------
# HTML REPORT (Dashboard)
# ---------------------------
html = """
<html>
<head>
    <title>QA Smoke Report</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        .pass { color: green; }
        .fail { color: red; }
        table { border-collapse: collapse; width: 100%; }
        td, th { border: 1px solid #ddd; padding: 8px; }
    </style>
</head>
<body>
<h2>QA Smoke Test Report</h2>
<table>
<tr><th>Status</th><th>Page</th><th>Message</th></tr>
"""

for r in report_data["results"]:
    html += f"""
    <tr>
        <td class="{r['status'].lower()}">{r['status']}</td>
        <td>{r['page']}</td>
        <td>{r['message']}</td>
    </tr>
    """

html += """
</table>
</body>
</html>
"""

with open("report/report.html", "w") as f:
    f.write(html)
