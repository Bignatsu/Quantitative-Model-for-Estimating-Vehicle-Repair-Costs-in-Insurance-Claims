import re
import math
import requests
from tkinter import *
from bs4 import BeautifulSoup
from datetime import datetime
from tkinter.ttk import Combobox
from proj.data import get_marks_models, print_models, get_class_auto, get_car_details, get_material_price, \
    get_norm_chas, get_a_b_L0_ML, data_to_excel, close_excel


class Remont:
    
    def __init__(self, tab3, wb):
        self.tab = tab3
        self.wb = wb
        self.header = ['Марка', 'Модель', 'Класс', 'Год', 'Пробег', 'Вид работы', 'Часть', 'Деталь', 'Площадь', 'Время', 'Норм часы', 'Стоимость']
        self.cars_list = list(get_marks_models().keys())
        self.class_auto_list = list(get_class_auto().keys())
        self.car_details_list = list(get_car_details().keys())

    def updtcblist(self, model, marka):
        model['values'] = print_models(marka.get())

    def updtcblist_v2(self, detail_v2, detail_v1):
        detail_v2['values'] = get_car_details()[detail_v1.get()]
    
    def start(self):
        Label(self.tab, text='Марка').grid(row=1, column=0)
        Label(self.tab, text='Модель').grid(row=2, column=0)
        Label(self.tab, text='Класс').grid(row=3, column=0)
        Label(self.tab, text='Год').grid(row=4, column=0)
        Label(self.tab, text='Пробег').grid(row=5, column=0)
        Label(self.tab, text='Вид работы').grid(row=6, column=0)
    
        marka = Combobox(self.tab, width=45)
        marka['values'] = self.cars_list
        marka.current(0)
        marka.grid(row=1, column=1)
    
        # Выбор модель машины
        model = Combobox(self.tab, width=45)
        model = Combobox(self.tab, postcommand=lambda: self.updtcblist(model, marka), width=45)
        model.grid(row=2, column=1)

        # Класс
        class_auto = Combobox(self.tab, width=45)
        class_auto['values'] = self.class_auto_list
        class_auto.current(0)
        class_auto.grid(row=3, column=1)

        # Год
        year = Entry(self.tab)
        year.insert(-1, "2023")
        year.grid(row=4, column=1, sticky="ew")

        # Пробег
        probeg = Entry(self.tab)
        probeg.insert(-1, "0")
        probeg.grid(row=5, column=1, sticky="ew")

        # Вид работы
        vid = Combobox(self.tab, width=45)
        vid['values'] = ['Малярные', 'Снятие/Установка', 'Разборка/Сборка', 'Замена']
        vid.current(0)
        vid.grid(row=6, column=1)
    
        Label(self.tab, text='Часть').grid(row=1, column=2)
        Label(self.tab, text='Деталь').grid(row=2, column=2)
        Label(self.tab, text='Площадь (м^2)').grid(row=3, column=2)
        Label(self.tab, text='Время (часы)').grid(row=4, column=2)
        Label(self.tab, text='Норм-час (тг)').grid(row=5, column=2)

        # Часть
        detail_v1 = Combobox(self.tab, width=30)
        detail_v1['values'] = self.car_details_list
        detail_v1.current(0)
        detail_v1.grid(row=1, column=3)

        # Наименование агрегата, узла, детали
        detail_v2 = Combobox(self.tab, width=30)
        detail_v2 = Combobox(self.tab, postcommand=lambda: self.updtcblist_v2(detail_v2, detail_v1), width=30)
        detail_v2.grid(row=2, column=3)

        # Площадь
        plowad = Entry(self.tab)
        plowad.insert(-1, "0")
        plowad.grid(row=3, column=3, sticky="ew")

        # Время
        vremya = Entry(self.tab)
        vremya.insert(-1, "0")
        vremya.grid(row=4, column=3, sticky="ew")

        # Норм часы
        norm_chas = Entry(self.tab)
        norm_chas.insert(-1, "0")
        norm_chas.grid(row=5, column=3, sticky="ew")

        # Итог
        itog = Label(self.tab, text='', width=12, fg='green', font=('Arial', 11, 'normal'))
        itog.grid(row=7, column=3, sticky="ew")

        # Кнопка рассчета
        Button(self.tab, text='Посчитать', width=15, command=lambda: self.calculate(
            marka.get(),
            model.get(),
            class_auto.get(),
            float(year.get()),
            float(probeg.get()),
            vid.get(),
            detail_v1.get(),
            detail_v2.get(),
            float(plowad.get()),
            float(vremya.get()),
            float(norm_chas.get()),
            itog
        )).grid(row=7, column=1)

    def calculate(self, marka, model, class_auto, year, probeg, vid, detail_v1, detail_v2, plowad, vremya, norm_chas, itog):

        # если Норм час = 0, высчитываем сами по классу авто, году и мрп
        if norm_chas == 0:
            norm_chas = get_norm_chas(class_auto, year)

        if vid == "Малярные":
            info = self.malar_work(plowad, vremya, norm_chas)

        if vid == "Снятие/Установка":
            info = self.snyatie_razborka_work(vremya, norm_chas, detail_v2, vid, plowad)

        if vid == "Разборка/Сборка":
            info = self.snyatie_razborka_work(vremya, norm_chas, detail_v2, vid, plowad)

        if vid == "Замена":
            info = self.zamena_work(vremya, norm_chas, marka, model.split(',')[0], detail_v2, vid, year, probeg)

        print(marka, model, class_auto, year, probeg, vid, detail_v1, detail_v2, plowad, vremya, norm_chas)
        itog.configure(text=info[0])

        arr = [marka, model, class_auto, year, probeg, vid, detail_v1, detail_v2, plowad, vremya, norm_chas]
        arr += info[1:]
        data_to_excel(arr, self.wb, "Ремонт", self.header)

    def malar_work(self, plowad, vremya, norm_chas):
        material_price = get_material_price()

        price = material_price * plowad
        price += vremya * norm_chas
        msg = f"Малярные работы.\nОбщая стоимость:\n{round(price)}"
        return [msg, price]

    def get_fiz_iznos(self, year, marka, probeg):
        currentYear = datetime.now().year
        srok = currentYear - year

        # Find coeeficients
        info = get_a_b_L0_ML(marka)
        coeff_a_out = float(info["coeff_a"])
        coeff_b_out = float(info["coeff_b"])

        # Рассчет пробега если он 0
        if probeg == 0:
            Lo_out = float(info["Lo"])
            ML_out = float(info["ML"])
            probeg = Lo_out * (srok ** ML_out)

        omega = (coeff_a_out * srok) + (coeff_b_out * probeg)

        fiz_iznnos = 100 * (1 - (math.e ** (-1 * omega)))
        if fiz_iznnos > 75:
            fiz_iznnos = fiz_iznnos % 75

        return fiz_iznnos

    def snyatie_razborka_work(self, vremya, norm_chas, detail_v2, vid, plowad):
        price = vremya * norm_chas

        material_price = get_material_price()
        price += material_price * plowad

        msg = f"{detail_v2}\n{vid.lower()}\nОбщая стоимость\n{round(price)}"
        return [msg, price]

    def zamena_work(self, vremya, norm_chas, brand, model, search, vid, year, probeg):
        price = vremya * norm_chas

        prices = []

        # Ищем в kolesa.kz
        try:
            search_str = search.lower().strip().replace(' ', '+')

            host = f'https://kolesa.kz/zapchasti/prodazha/{brand.lower()}/{model.lower()}/?_txt_={search_str}&spare-condition=2&has-delivery=1&find-in-text=0'

            request1 = requests.get(host)
            soup1 = BeautifulSoup(request1.text, 'html.parser')

            for i in soup1.find_all(class_='a-card__title'):
                request2 = requests.get('https://kolesa.kz' + i.find('a', class_='a-card__link')['href'])  # item_link
                soup2 = BeautifulSoup(request2.text, 'html.parser')

                p = re.sub("[^0-9]", "", soup2.find('div', class_='offer__price').text)
                prices.append(int(p))

            zapchast_price = sum(prices) / len(prices)

            # Если срок авто больше 7 лет
            if (year - datetime.now().year) >= 7:
                zapchast_price = zapchast_price * (1 - (self.get_fiz_iznos(year, brand, probeg)/100))

            price += zapchast_price

            msg = f"{search} {vid.lower()}\nОбщая стоимость\n{round(price)}тг\nс учетом детали"
            return [msg, price, "с учетом детали", host]

        # если мы не находим деталь на сайте
        except:
            msg = f"{search} замена\nОбщая стоимость:\n{round(price)}\nбез учета детали\n(деталь не найдена)"
            return [msg, price, "без учета детали"]
