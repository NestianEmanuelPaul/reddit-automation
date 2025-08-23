import itertools
import httpx

# lista de proxy-uri (poți pune mai multe)
proxies_list = [
    "http://user:pass@123.45.67.89:8080",
    "http://98.76.54.32:3128",
    "https://203.0.113.45:443",
    "socks5://user:pass@198.51.100.23:1080"
]


# Rotează proxy-urile la infinit
proxy_cycle = itertools.cycle(proxies_list)

async def get_next_working_proxy(test_url="https://httpbin.org/ip", timeout=5):
    for _ in range(len(proxies_list)):
        proxy = next(proxy_cycle)
        try:
            async with httpx.AsyncClient(proxies={"http://": proxy, "https://": proxy}, timeout=timeout) as client:
                r = await client.get(test_url)
                if r.status_code == 200:
                    return proxy
        except Exception:
            continue
    return None  # dacă niciun proxy nu merge

