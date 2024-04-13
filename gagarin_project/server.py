import requests 

res = requests.post("http://127.0.0.1:3000/api/courses/1")
print(res.json())

