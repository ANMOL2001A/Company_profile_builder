import os
import spacy
import re
import json
from collections import defaultdict

nlp = spacy.load("en_core_web_sm")
EXTRACTED_DIR = "extracted_pages"

CEO_KEYWORDS = ["ceo", "chief executive officer", "founder", "co-founder"]
HQ_KEYWORDS = ["headquarter", "head office", "located in", "based in"]
REVENUE_KEYWORDS = ["revenue", "annual revenue", "turnover", "income"]
EMPLOYEE_KEYWORDS = ["employees", "employee count", "team of"]
FOUNDED_KEYWORDS = ["founded", "established", "since"]
TOOLS_KEYWORDS = ["tools", "technologies", "tech stack", "frameworks", "platforms"]

def contains_keywords(text, keywords):
    text_lower = text.lower()
    return any(k in text_lower for k in keywords)

results = []

for filename in os.listdir(EXTRACTED_DIR):
    if not filename.endswith(".txt"):
        continue

    filepath = os.path.join(EXTRACTED_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"\nProcessing: {filename}")

    doc = nlp(text)

    record = defaultdict(str)
    record["filename"] = filename

    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    if orgs:
        record["company_name"] = orgs[0]  
    gpes = [ent.text for ent in doc.ents if ent.label_ == "GPE"]

    for sent in doc.sents:
        sent_text = sent.text.strip()

        if contains_keywords(sent_text, CEO_KEYWORDS):
            people = [ent.text for ent in sent.ents if ent.label_ == "PERSON"]
            if people:
                record["company_ceo"] = people[0]

        if contains_keywords(sent_text, HQ_KEYWORDS):
            places = [ent.text for ent in sent.ents if ent.label_ == "GPE"]
            if places:
                record["company_headquarter"] = places[0]

        if contains_keywords(sent_text, REVENUE_KEYWORDS):
            money = [ent.text for ent in sent.ents if ent.label_ == "MONEY"]
            if money:
                record["financial_reports"] = f"Revenue: {money[0]}"

        
        if contains_keywords(sent_text, FOUNDED_KEYWORDS):
            dates = [ent.text for ent in sent.ents if ent.label_ == "DATE"]
            if dates:
                record["history"] = f"Founded: {dates[0]}"

        if contains_keywords(sent_text, EMPLOYEE_KEYWORDS):
            numbers = [ent.text for ent in sent.ents if ent.label_ in ["CARDINAL", "QUANTITY"]]
            if numbers:
                record["employee_strength"] = numbers[0]

        if contains_keywords(sent_text, TOOLS_KEYWORDS):
            record["tools_used"] = sent_text

    if not record["company_headquarter"] and gpes:
        record["company_headquarter"] = gpes[0]

    results.append(record)

output_file = "company_profiles.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nExtraction complete. Results saved to: {output_file}")
