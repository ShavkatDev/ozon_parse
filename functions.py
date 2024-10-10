import time as tm
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import re


def page_down(driver):
    driver.execute_script('''
                            const scrollStep = 200; // Размер шага прокрутки (в пикселях)
                            const scrollInterval = 100; // Интервал между шагами (в миллисекундах)

                            const scrollHeight = document.documentElement.scrollHeight;
                            let currentPosition = 0;
                            const interval = setInterval(() => {
                                window.scrollBy(0, scrollStep);
                                currentPosition += scrollStep;

                                if (currentPosition >= scrollHeight) {
                                    clearInterval(interval);
                                }
                            }, scrollInterval);
                        ''')


def collect_product_info(driver, url=''):

    driver.switch_to.new_window('tab')

    tm.sleep(3)
    driver.get(url=url)
    tm.sleep(3)

    # product_id
    try:
        product_id = driver.find_element(
        By.XPATH, '//div[contains(text(), "Артикул: ")]'
        ).text.split('Артикул: ')[1]
    except:
        print(f'[!] Не получилось собрать артикул! [!]\n{page_source}')

    page_source = str(driver.page_source)
    soup = BeautifulSoup(page_source, 'lxml')

    with open(f'product_{product_id}.html', 'w', encoding='utf-8') as file:
        file.write(page_source)

    try:
        product_name = soup.find('div', attrs={"data-widget": 'webProductHeading'}).find(
        'h1').text.strip().replace('\t', '').replace('\n', ' ')
    except:
        print(f'[!] Не получилось собрать название! [!]\n{page_source}')


    # product_id
    # try:
    #     product_id = soup.find('div', string=re.compile(
    #         'Артикул:')).text.split('Артикул: ')[1].strip()
    # except:
    #     product_id = None

    try:
        pattern = r'/product/.*?-(\d+)/'
        artikuls = re.search(pattern, page_source).group(1)
    except:
        print(f'[!] Не получилось собрать артикул! [!]\n{page_source}')

    # product image
    try:
        product_video_div = soup.find('div', class_='kp4_27 k4p_27')
        if not product_video_div:
            product_video_div = soup.find('div', class_='p2k_27 pk3_27')
        product_image = product_video_div.find('img')['src']
    except:
        product_image = None
        
    #product category
    product_category_all = None
    try:
        product_category_div = soup.find('ol', class_='ie8_10 tsBodyControl400Small')
        product_category = product_category_div.find_all('li')

        product_category_all = ''
        for li in product_category:
            if product_category[-1].text == li.text:
                product_category_all += f'{li.text}'
            else:
                product_category_all += f'{li.text} -> '

    except:
        print(f'[!] Не получилось собрать категорию! [!]\n{page_source}')

    # product statistic
    product_stars = None
    product_reviews = None
    product_statistic = None
    try:
        product_statistic = soup.find(
            'div', attrs={"data-widget": 'webSingleProductScore'}).text.strip()

        if " • " in product_statistic:
            product_stars = product_statistic.split(' • ')[0].strip()
            product_reviews = product_statistic.split(' • ')[1].strip()
        else:
            product_statistic = product_statistic
    except:
        product_statistic = None
        product_stars = None
        product_reviews = None

    # product price
    try:
        ozon_card_price_element = soup.find(
            'span', string="c Ozon Картой").parent.find('div').find('span')
        product_ozon_card_price = ozon_card_price_element.text.strip(
        ) if ozon_card_price_element else ''

        price_element = soup.find(
            'span', string="без Ozon Карты").parent.parent.find('div').findAll('span')

        product_discount_price = price_element[0].text.strip(
        ) if price_element[0] else ''
        product_base_price = price_element[1].text.strip(
        ) if price_element[1] is not None else ''
    except:
        product_ozon_card_price = None
        product_discount_price = None
        product_base_price = None

    # product price
    try:
        ozon_card_price_element = soup.find(
            'span', string="c Ozon Картой").parent.find('div').find('span')
    except AttributeError:
        card_price_div = soup.find(
            'div', attrs={"data-widget": "webPrice"}).findAll('span')

        product_base_price = card_price_div[0].text.strip()
        product_discount_price = card_price_div[1].text.strip()

    product_data = (
        {
            'product_id': artikuls,
            'product_name': product_name,
            'product_ozon_card_price': product_ozon_card_price,
            'product_discount_price': product_discount_price,
            'product_base_price': product_base_price,
            'product_image': product_image,
            'product_category': product_category_all,
            'product_link': driver.current_url,
            'product_statistic': product_statistic,
            'product_stars': product_stars,
            'product_reviews': product_reviews,
        }
    )

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return product_data
