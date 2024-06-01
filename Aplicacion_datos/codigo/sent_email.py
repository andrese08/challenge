import requests

API_URL = 'http://email-api:5000/api/verificar_y_enviar_emails'

response = requests.post(API_URL)
if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.status_code}")
