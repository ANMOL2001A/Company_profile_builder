import os
import requests
from bs4 import BeautifulSoup
import time
import json
from configrations.env import env
from utilities.generate_queries import generate_queries
SCRAPERAPI_KEY = env.scraperapi_key.get_secret_value()


def get_google_results(query, num_results=3):
    urls = set()
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    url = f"https://www.google.com/search?q={query}&num={num_results}&hl=en"

    scraperapi_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={url}"

    try:
        response = requests.get(scraperapi_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for g in soup.find_all('div', class_='yuRUbf'):
            link = g.find('a')
            if link and link['href']:
                urls.add(link['href'])

    except Exception as e:
        print(f" Error while fetching: {query} occors {e}")

    return urls

def collect_all_urls(company, person):
    queries = generate_queries(company, person)
    all_results = set()

    for query in queries:
        print(f"\nSearching: {query}")
        results = get_google_results(query)
        for url in results:
            if "linkedin.com/pub/dir" in url:
                continue
            print(url)
            all_results.add(url)
        time.sleep(2)

    return all_results


if __name__ == "__main__":
    company = "Cynoteck Technology Solutions"
    person = "Anmol sharma"
    urls = collect_all_urls(company, person)
    with open("results.json", "w") as f:
        json.dump(list(urls), f, indent=2)
    print(f"\n Total unique URLs collected: {len(urls)}")