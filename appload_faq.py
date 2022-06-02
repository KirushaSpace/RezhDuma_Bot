import json
import requests

response = requests.get('http://51.250.111.89:8080/api/appeals/popular')
faq = open('faq.json', 'w')
json.dump(response.json(), faq)
faq.close()