page = 3
link_lenght = len(f'&page={page}')
current_url = f'https://uz.ozon.com/search/?brand=74301437&from_global=true&text=IKEA&page=3'

print(current_url[:len(current_url)-link_lenght])