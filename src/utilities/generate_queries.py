import json
import random
from groq import Groq
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from configrations.env import env
from utilities.temprature_enums import TemperatureLevel
from faker import Faker
faker = Faker()


client = Groq(api_key=env.groq_api_key.get_secret_value())

examples = [
    {
        "person": "Anmol Sharma",
        "company": "Cynoteck",
        "queries": "\n".join([
            '"Anmol Sharma" works at "Cynoteck"',
            '"Anmol Sharma" "Cynoteck" profile',
            '"Anmol Sharma" "Cynoteck" LinkedIn',
            '"Anmol Sharma" "Cynoteck" site:linkedin.com',
            '"Anmol Sharma" "Cynoteck" site:crunchbase.com',
            '"Anmol Sharma" "Cynoteck" site:zoominfo.com',
            '"Anmol Sharma" site:linkedin.com/in',
            '"Cynoteck" profile',
            '"Cynoteck" overview',
            '"Cynoteck" revenue investors team',
            '"Cynoteck" financials',
            '"Cynoteck" employee strength history',
            '"Cynoteck" site:linkedin.com',
            '"Cynoteck" site:crunchbase.com',
            '"Cynoteck" site:salesintel.io',
            '"Cynoteck" site:zoominfo.com'
        ])
    },
    {
        "person": "Elon Musk",
        "company": "SpaceX",
        "queries": "\n".join([
            '"Elon Musk" "SpaceX" profile',
            '"Elon Musk" "SpaceX" leadership',
            '"Elon Musk" "SpaceX" interviews',
            '"Elon Musk" "SpaceX" site:linkedin.com',
            '"Elon Musk" "SpaceX" site:businessinsider.com',
            '"Elon Musk" "SpaceX" site:forbes.com',
            '"SpaceX" company overview',
            '"SpaceX" financials',
            '"SpaceX" investors',
            '"SpaceX" employee reviews site:glassdoor.com',
            '"SpaceX" site:linkedin.com',
            '"SpaceX" site:crunchbase.com',
            '"SpaceX" site:zoominfo.com',
            '"SpaceX" site:reuters.com',
            '"SpaceX" site:techcrunch.com'
        ])
    }
]

example_prompt = PromptTemplate(
    input_variables=["person", "company", "queries"],
    template=(
        "Person: {person}\n"
        "Company: {company}\n"
        "Queries:\n{queries}"
    )
)

prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix=(
        "You are a query generation assistant.\n"
        "Given a person's name and a company name, create diverse, high-quality search queries that help find:\n"
        "- Information connecting the person to the company (such as employment details, profiles, etc.).\n"
        "- Information about the company itself, including its business overview, leadership, ceo, headquarters, financials, news coverage, and other relevant details.\n\n"
        "Guidelines:\n"
        "- For combined queries (person + company), include variations that mention both names together in different ways.\n"
        "- For company-only queries, cover multiple aspects such as company profile, financials, leadership team, growth, investments, and public information.\n"
        "- Use a variety of search operators and reputable sources similar to those shown in the examples (e.g., LinkedIn, Crunchbase, Zoominfo, Business Insider, Glassdoor, company websites, etc.).\n\n"
        "Output ONLY the list of queries, one query per line, and nothing else."
    ),
    suffix="Person: {person}\nCompany: {company}\nQueries:",
    input_variables=["person", "company"],
    example_separator="\n---\n"
)

def generate_queries(company_name, person_name, temperature=TemperatureLevel.LEVEL_0_3):
    prompt_text = prompt.format(
        person=person_name.strip(),
        company=company_name.strip()
    )
    completion = client.chat.completions.create(
        model=env.model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise and reliable assistant specializing in generating diverse search queries "
                    "for finding information about professionals and companies."
                )
            },
            {
                "role": "user",
                "content": prompt_text
            }
        ],
        temperature=temperature
    )

    raw_output = completion.choices[0].message.content
    queries = []
    for line in raw_output.splitlines():
        if line.strip():
            cleaned = line.strip("- ").strip()
            queries.append(cleaned)
    return queries


if __name__ == "__main__":
    all_results = []
    for i in range(30):
        person = faker.name()
        company = faker.company()
        print(f"\nGenerating queries for: {person} @ {company}")
        queries = generate_queries(company, person)
        all_results.append({
            "person": person,
            "company": company,
            "queries": queries
        })

    output_file = "bulk_queries.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(all_results)} query sets to {output_file}")
