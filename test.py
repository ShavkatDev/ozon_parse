import json

with open('products_urls_dict.json', 'r', encoding='utf-8') as file:
    data_json = json.load(file)

for number, url in data_json.items():
    print(url)