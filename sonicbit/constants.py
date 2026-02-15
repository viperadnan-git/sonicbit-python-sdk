class Constants:
    API_DOMAIN = "v6.sonicbit.net"
    API_ORIGIN = "https://my.sonicbit.net"
    API_REFERER = "https://my.sonicbit.net/"
    API_BASE_URL = f"https://{API_DOMAIN}/api"

    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"

    API_HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-IN,en-GB;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Host": API_DOMAIN,
        "Origin": API_ORIGIN,
        "Referer": API_REFERER,
        "User-Agent": USER_AGENT,
    }
