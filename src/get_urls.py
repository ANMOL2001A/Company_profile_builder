import os
import requests
from bs4 import BeautifulSoup
import time
import json
from typing import Set, List

from configrations.env import env
from utilities.generate_queries import generate_queries

SCRAPERAPI_KEY = env.scraperapi_key.get_secret_value()


def get_google_results(query: str, num_results: int = 3) -> Set[str]:
    """
    Fetches Google search result URLs for a query via ScraperAPI.

    Args:
        query (str): Search query.
        num_results (int): Number of results to fetch per query.

    Returns:
        Set[str]: A set of result URLs.
    """
    urls: Set[str] = set()
    headers = {"User-Agent": "Mozilla/5.0"}

    url = f"https://www.google.com/search?q={query}&num={num_results}&hl=en"
    scraperapi_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={url}"

    try:
        response = requests.get(scraperapi_url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Google results for query '{query}': {e}")

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        for g in soup.find_all("div", class_="yuRUbf"):
            link = g.find("a")
            if link and link.get("href"):
                urls.add(link["href"])
    except Exception as e:
        raise RuntimeError(f"Error parsing HTML response for query '{query}': {e}")

    return urls


def collect_all_urls(company: str, person: str) -> Set[str]:
    """
    Generates queries and collects all unique URLs.

    Args:
        company (str): Company name.
        person (str): Person name.

    Returns:
        Set[str]: All collected unique URLs.

    """
    try:
        queries: List[str] = generate_queries(company, person)
    except Exception as e:
        raise RuntimeError(f"Failed to generate queries: {e}")

    if not queries:
        raise RuntimeError("No queries generated; cannot proceed.")

    all_results: Set[str] = set()

    for query in queries:
        print(f"\nSearching: {query}")
        try:
            results = get_google_results(query)
        except RuntimeError as e:
            print(f"Skipping query due to error: {e}")
            continue

        for url in results:
            if "linkedin.com/pub/dir" in url:
                continue
            print(url)
            all_results.add(url)

        time.sleep(2)

    if not all_results:
        raise RuntimeError("No URLs collected after processing all queries.")

    return all_results


if __name__ == "__main__":
    company = "Cynoteck Technology Solutions"
    person = "Anmol Sharma"

    try:
        urls = collect_all_urls(company, person)
    except Exception as e:
        print(f" Could not collect URLs: {e}")

    try:
        with open("results.json", "w", encoding="utf-8") as f:
            json.dump(sorted(urls), f, indent=2, ensure_ascii=False)
        print(f"\nTotal unique URLs collected: {len(urls)}")
    except Exception as e:
        print(f"Failed to save results: {e}")
