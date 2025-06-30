import json
import os
import time
import argparse
from get_urls import collect_all_urls
from extract_text_from_url import (
    clean_filename,
    extract_text,
    extract_linkedin_profile,
    LINKEDIN_EMAIL,
    LINKEDIN_PASSWORD,
)


def main(company, person):
    urls = collect_all_urls(company, person)

    with open("results.json", "w") as f:
        json.dump(list(urls), f, indent=2)

    os.makedirs("extracted_pages", exist_ok=True)####

    for idx, url in enumerate(urls):
        print(f"\n[{idx + 1}/{len(urls)}] Processing: {url}")

        if "linkedin.com" in url:
            text = extract_linkedin_profile(
                linkedin_url=url,
                email=LINKEDIN_EMAIL,
                password=LINKEDIN_PASSWORD,
                expected_name=person,
                expected_company=company
            )
        else:
            text = extract_text(url)

        if text:
            filename = clean_filename(url)
            with open(os.path.join("extracted_pages", filename), "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Saved to: extracted_pages/{filename}")
        else:
            print(" No content extracted.")

        time.sleep(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract URLs and content for a person and company.")
    parser.add_argument(
        "--company",
        type=str,
        required=True,
        help="Company name (e.g., 'Cynoteck Technology Solutions')"
    )
    parser.add_argument(
        "--person",
        type=str,
        required=True,
        help="Person name (e.g., 'Anmol Sharma')"
    )
    args = parser.parse_args()

    main(company=args.company, person=args.person)
