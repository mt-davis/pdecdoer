import random
from langchain_openai import ChatOpenAI
import streamlit as st

def simulate_impact_by_zip(documents, user_data, api_key):
    # Add debug print to help identify issues
    print(f"Starting simulation with: ZIP={user_data.get('zip', '')}, API key length={len(api_key) if api_key else 0}")
    
    policy_text = "\n".join([doc.page_content for doc in documents])
    
    # Extract user data
    zip_code = user_data.get("zip", "")
    household_size = user_data.get("household_size", 0)
    income = user_data.get("income", "")
    occupation = user_data.get("occupation", "")
    has_health_insurance = user_data.get("has_health_insurance", False)
    housing_status = user_data.get("housing_status", "")
    
    # More debug info
    print(f"User data extracted: {user_data}")
    
    # In a real application, we would:
    # 1. Call OpenAI to analyze the policy against the user's demographics
    # 2. Get economic data for the ZIP code
    # 3. Generate a personalized impact report
    
    # For now, we'll create a more detailed simulation with mock data
    impact_categories = {
        "Healthcare": random.randint(20, 100),
        "Education": random.randint(10, 80),
        "Employment": random.randint(15, 90),
        "Housing": random.randint(5, 70),
        "Taxes": random.randint(10, 95),
        "Transportation": random.randint(5, 60)
    }
    
    # Generate personalized impact details based on user data
    impact_details = {}
    
    # Healthcare impact details
    if "Healthcare" in impact_categories:
        insurance_status = "having" if has_health_insurance else "not having"
        healthcare_impact = f"As someone {insurance_status} health insurance, this policy could affect your healthcare costs by approximately {impact_categories['Healthcare']}%. "
        if "healthcare" in policy_text.lower() or "medical" in policy_text.lower():
            healthcare_impact += "The policy specifically mentions healthcare provisions that may apply to your situation."
        impact_details["Healthcare"] = healthcare_impact
    
    # Housing impact details
    if "Housing" in impact_categories:
        housing_impact = f"As a {housing_status.lower()}, this policy could affect your housing costs by approximately {impact_categories['Housing']}%. "
        if "housing" in policy_text.lower() or "rent" in policy_text.lower() or "mortgage" in policy_text.lower():
            housing_impact += "The policy contains specific housing provisions that may impact your situation."
        impact_details["Housing"] = housing_impact
    
    # Income/Tax impact details
    if "Taxes" in impact_categories:
        tax_impact = f"Based on your income range of {income}, this policy could affect your tax burden by approximately {impact_categories['Taxes']}%. "
        if "tax" in policy_text.lower() or "income" in policy_text.lower():
            tax_impact += "The policy contains specific tax provisions that may impact your financial situation."
        impact_details["Taxes"] = tax_impact
    
    # Occupation impact details
    if "Employment" in impact_categories:
        employment_impact = f"As someone working in {occupation}, this policy could affect your employment conditions by approximately {impact_categories['Employment']}%. "
        if occupation.lower() in policy_text.lower() or "employment" in policy_text.lower():
            employment_impact += "The policy references your industry specifically."
        impact_details["Employment"] = employment_impact
    
    # Generate personalized summary
    summary = f"Based on your profile (ZIP code {zip_code}, household of {household_size}, income {income}, {occupation} occupation), this policy is predicted to have the most significant impact on your {max(impact_categories, key=impact_categories.get)} costs. "
    
    if "tax" in policy_text.lower() and income == "More than $150,000":
        summary += "As someone in a higher income bracket, you may see larger tax implications. "
    elif "subsidy" in policy_text.lower() and income == "Less than $25,000":
        summary += "You may qualify for subsidies or assistance programs mentioned in this policy. "
    
    if household_size > 4:
        summary += f"With a larger household size of {household_size}, family-oriented provisions in this policy will be particularly relevant to you."

    result = {
        "zip": zip_code,
        "summary": summary,
        "categories": impact_categories,
        "details": impact_details
    }
    
    # Final debug print
    print(f"Simulation complete, returning result with {len(impact_details)} detail categories")
    
    return result
