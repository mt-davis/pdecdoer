import random

def simulate_impact_by_zip(documents, zip_code, api_key):
    policy_text = "\n".join([doc.page_content for doc in documents])

    # Placeholder logic for now
    categories = {
        "Healthcare": random.randint(20, 100),
        "Education": random.randint(10, 80),
        "Employment": random.randint(15, 90),
        "Housing": random.randint(5, 70)
    }

    summary = f"This bill is predicted to significantly affect ZIP code {zip_code} in areas such as healthcare, education, and employment."

    return {
        "zip": zip_code,
        "summary": summary,
        "categories": categories
    }
