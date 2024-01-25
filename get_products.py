from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os
import requests
import time
import json
from bs4 import BeautifulSoup

chrome_options = Options()
chrome_options.add_argument('--headless')  # Modo headless
driver = webdriver.Chrome(options=chrome_options)

products_file = open('product_links.json')
data = json.load(products_file)

for product_link in data['products']:
    driver.get(product_link)
    driver.implicitly_wait(10)

    product_data = {}
    product_data['name'] = driver.find_element(By.CLASS_NAME, 'product-name').text
    description = driver.find_element(By.CLASS_NAME, 'description')
    product_data['description'] = driver.execute_script("return arguments[0].innerHTML;", description)
    product_data['category'] = driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/div[1]/ul/li[2]/a').text

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    product_entity = soup.find('script', {'data-component': 'structured-data.page'})
    product_entity_json = json.loads(product_entity.contents[0])
    product_data['entity_data'] = product_entity_json['mainEntity']

    seg = product_link.rstrip('/').split('/')
    product_name = seg[-1]

    if not os.path.exists(f'productos/{product_name}/imagenes'):
        os.makedirs(f'productos/{product_name}/imagenes')


    data_route = os.path.join(f'productos/{product_name}', f'data_{product_name}.json')
    with open(data_route, 'w') as f:
        json.dump(product_data, f)

    div_carrousel = soup.find('div', {'class': 'swiper-wrapper'})
    image_divs = div_carrousel.find_all('div', class_='js-product-slide')
    print(f'-> Producto: {product_name}')
    for i, image in enumerate(image_divs):
        a = image.find('a')
        img_url = a['href']
        img_nombre = f"{product_name}_{i + 1}.webp"
        img_ruta = os.path.join(f'productos/{product_name}/imagenes', img_nombre)

        with open(img_ruta, 'wb') as img_file:
            img_data = requests.get(('https:' + img_url)).content
            img_file.write(img_data)

        print(f"Imagen {i + 1} descargada: {img_ruta}")