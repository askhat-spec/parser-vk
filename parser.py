import requests
from bs4 import BeautifulSoup as bs
import csv
from fake_useragent import UserAgent
import time
import csv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

# Функция для скроллинга страницы
def scroll(driver, timeout):
    scroll_pause_time = timeout
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(scroll_pause_time)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# Взятие всех ссылок на странице
def get_all_links(url):
    options = Options()
    options.set_preference('permissions.default.image', 2)
    options.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', False)
    driver = webdriver.Firefox(options=options ,executable_path='./geckodriver')
    driver.implicitly_wait(45)
    driver.get(url)
    scroll(driver, 10)
    soup = bs(driver.page_source, 'lxml')
    driver.close()

    divs = soup.find('div', attrs = {'class':'author_page_articles'}).find_all('a')
    links = []
    for div in divs:
        a = div.get('href')
        a = 'https://vk.com' + a
        links.append(a)
    
    return links


def get_html(url):
    user_agent = UserAgent()
    user = user_agent.random
    headers = {'User-Agent': str(user)}
    r = requests.get(url, headers=headers)
    return r.text


def get_data(html):
    soup = bs(html, "lxml")
    try:
        title = soup.find('h1').text
    except:
        title = ''

    try:
        lines = soup.find_all('p')
        article = '\n'.join([line.text for line in lines])
    except:
        name = ''

    try:
        imgs = soup.find_all('img')
        image_urls = ''
        a = 1
        for i in imgs:
            image = f"imageURL{a}: {i.get('src')} \n"
            image_urls += image
            a += 1
    except:
        image_urls = ''

    data = [title, article, image_urls]
    print(title, 'parsed')
    return data


if __name__ == "__main__":
    url = 'https://vk.com/@yvkurse'
    all_links = get_all_links(url)
    all_data = []
    for link in all_links:
        all_data.append(get_data(get_html(link)))

    names = ['Заголовок', 'Статья', 'Изображении']

    FILENAME = "result.csv"
    with open(FILENAME, "a", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter = ';')
        writer.writerow(names)
        for data in all_data:
            writer.writerow(data)