import httpx
import time

url="https://httpbin.org/delay/10"

start= time.perf_counter()
response = httpx.get(url,timeout=5)
end= time.perf_counter()

print("Status code:", response.status_code)
print("Time taken:", round((end-start)*1000),"ms")