class Constants:
    """SonicBit API constants (2026-11 platform: my.sonicbit.net).

    The legacy ``v6.sonicbit.net`` API was retired; all endpoints now live on
    the web app origin. The API is protected by TLS-fingerprint filtering —
    non-browser TLS stacks (plain httpx/requests/curl) receive
    ``403 {"msg": "This app isn't supported..."}`` — so every request MUST go
    through a curl_cffi session with browser impersonation.
    """

    API_ORIGIN = "https://my.sonicbit.net"
    API_BASE_URL = f"{API_ORIGIN}/api"
    FILES_BASE_URL = "https://files.sonicbit.net/dl"

    # curl_cffi impersonation target used for every request (see module docstring).
    IMPERSONATE = "chrome136"

    # Impersonation already sends browser-like Accept/UA headers; only the
    # same-origin web-app headers are added explicitly.
    API_HEADERS = {
        "Origin": API_ORIGIN,
        "Referer": f"{API_ORIGIN}/",
    }

    # Session cookie set by /auth/login and required by every other endpoint.
    SESSION_COOKIE = "sb_jwt"
