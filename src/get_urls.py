import time
import json
from typing import Set, List

from duckduckgo_search import DDGS
from utilities.generate_queries import generate_queries


def get_duckduckgo_results(query: str, num_results: int = 3) -> Set[str]:
    """
    Fetches DuckDuckGo search result URLs for a query.

    Args:
        query (str): Search query.
        num_results (int): Number of results to fetch.

    Returns:
        Set[str]: A set of result URLs.
    """
    urls: Set[str] = set()

    with DDGS() as ddgs:
        for r in ddgs.text(query):
            href = r.get("href")
            if href:
                urls.add(href)
            if len(urls) >= num_results:
                break

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
            results = get_duckduckgo_results(query)
        except RuntimeError as e:
            print(f"Skipping query due to error: {e}")
            continue

        for url in results:
            if "linkedin.com/pub/dir" in url:
                continue
            print(url)
            all_results.add(url)

        time.sleep(5)

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
