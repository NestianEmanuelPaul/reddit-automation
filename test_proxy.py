import httpx

proxy_url = "socks5h://aepodqcp:rsbwdel9hpcq@136.0.207.84:6661"  # pune aici exact cum e în config
proxy_url1 = "socks5h://aepodqcp:rsbwdel9hpcq@216.10.27.159:6837"  # pune aici exact cum e în config

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}

try:
    with httpx.Client(proxy=proxy_url, headers=headers, timeout=10) as client:
        r = client.get("https://www.reddit.com/user/spez/about.json")
        print("Status:", r.status_code)
        print("Primele 200 caractere:", r.text[:200])
except Exception as e:
    print("Eroare completă:", repr(e))
