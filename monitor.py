from apscheduler.schedulers.blocking import BlockingScheduler

from checker import check_url
from db import init_db, save_check

URLS = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/500",
    "https://this-does-not-exist.invalid",
]

def run_checks():
    print("Running checks...")
    for url in URLS: 
        result = check_url(url,slow_ms=4000)
        save_check(result)
        print(f"{url}->{result['result']} ({result['response_ms']})")

if __name__ == "__main__":
    init_db()
    run_checks()

    scheduler = BlockingScheduler()
    scheduler.add_job(run_checks, "interval", seconds=30)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Stopped.")
