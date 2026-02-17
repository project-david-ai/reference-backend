import requests

url = "https://api.hyperbolic.xyz/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJwcmltZS50aGFub3MzMzZAZ21haWwuY29tIiwiaWF0IjoxNzM4NDc2MzgyfQ.4V27eTb-TRwPKcA5zit4pJckoEUEa7kxmHwFEn9kwTQ",
}
data = {
    "messages": [],
    "model": "deepseek-ai/DeepSeek-V3",
    "max_tokens": 512,
    "temperature": 0.1,
    "top_p": 0.9,
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
