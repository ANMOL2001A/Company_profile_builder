from googlesearch import search
import time


def generate_search_queries(company_name, person_name):
    queries = []

    company = company_name.strip()
    person = person_name.strip()

    queries.extend([
        f'"{person}""{company}"',
        f'"{person}""{company}" profile',
        f'"{person}""{company}" LinkedIn',
        f'"{person}""{company}" site:linkedin.com',
        f'"{person}""{company}" site:crunchbase.com',
        f'"{person}""{company}" site:salesintel.io',
        f'"{person}""{company}" site:zoominfo.com',
        f'"{person}" site:linkedin.com/in'
    ])

    queries.extend([
        f'"{company}" profile',
        f'"{company}" overview',
        f'"{company}" revenue investors team',
        f'"{company}" financials',
        f'"{company}" employee strength history',
        f'"{company}" site:linkedin.com',
        f'"{company}" site:crunchbase.com',
        f'"{company}" site:salesintel.io',
        f'"{company}" site:zoominfo.com'
    ])

    return queries

def collect_urls(company, person, num_results=3, delay=2.0):
    queries = generate_search_queries(company, person)
    all_urls = set()

    for query in queries:
        print(f"\n Searching for: {query}")
        try:
            results = search(query, num_results=num_results, lang="en")
            for url in results:
                print(url)
                all_urls.add(url)
        except Exception as e:
            print(f" Error for query '{query}': {e}")
        time.sleep(delay)  

    return all_urls

if __name__ == '__main__':
    company_name = "cynoteck pvt. limited"
    person_name = "Anmol Sharma"

    print("Collecting search result URLs...\n")
    urls = collect_urls(company_name, person_name)
    with open("results.txt", "w") as f:
        for url in urls:
            f.write(url + "\n")

    print(f"\n Total unique URLs collected: {len(urls)}")
