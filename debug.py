import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

url = "https://www.snhenaa.pk/collections/henna-stencils"
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Save raw HTML so we can inspect it
with open("page.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Status code:", response.status_code)
print("Page saved to page.html")
print("Page length:", len(response.text))
