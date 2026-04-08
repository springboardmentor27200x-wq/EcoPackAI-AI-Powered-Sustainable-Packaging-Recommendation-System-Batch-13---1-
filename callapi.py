import requests

url = "http://127.0.0.1:5000/recommend"

headers = {
    "x-api-key": "ecopack123"
}

data = {
    "product_id": 5
}

res = requests.post(url, json=data, headers=headers)

print(res.json())