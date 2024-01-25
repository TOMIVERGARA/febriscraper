from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import json
from bs4 import BeautifulSoup
driver = webdriver.Chrome()


startingUrl = "https://www.febriiluminacion.com/productos/"

driver.get(startingUrl)
driver.implicitly_wait(20)

def load_more_items():
    while True:
        try:
             # Scroll hasta el final de la página
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Esperar un breve momento para que se carguen los nuevos elementos (puedes ajustar el tiempo según tus necesidades)
            time.sleep(1)
            # Buscar el botón "Cargar más" por su clase
            load_more_buton = driver.find_element(By.CLASS_NAME, 'js-load-more-btn')
            
            # Hacer clic en el botón
            driver.execute_script("arguments[0].click();", load_more_buton)
            # Esperar un breve momento para que se carguen los nuevos elementos (puedes ajustar el tiempo según tus necesidades)
            print('Loading more items...')
        except:
            # Si no se encuentra el botón, salir del bucle
            print('Finished loading items.')
            time.sleep(5)
            break

load_more_items()
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
div_items = soup.find_all('div', class_='item')
product_links = []

for div_item in div_items:
    div1 = div_item.find('div', {'class': 'p-relative overflow-none'})
    div2 = div1.find('div')
    href = div2.find('a')

    if href:
        link = href['href']
        product_links.append(link)


print(f'-> A total of {len(product_links)} product links were captured.')

with open('product_links.json', 'w') as f:
    json.dump({'product_total': len(product_links), 'products': product_links}, f)