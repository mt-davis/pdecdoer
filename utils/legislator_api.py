import requests

def fetch_legislator_info(name, api_key):
    headers = {"X-API-Key": api_key}
    base_url = "https://api.propublica.org/congress/v1/members.json"

    res = requests.get(base_url, headers=headers)
    if res.status_code != 200:
        return None

    members = res.json().get("results", [])[0].get("members", [])
    match = next((m for m in members if name.lower() in f"{m['first_name']} {m['last_name']}".lower()), None)

    if not match:
        return None

    member_id = match["id"]
    profile_url = f"https://api.propublica.org/congress/v1/members/{member_id}.json"
    votes_url = f"https://api.propublica.org/congress/v1/members/{member_id}/votes.json"

    profile_res = requests.get(profile_url, headers=headers).json()
    votes_res = requests.get(votes_url, headers=headers).json()

    bio = profile_res.get("results", [{}])[0].get("roles", [{}])[0].get("committees", [])
    vote_data = votes_res.get("results", [{}])[0].get("votes", [])

    return {
        "name": f"{match['first_name']} {match['last_name']}",
        "party": match["party"],
        "state": match["state"],
        "district": match.get("district", "At-Large"),
        "bio": ", ".join([c.get("name", "") for c in bio]),
        "votes": [f"{v['date']} - {v['description']}" for v in vote_data[:5]]
    }
