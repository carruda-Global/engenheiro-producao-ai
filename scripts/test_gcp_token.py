import httpx, json

token = "ya29.a0AT3oNZ8Z7vnnPBPLraibWIN5NQWJM1yf82o4c7t5uGJa1BamDEtb2k2umgBdF3gxbqSHNu9liFs0kDc0h2LA0_sYHV0SqyU4IK19C4Cycdz3ew3dRr83wGsEtePl5Wq7wUhHPt383T_5XzGkRBFrSR2zeB8Cs43MuQ6UlMhvI3EP8ZDVveirq0rOs1wQT4LQ-WYbWW0aCgYKAc8SARISFQHGX2Mi9JQLm-6GJ2t8zampRa0eGA0206"
headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}

r = httpx.get("https://oauth2.googleapis.com/tokeninfo?access_token=" + token, timeout=10)
print(f"Token info: {r.status_code}")
if r.status_code == 200:
    info = r.json()
    print(f"Email: {info.get('email', 'N/A')}")
    print(f"Scopes: {info.get('scope', 'N/A')}")

r2 = httpx.get(
    "https://cloudresourcemanager.googleapis.com/v1/projects/global-engenharia-498823",
    headers=headers,
    timeout=10,
)
print(f"\nProject: {r2.status_code}")
if r2.status_code == 200:
    print(json.dumps(r2.json(), indent=2)[:300])
else:
    print(r2.text[:300])
