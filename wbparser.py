import json
from datetime import date
from os import path
import pandas as pd
import requests
import time

class WildBerriesParser:
    def __init__(self):
        self.headers = {'Accept': "*/*", 'User-Agent': "Chrome/51.0.2704.103 Safari/537.36"}
        self.run_date = date.today()
        self.product_cards = []
        self.directory = path.dirname(__file__)

    def download_current_catalogue(self) -> str:
        local_catalogue_path = path.join(self.directory, 'wb_catalogue.json')
        if (not path.exists(local_catalogue_path) or date.fromtimestamp(int(path.getmtime(local_catalogue_path))) > self.run_date):
            url = ('https://static-basket-01.wb.ru/vol0/data/main-menu-ru-ru-v2.json')
            response = requests.get(url, headers=self.headers).json()
            with open(local_catalogue_path, 'w', encoding='UTF-8') as my_file:
                json.dump(response, my_file, indent=2, ensure_ascii=False)
        return local_catalogue_path

    def traverse_json(self, parent_category: list, flattened_catalogue: list):
        for category in parent_category:
            try:
                flattened_catalogue.append({
                    'name': category['name'],
                    'url': category['url'],
                    'shard': category['shard'],
                    'query': category['query']
                })
            except KeyError:
                continue
            if 'childs' in category:
                self.traverse_json(category['childs'], flattened_catalogue)

    def process_catalogue(self, local_catalogue_path: str) -> list:
        catalogue = []
        try:
            with open(local_catalogue_path, 'r', encoding='UTF-8') as my_file:
                self.traverse_json(json.load(my_file), catalogue)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Ошибка при чтении каталога: {e}")
        return catalogue

    def extract_category_data(self, catalogue: list, user_input: str) -> tuple:
        for category in catalogue:
            if (user_input.split("https://www.wildberries.ru")[-1] == category['url'] or user_input == category['name']):
                return category['name'], category['shard'], category['query']
        return None

    def get_products_on_page(self, page_data: dict) -> list:
        products_on_page = []
        if 'data' in page_data and 'products' in page_data['data']:
            for item in page_data['data']['products']:
                products_on_page.append({
                    'Ссылка': f"https://www.wildberries.ru/catalog/{item['id']}/detail.aspx",
                    'Артикул': item['id'],
                    'Наименование': item['name'],
                    'Бренд': item['brand'],
                    'ID бренда': item['brandId'],
                    'Цена': int(item['priceU'] / 100),
                    'Цена со скидкой': int(item['salePriceU'] / 100),
                    'Рейтинг': item['rating'],
                    'Отзывы': item['feedbacks']
                })
        return products_on_page

    def add_data_from_page(self, url: str):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            page_data = response.json()
            products_on_page = self.get_products_on_page(page_data)
            if len(products_on_page) > 0:
                self.product_cards.extend(products_on_page)
                print(f"Добавлено товаров: {len(products_on_page)}")
            else:
                print('Загрузка товаров завершена')
                return True
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"Ошибка при декодировании JSON: {e}")
            with open('error_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            return False

    def get_all_products_in_category(self, category_data: tuple):
        for page in range(1, 10):
            print(f"Загружаю товары со страницы {page}")
            url = (f"https://catalog.wb.ru/catalog/{category_data[1]}/catalog?appType=1&{category_data[2]}&curr=rub&dest=-1257786&page={page}&sort=popular&spp=24")
            if self.add_data_from_page(url):
                break
            time.sleep(1)  # Пауза между запросами для уменьшения нагрузки на сервер

    def get_sales_data(self):
        for card in self.product_cards:
            url = (f"https://product-order-qnt.wildberries.ru/by-nm/?nm={card['Артикул']}")
            try:
                response = requests.get(url, headers=self.headers).json()
                if response:
                    card['Продано'] = response[0]['qnt']
                else:
                    card['Продано'] = 0
            except requests.ConnectTimeout:
                card['Продано'] = 'нет данных'
            print(f"Собрано карточек: {self.product_cards.index(card) + 1} из {len(self.product_cards)}")

    def save_to_excel(self, file_name: str) -> str:
        data = pd.DataFrame(self.product_cards)
        result_path = (f"{path.join(self.directory, file_name)}_{self.run_date.strftime('%Y-%m-%d')}.xlsx")
        writer = pd.ExcelWriter(result_path)
        data.to_excel(writer, 'data', index=False)
        writer.close()
        return result_path

    def get_all_products_in_search_result(self, key_word: str):
        for page in range(1, 101):
            print(f"Загружаю товары со страницы {page}")
            url = (f"https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&curr=rub&dest=-1257786&page={page}&query={'%20'.join(key_word.split())}&resultset=catalog&sort=popular&spp=24&suppressSpellcheck=false")
            if self.add_data_from_page(url):
                break

    def run_parser(self):
        instructons = """Введите 1 для парсинга категории целиком, 2 — по ключевым словам: """
        mode = input(instructons)
        if mode == '1':
            local_catalogue_path = self.download_current_catalogue()
            print(f"Каталог сохранен: {local_catalogue_path}")
            processed_catalogue = self.process_catalogue(local_catalogue_path)
            input_category = input("Введите название категории или ссылку: ")
            category_data = self.extract_category_data(processed_catalogue, input_category)
            if category_data is None:
                print("Категория не найдена")
            else:
                print(f"Найдена категория: {category_data[0]}")
                self.get_all_products_in_category(category_data)
                self.get_sales_data()
                print(f"Данные сохранены в {self.save_to_excel(category_data[0])}")
        if mode == '2':
            key_word = input("Введите запрос для поиска: ")
            self.get_all_products_in_search_result(key_word)
            self.get_sales_data()
            print(f"Данные сохранены в {self.save_to_excel(key_word)}")

if __name__ == '__main__':
    app = WildBerriesParser()
    app.run_parser()
