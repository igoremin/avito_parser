import requests
import time
import datetime
import random
import os
from django.conf import settings
from .models import MapDetails, Target, ProxyFile, ResultFile
from json import JSONDecodeError
from math import ceil
from openpyxl import Workbook
from openpyxl.styles import NamedStyle, Font, Border, Side, Alignment, colors
from openpyxl.utils.exceptions import IllegalCharacterError


def get_headers():
    with open(f'{settings.MEDIA_DIR}/user-agents/user_agents_for_chrome_pk.txt') as u_a:
        user_agent = random.choice([row.strip() for row in u_a.readlines()])
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                  'q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru,ru-RU;q=0.9,kk-RU;q=0.8,kk;q=0.7,uz-RU;q=0.6,uz;q=0.5,en-RU;q=0.4,en-US;q=0.3,en;q=0.2',
        'connection': '0',
        'cache-control': 'max-age=0',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-Agent': user_agent
    }
    return headers


def load_data(proxies, all_price, proxy=False):
    status = Target.objects.all()[0].status
    if status is False:
        return False
    else:
        price = all_price.get_new_value()
        if price is not False:
            page = 1
            data = get_json(
                min_price=price[0], max_price=price[1],
                page=page, use_proxy=proxy, proxies=proxies
            )
            all_count = 0
            if data is not False:
                target = int(data['count'])
                page_target = ceil(target/20)
                count = get_data_from_json(data)
                all_count += count
                while True:
                    if settings.DEBUG:
                        print(f'Target : {target}, done : {all_count}, page : {page}, page_target : {page_target}, '
                              f'min price : {price[0]}, max price : {price[1]}')
                    if page > 250 or page >= page_target:
                        break
                    page += 1
                    new_data = get_json(
                        min_price=price[0], max_price=price[1],
                        page=page, use_proxy=proxy, proxies=proxies
                    )
                    if new_data is not False:
                        count = get_data_from_json(new_data)
                        all_count += count
                        if all_count >= target or page >= page_target:
                            if settings.DEBUG:
                                print(f'Target : {target}, done : {all_count}, page : {page}, '
                                      f'page_target : {page_target}, min price : {price[0]}, max price : {price[1]}\n')
                            break
                    else:
                        break
        else:
            return False


def get_json(min_price, max_price, page, use_proxy, proxies):
    step = 0
    while step < 10:
        time.sleep(random.uniform(0.5, 3.5))
        url = 'https://www.avito.ru/js/v2/map/items'
        params = {'categoryId': '24', 'locationId': '637640', 'correctorMode': '1', 'page': page, 'map': 'e30=',
                  'params[201]': '1059', 'viewPort[width]': '1404', 'viewPort[height]': '510', 'limit': '20',
                  'priceMin': min_price, 'priceMax': max_price}
        check_proxy = 'NOT'
        if use_proxy is False:
            try:
                request = requests.get(url=url, params=params, headers=get_headers())
            except Exception as err:
                print(err)
                request = False
        else:
            try:
                proxy = proxies.get_new_proxy()[0]
                request = requests.get(url=url, params=params, headers=get_headers(), proxies=proxy)
                check_proxy = requests.get('https://check-host.net/ip', headers=get_headers(), proxies=proxy).text
            except Exception as err:
                print(err)
                request = False

        if request is not False:
            try:
                data = request.json()
            except JSONDecodeError:
                print(f'DECODE ERROR, IP : {check_proxy}')
            else:
                return data
        step += 1
    return False


def get_data_from_json(js_data):
    k = 0
    for item in js_data['items']:
        new_row = MapDetails()
        new_row.add_new_row(item)
        k += 1
    return k


def get_target_value():
    url = 'https://www.avito.ru/js/v2/map/items'
    params = {'categoryId': '24', 'locationId': '637640', 'correctorMode': '1', 'page': '1', 'map': 'e30=',
              'params[201]': '1059', 'viewPort[width]': '1404', 'viewPort[height]': '510', 'limit': '20'}
    request = requests.get(url=url, params=params, headers=get_headers())
    if request.status_code == 200:
        data = request.json()
        target_value = data['count']
        Target.objects.all().delete()
        new_target = Target(
            target_value=int(target_value),
            status=True
        )
        new_target.save()
        return True
    else:
        print(f'ERROR GET TARGET VALUE. STATUS CODE : {request.status_code}')
        return False


def change_status():
    try:
        target = Target.objects.all()[0]
        target.status = False
        target.save()
    except IndexError:
        pass


class AllPriseValues:
    def __init__(self):
        self.all_price = [0, 2000000]
        for _ in range(0, 800):
            self.all_price.append(self.all_price[-1] + 50000)

        for _ in range(0, 120):
            self.all_price.append(self.all_price[-1] + 500000)

        self.price_list = ([self.all_price[i-1] + 1, self.all_price[i]] for i in range(1, len(self.all_price)))

    def get_new_value(self):
        try:
            return next(self.price_list)
        except StopIteration:
            return False


class Proxy:
    def __init__(self):
        try:
            self.file = ProxyFile.objects.all()[0].proxy_file.path
        except IndexError:
            self.file = False

        if self.file:
            with open(f'{self.file}', 'r', encoding='utf-8') as proxy_file:
                all_proxies = [row.strip() for row in proxy_file.readlines()]
                self.proxies = sorted(all_proxies, key=lambda *args: random.random())

            self.block_proxies = []

    def get_new_proxy(self):
        new_proxy = False
        k = 0
        while new_proxy is False or k < len(self.proxies):
            new_proxy = self.proxies.pop(0).split(':')
            if new_proxy not in self.block_proxies:
                break
            else:
                new_proxy = False
                k += 1
        if new_proxy is not False:
            ip, port, login, password = new_proxy[0], new_proxy[1], new_proxy[2], new_proxy[3]

            proxy_setting = {
                "http": f"http://{login}:{password}@{ip}:{port}",
                "https": f"https://{login}:{password}@{ip}:{port}"
            }

            if len(self.proxies) < 1 and self.file is not False:
                with open(f'{self.file}', 'r', encoding='utf-8') as proxy_file:
                    all_proxies = [row.strip() for row in proxy_file.readlines()]
                    not_block_proxies = []
                    for p in all_proxies:
                        if p not in self.block_proxies:
                            not_block_proxies.append(p)

                    self.proxies = sorted(not_block_proxies, key=lambda *args: random.random())
            return proxy_setting, new_proxy
        else:
            return False

    def add_block_proxy(self, block_proxy):
        self.block_proxies.append(f"{block_proxy[0]}:{block_proxy[1]}:{block_proxy[2]}:{block_proxy[3]}")


def start(use_proxy=False):
    if get_target_value() is True:
        all_price = AllPriseValues()
        proxies = Proxy()
        while True:
            if load_data(proxy=use_proxy, proxies=proxies, all_price=all_price) is False:
                break

    change_status()


def write_results_xlsx_file():
    print('WRITE')

    file_name = f'{datetime.datetime.today().strftime("%d-%m-%Y_%H-%M")}.xlsx'

    wb = Workbook()

    sheet = wb['Sheet']
    wb.remove(sheet)

    wb.create_sheet('Результаты')
    sheet = wb['Результаты']

    sheet.column_dimensions['A'].width = 30
    sheet.column_dimensions['B'].width = 50
    sheet.column_dimensions['C'].width = 30
    sheet.column_dimensions['D'].width = 30
    sheet.column_dimensions['E'].width = 30
    sheet.column_dimensions['F'].width = 30
    sheet.column_dimensions['G'].width = 30
    sheet.column_dimensions['H'].width = 50
    sheet.column_dimensions['I'].width = 100
    sheet.column_dimensions['J'].width = 30
    sheet.column_dimensions['K'].width = 30
    sheet.column_dimensions['L'].width = 30
    sheet.column_dimensions['M'].width = 30
    sheet.column_dimensions['N'].width = 50
    sheet.column_dimensions['O'].width = 30
    sheet.column_dimensions['P'].width = 150

    search_results = MapDetails.objects.all()

    header = NamedStyle(name="header")
    header.font = Font(bold=True, color=colors.RED, size=15)
    header.border = Border(bottom=Side(border_style="thin"))
    header.alignment = Alignment(horizontal="center", vertical="center")
    sheet.append(['Название', 'Адресс', 'Тип дома', 'Цена', 'Площадь', 'Этаж', 'Всего этажей', 'Продавец',
                  'Расстояние до метро', 'ID', 'URL', 'Новый или вторичка', 'Количество комнат', 'Изображения',
                  'Координаты', 'Строка ответа'])

    header_row = sheet[1]
    for cell in header_row:
        cell.style = header

    r = 0
    for result in search_results:

        data = [result.title, result.address, result.house_type, result.price, result.area, result.floor,
                result.floors_count, result.commission, result.metro_distance, result.avito_id, result.url,
                result.type, result.flat_type, result.images, result.coords, result.full_string]

        try:
            sheet.append(data)
            r += 1

        except IllegalCharacterError:
            pass

    path = os.path.join(settings.BASE_DIR, f'media/results_files/')
    if os.path.isdir(path) is False:
        os.makedirs(path, mode=0o777)

    wb.save(f'{path}/{file_name}')

    new_file = ResultFile()
    new_file.result_file = f'results_files/{file_name}'
    new_file.save()
