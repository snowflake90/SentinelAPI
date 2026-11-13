import httpx
import time

def check_url(url, timeout=5, slow_ms=4000):
    """Check one URL and return a dictionary describing the result."""
    start=time.perf_counter()
    status_code = None
    error = None

    try:
        response = httpx.get(url, timeout=timeout)
        status_code = response.status_code
        if status_code >= 400:
            error = f"HTTP {status_code}"
    except httpx.TimeoutException:
        error = "timeout"
    except httpx.HTTPError:
        error="connection error"

    response_ms=round((time.perf_counter()-start)*1000)

    if error:
        result = "down"
    elif response_ms > slow_ms:
        result = "slow"
    else:
        result = "healthy"

    return{
        "url": url,
        "status_code": status_code,
        "response_ms": response_ms,
        "result": result,
        "error": error
    }

if __name__=="__main__":
    test_urls=[
        "https://httpbin.org/status/200",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/status/500",
        "https://httpbin.org/delay/10",
        "https://this-does-not-exist.invalid"
    ]
    for u in test_urls:
        print(check_url(u))