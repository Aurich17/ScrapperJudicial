import requests

session = requests.Session()

url = "LOGIN_URL"

payload = {
    "usuario": "xxx",
    "password": "xxx"
}

response = session.post(url, data=payload)

print(response.status_code)
print(response.text)