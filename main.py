import csv
import json
import time
import undetected_chromedriver as uc 
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.ui import WebDriverWait
from functions import page_down, collect_product_info


def get_products_links(item_name):
    driver = uc.Chrome()
    driver.implicitly_wait(5)

    driver.get(url=f'https://uz.ozon.com/')
    time.sleep(2)

    find_input = driver.find_element(By.NAME, 'text')
    find_input.clear()
    find_input.send_keys(item_name)
    time.sleep(2)

    find_input.send_keys(Keys.ENTER)
    time.sleep(2)
    
    page=1
    for i in range(70):
        current_url = driver.current_url
        parsed_url = urlparse(current_url)
        query_params = parse_qs(parsed_url.query)
        query_params['page'] = page
        updated_query = urlencode(query_params, doseq=True)
        current_url = urlunparse(parsed_url._replace(query=updated_query))
        
        if page == 207 or page == 208:
            page = 210
        else:
            page += 3

        driver.get(url=current_url)
        time.sleep(2)

        # page_down(driver=driver)
        # time.sleep(2)

        try:
            find_links = driver.find_elements(By.CLASS_NAME, 'tile-hover-target')
            products_urls = list(set([f'{link.get_attribute("href")}' for link in find_links]))

            print('[+] Ссылки на товары собраны!')
        except:
            print('[!] Что-то сломалось при сборе ссылок на товары!')

        products_urls_dict = {}

        for k, v in enumerate(products_urls):
            products_urls_dict.update({k: v})

        with open('products_urls_dict.json', 'w', encoding='utf-8') as file:
            json.dump(products_urls_dict, file, indent=4, ensure_ascii=False)

        time.sleep(2)

    products_data = []

    for url in products_urls:
        data = collect_product_info(driver=driver, url=url)
        print(f'[+] Собрал данные товара с id: {data.get("product_id")}')
        time.sleep(2)
        products_data.append(data)

    # with open('PRODUCTS_DATA.json', 'w', encoding='utf-8') as file:
    #     json.dump(products_data, file, indent=4, ensure_ascii=False)

    csv_filename = f'PRODUCTS_DATA_{page}.csv'

    fieldnames = [
        "product_id",
        "product_name",
        "product_ozon_card_price",
        "product_discount_price",
        "product_base_price",
        "product_image",
        "product_category",
        "product_link",
        "product_statistic",
        "product_stars",
        "product_reviews",
    ]

    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for product in products_data:
            writer.writerow(product)

    print(f"Данные успешно сохранены в {csv_filename}")


    driver.close()
    driver.quit()


def main():
    print('[INFO] Сбор данных начался. Пожалуйста ожидайте...')
    item_name = 'IKEA'
    get_products_links(item_name)

    print('[INFO] Работа выполнена успешно!')

if __name__ == '__main__':
    main()
