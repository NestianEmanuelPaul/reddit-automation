from itertools import cycle

# lista de proxy-uri (poți pune mai multe)
proxy_list = [
    "socks5://127.0.0.1:9050",
    # "socks5://IP:PORT", ...
]

proxy_pool = cycle(proxy_list)

def get_proxy():
    proxy = next(proxy_pool)
    return {"http": proxy, "https": proxy}
