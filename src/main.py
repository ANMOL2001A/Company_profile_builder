import json
import os
import time
import argparse
from typing import Set, Optional

from get_urls import collect_all_urls
from extract_text_from_url import (
    clean_filename,
    extract_text,
    extract_linkedin_profile,
    LINKEDIN_EMAIL,
    LINKEDIN_PASSWORD,
)


def main(*, company: str, person: str) -> None:
    """
    Main execution function to collect URLs and extract text content.

    Args:
        company (str): Name of the company.
        person (str): Name of the person.
    """
    try:
        urls: Set[str] = collect_all_urls(company, person)
    except Exception as e:
        print(f"Failed to collect URLs: {e}")
        return

    if not urls:
        print("No URLs collected. Exiting.")
        return

    try:
        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(sorted(urls), f, indent=2, ensure_ascii=False)
        print(f"Saved {len(urls)} URLs to results.json")
    except Exception as e:
        print(f"Failed to save URLs: {e}")
        return

    os.makedirs("extracted_pages", exist_ok=True)

    for idx, url in enumerate(urls):
        print(f"\n[{idx + 1}/{len(urls)}] Processing: {url}")
        text: Optional[str] = None

        try:
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
        except Exception as e:
            print(f"Failed to extract content from {url}: {e}")
            continue

        if text:
            try:
                filename = clean_filename(url)
                output_path = os.path.join("extracted_pages", filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"Saved extracted content to: {output_path}")
            except Exception as e:
                print(f"Failed to save content for {url}: {e}")
        else:
            print("No content extracted.")

        time.sleep(2) 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract URLs and content for a person and company."
    )
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
