import httpx

url = "https://gveuivwuilhhwhzjdnvg.supabase.co"
key = "sb_secret_anWk8djfzRHQoxUNnlRhiw_kWjcUE_O"
headers = {
    "apikey": key,
    "Authorization": "Bearer " + key,
    "Content-Type": "application/json",
}

# Try Management API
r = httpx.get(
    "https://api.supabase.com/v1/projects/gveuivwuilhhwhzjdnvg",
    headers=headers,
    timeout=10,
)
print(f"Project info: {r.status_code}")
if r.status_code == 200:
    print(r.json().get("name", ""))
else:
    print(r.text[:300])
