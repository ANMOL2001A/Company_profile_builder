from groq import Groq
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
import json
from configrations.env import env

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
        "person": "Tapan pandey",
        "company": "Cynoteck",
        "queries": "\n".join([
            '"Tapan pandey" works at "Cynoteck"',
            '"Tapan pandey" "Cynoteck" profile',
            '"Tapan pandey" "Cynoteck" LinkedIn profile',
            '"Tapan pandey" "Cynoteck" site:linkedin.com',
            '"Tapan pandey" "Cynoteck" site:crunchbase.com',
            '"Tapan pandey" "Cynoteck" site:zoominfo.com',
            '"Tapan pandey" "Cynoteck" site:salesintel.com',
            '"Tapan pandey" site:linkedin.com/in',
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
        "Given a person's name and a company name, create diverse search queries including:\n"
        "- Queries combining the person and company\n"
        "- Queries about the company alone\n\n"
        "Output ONLY the list of queries, one per line, and nothing else."
    ),
    suffix="Person: {person}\nCompany: {company}\nQueries:",
    input_variables=["person", "company"],
    example_separator="\n---\n"
)

def generate_queries(company_name, person_name, output_file=None):
    prompt_text = prompt.format(
        person=person_name.strip(),
        company=company_name.strip()
    )
    
    completion = client.chat.completions.create(
        model=env.model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that generates search queries."
            },
            {
                "role": "user",
                "content": prompt_text
            }
        ],
        temperature=0.3
    )

    raw_output = completion.choices[0].message.content

    queries = []

    for line in raw_output.splitlines():
        if line.strip():
            cleaned = line.strip("- ").strip()
            queries.append(cleaned)

    print("\nGenerated queries:")
    for q in queries:
        print(f"- {q}")

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(queries, f, indent=2, ensure_ascii=False)
        print(f"\nSaved {len(queries)} queries to {output_file}")
    else:
        print("\nNo output file specified; skipping saving.")

    return queries

if __name__ == "__main__":
    generate_queries(
        company_name="Cynoteck",
        person_name="Anmol Sharma",
        output_file="queries.json"
    )
    
    # generate_and_save_queries(
    #     company_name="Cynoteck",
    #     person_name="Anmol Sharma"
    # )
