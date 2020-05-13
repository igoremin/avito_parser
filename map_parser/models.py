from django.db import models
from django.conf import settings


class MapDetails(models.Model):
    title = models.CharField(max_length=400, verbose_name='Название объявления', blank=True)
    avito_id = models.IntegerField(verbose_name='ID на сайте', blank=True, null=True)
    url = models.TextField(verbose_name='Ссылкуа на объект', blank=True)
    images = models.TextField(verbose_name='Изображения', blank=True)
    metro_distance = models.TextField(verbose_name='Расстояние до метро', blank=True)
    commission = models.CharField(max_length=400, verbose_name='Посредник или владелец', blank=True)
    address = models.CharField(max_length=400, verbose_name='Адресс', blank=True)
    floor = models.IntegerField(verbose_name='Этаж', blank=True, null=True)
    floors_count = models.IntegerField(verbose_name='Этажей в доме', blank=True, null=True)
    house_type = models.CharField(max_length=400, verbose_name='Тип дома', blank=True)
    type = models.CharField(max_length=400, verbose_name='Новый или вторичка', blank=True)
    flat_type = models.CharField(max_length=400, verbose_name='Количество комнат', blank=True)
    area = models.FloatField(verbose_name='Площадь', blank=True, null=True)
    price = models.IntegerField(verbose_name='Цена', blank=True, null=True)
    coords = models.CharField(max_length=400, verbose_name='Координаты', blank=True)
    full_string = models.TextField(verbose_name='Строка ответа', blank=True)

    class Meta:
        verbose_name = 'Объекты'
        verbose_name_plural = 'Объекты полученные из карт'

    def __str__(self):
        return f"{self.title} , id : {self.avito_id}"

    def add_new_row(self, data):
        try:
            self.title = data['title']
        except KeyError:
            pass
        try:
            self.avito_id = data['itemId']
        except KeyError:
            pass
        try:
            self.url = f"https://www.avito.ru{data['url']}"
        except KeyError:
            pass
        self.images = data['images']
        try:
            metro_distance = data['ext']['metro_distance']
            rez = ', '
            rez_arr = []
            with open(f'{settings.BASE_DIR}/map_parser/all_metro_stations.txt', 'r', encoding='utf-8') as metro_file:
                all_metro = {row.split(':')[1].strip(): row.split(':')[0].strip() for row in metro_file.readlines()}
                for key in metro_distance:
                    try:
                        name = all_metro[key]
                        distance = float(metro_distance[key]) * 1000
                        rez_arr.append(f"{name} : {int(distance)}")
                    except Exception as err:
                        print(err)
                rez = rez.join(rez_arr)
                self.metro_distance = rez
        except KeyError:
            pass
        try:
            self.commission = data['ext']['commission']
        except KeyError:
            pass
        try:
            self.address = data['ext']['address']
        except KeyError:
            pass
        try:
            self.floor = data['ext']['floor']
        except KeyError:
            pass
        try:
            self.floors_count = data['ext']['floors_count']
        except KeyError:
            pass
        try:
            self.house_type = data['ext']['house_type']
        except KeyError:
            pass
        try:
            self.type = data['ext']['type']
        except KeyError:
            pass
        try:
            self.flat_type = data['ext']['rooms']
        except KeyError:
            pass
        try:
            area = data['ext']['area']
            self.area = str(area).split(' ')[0]
        except KeyError:
            pass
        try:
            self.price = data['price']
        except KeyError:
            pass
        try:
            self.coords = data['coords']
        except KeyError:
            pass
        self.full_string = data

        self.save()


class Target(models.Model):
    target_value = models.IntegerField(verbose_name='Цель по количеству объектов')
    status = models.BooleanField(verbose_name='Статус парсинга', default=False)

    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цель по количетву объектов'

    def __str__(self):
        return str(self.target_value)


class ProxyIP(models.Model):
    ip = models.CharField(verbose_name='IP адрес', max_length=100, blank=True, null=True)
    port = models.CharField(verbose_name='Порт', max_length=100, blank=True, null=True)
    login = models.CharField(verbose_name='Логин', max_length=100, blank=True, null=True)
    password = models.CharField(verbose_name='Пароль', max_length=100, blank=True, null=True)
    change_ip_url = models.CharField(verbose_name='URL для смены IP', max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = 'Мобильный прокси'
        verbose_name_plural = 'Мобильные прокси'

    def __str__(self):
        return str(f'{self.ip}:{self.port}@{self.login}:{self.password}')


class ResultFile(models.Model):
    result_file = models.FileField(upload_to='results_files/', blank=True, verbose_name='Файл с результатами')

    class Meta:
        verbose_name = 'Итоговый файл'
        verbose_name_plural = 'Файлы с результатами'
        ordering = ['-id']

    def __str__(self):
        return self.result_file.name.split('/')[-1]

    def delete(self, *args, **kwargs):
        if self.result_file:
            self.result_file.delete(False)
        super().delete(*args, **kwargs)
