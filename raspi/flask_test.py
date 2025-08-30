import requests
response = requests.get("http://192.168.1.100:5000/")
print(response.text)
