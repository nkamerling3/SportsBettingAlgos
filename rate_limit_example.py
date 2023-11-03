import requests
import time

# Define the URL you want to request
url = 'https://google.com/'

# Number of requests to make
num_requests = 10

# Time interval (in seconds) between requests
request_interval = 5
current_request = 1

for _ in range(num_requests):
    response = requests.get(url)

    if response.status_code == 200:  # Check if the request was successful
        print(f"Request {current_request} successful")
        current_request += 1
    else:
        print(f"Request {num_requests + 1} failed with status code {response.status_code}")

    # Wait for the specified interval before making the next request
    time.sleep(request_interval)