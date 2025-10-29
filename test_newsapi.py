import requests

API_KEY = "00e5edc6e9d445b2bb2b2ea0aae0473d"
url = f"https://newsapi.org/v2/top-headlines?country=us&category=technology&apiKey={API_KEY}"
resp = requests.get(url).json()
print(resp)
