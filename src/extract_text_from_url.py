import requests
from bs4 import BeautifulSoup
import json
import re
import os
from playwright.sync_api import sync_playwright
from configrations.env import env

os.makedirs("extracted_pages", exist_ok=True)

LINKEDIN_EMAIL = env.linkedin_email
LINKEDIN_PASSWORD = env.linkedin_password.get_secret_value()


def clean_filename(url):
    return re.sub(r'\W+', '_', url)[:100] + ".txt"


def extract_text(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "meta", "noscript"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        print(f"Failed to fetch {url} {e}")
        return None


def extract_linkedin_profile(linkedin_url, email, password, expected_name, expected_company):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            if os.path.exists("linkedin_login.json"):
                print(" Reusing saved LinkedIn session...")
                context = browser.new_context(storage_state="linkedin_login.json")
            else:
                print(" Logging into LinkedIn for the first time...")
                context = browser.new_context()
                page = context.new_page()
                page.goto("https://www.linkedin.com/login", timeout=60000)
                page.fill("input[name='session_key']", email)
                page.fill("input[name='session_password']", password)
                page.click("button[type='submit']")
                page.wait_for_timeout(5000)
                context.storage_state(path="linkedin_login.json")

            page = context.new_page()
            page.goto(linkedin_url, timeout=60000)
            page.wait_for_timeout(5000)

            is_person_block = page.locator("css=div[class*='cPrITgaUqRHXqEsstahTboQvkrmcrpcPI']").first.is_visible()
            is_company_block = page.locator("css=div[class*='gVdBChdagDTvwibYzgGnzhyGoypqvEALJwNf'][class*='inline-show-more-text--is-collapsed']").first.is_visible()

            if is_person_block and is_company_block:
                print("Detected: Person profile")
                name_text = ""
                company_text = ""
                try:
                    name_block = page.locator("css=div[class*='cPrITgaUqRHXqEsstahTboQvkrmcrpcPI']").first
                    name_text = name_block.inner_text(timeout=3000).strip()
                except:
                    print(" Name block not found")

                try:
                    company_block = page.locator("css=div[class*='gVdBChdagDTvwibYzgGnzhyGoypqvEALJwNf'][class*='inline-show-more-text--is-collapsed']").first
                    company_text = company_block.inner_text(timeout=3000).strip()
                except:
                    print("Company block not found")

                if expected_name.lower() in name_text.lower() and expected_company.lower() in company_text.lower():
                    return f"{name_text}\n\n{company_text}"
                else:
                    print(f"Skipping: name/company mismatch.\n  Found Name: {name_text}\n  Found Company: {company_text}")
                    return None

            else:
                print("Detected: Company profile — extracting full content")
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                for tag in soup(["script", "style", "meta", "noscript"]):
                    tag.decompose()
                return soup.get_text(separator="\n", strip=True)

    except Exception as e:
        print(f"LinkedIn fetch failed — {e}")
        return None

def process_urls_from_json(json_file):
    with open(json_file, "r") as f:
        urls = json.load(f)

    for idx, url in enumerate(urls):
        print(f"\n[{idx+1}/{len(urls)}] Processing: {url}")

        if "linkedin.com/in/" in url or "linkedin.com/company/" in url:
            text = extract_linkedin_profile(
                url,
                LINKEDIN_EMAIL,
                LINKEDIN_PASSWORD,
                expected_name="Anmol Sharma",
                expected_company="Cynoteck"
            )
        else:
            text = extract_text(url)

        if text:
            filename = clean_filename(url)
            with open(os.path.join("extracted_pages", filename), "w", encoding="utf-8") as out_file:
                out_file.write(text)
            print(f"Saved to: extracted_pages/{filename}")
        else:
            print("No content extracted.")


if __name__ == "__main__":
    process_urls_from_json("results.json")
