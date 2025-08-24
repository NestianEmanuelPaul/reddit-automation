import itertools
import httpx

proxies_list = [
    "socks5h://aepodqcp:rsbwdel9hpcq@136.0.207.84:6661",
    "socks5h://aepodqcp:rsbwdel9hpcq@216.10.27.159:6837"
]

proxy_cycle = itertools.cycle(proxies_list)

async def get_next_working_proxy(start_proxy=None, test_url="https://httpbin.org/ip", timeout=5):
    # dacă ai primit un start_proxy, începi cu el
    if start_proxy:
        try:
            async with httpx.AsyncClient(proxy=start_proxy, timeout=timeout) as client:
                r = await client.get(test_url)
                if r.status_code == 200:
                    return start_proxy
        except Exception:
            pass

    # dacă nu merge sau nu ai primit, rotești lista
    for _ in range(len(proxies_list)):
        proxy = next(proxy_cycle)
        try:
            async with httpx.AsyncClient(proxy=proxy, timeout=timeout) as client:
                r = await client.get(test_url)
                if r.status_code == 200:
                    return proxy
        except Exception:
            continue
    return None
