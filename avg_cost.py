import re
import requests
from tkinter import *
from bs4 import BeautifulSoup
from tkinter.ttk import Combobox
from proj.data import print_models, get_marks_models, data_to_excel, close_excel


class Avg_cost:

    def __init__(self, tab2, wb):
        self.tab = tab2
        self.cars = list(get_marks_models().keys())
        self.wb = wb
        self.header = ["Марка", "Модель", "Год", "Тип двигателя", "Коробка", "Руль", "Привод", "Объём", "Пробег до", "Ср. стоимость"]

        self.prices = []

        # Default
        self.miles = 0
        self.volume = 0
        self.year = 2023
        self.brand = ''
        self.model = ''
        self.fuel_type = 'Бензин'
        self.kpp_type = 'Автомат'
        self.sweel_type = 'Слева'
        self.privod_type = 'Передний'

        
        self.fuel = {'бензин': [1, 9],
                     'дизель': [2, 10],
                     'гибрид': [5, 11],
                     'электричество': [6, 12]}

        self.car_transm = {'механика': [1, 14, 'MT'],
                           'автомат': [2, 13, 'AVTOMAT']}

        self.sweel = {'слева': [1, 'false', 1],
                      'справа': [2, 'true', 2]}

        self.dwheel = {'передний': [1, 15, 'front'],
                       'полный': [2, 17, 'full'],
                       'задний': [3, 16, 'back']}

    def updtcblist(self, model, marka):
        model['values'] = print_models(marka.get())

    def start(self):
        
        Label(self.tab, text='Марка', width=14).grid(row=0)
        marka = Combobox(self.tab, width=45)
        marka['values'] = self.cars
        marka.current(0)
        marka.grid(row=0, column=1)

        
        Label(self.tab, text='Модель', width=14).grid(row=1)
        model = Combobox(self.tab, postcommand=lambda: self.updtcblist(model, marka), width=45)
        model.grid(row=1, column=1)

        
        Label(self.tab, text='Год', width=14).grid(row=2)
        year = Entry(self.tab)
        year.insert(-1, "2023")
        year.grid(row=2, column=1, sticky="ew")

        
        Label(self.tab, text='Тип двигателя', width=14).grid(row=3)
        fuel = Combobox(self.tab, width=45)
        fuel['values'] = list(self.fuel.keys())
        fuel.current(0)
        fuel.grid(row=3, column=1)

        
        Label(self.tab, text='Коробка', width=14).grid(row=4)
        kpp = Combobox(self.tab, width=45)
        kpp['values'] = list(self.car_transm.keys())
        kpp.current(0)
        kpp.grid(row=4, column=1)

        Label(self.tab, text='Руль', width=14).grid(row=5)
        sweel = Combobox(self.tab, width=45)
        sweel['values'] = list(self.sweel.keys())
        sweel.current(0)
        sweel.grid(row=5, column=1)

        Label(self.tab, text='Привод', width=14).grid(row=6)
        dwheel = Combobox(self.tab, width=45)
        dwheel['values'] = list(self.dwheel.keys())
        dwheel.current(0)
        dwheel.grid(row=6, column=1)

        Label(self.tab, text='Объём (л)', width=14).grid(row=7)
        volume = Entry(self.tab)
        volume.insert(-1, "0")
        volume.grid(row=7, column=1, sticky="ew")

        Label(self.tab, text='Пробег (км)', width=14).grid(row=8)
        miles = Entry(self.tab)
        miles.insert(-1, "0")
        miles.grid(row=8, column=1, sticky="ew")

        
        itog = Label(self.tab, text='', width=14, fg='green', font=('Arial', 11, 'normal'))
        itog.grid(row=10, column=0)

        
        Button(self.tab, text='Посчитать', width=10, command=lambda: self.calculate_avg_cost(
            float(miles.get()),
            float(volume.get()),
            float(year.get()),
            marka.get(),
            model.get(),
            fuel.get(),
            kpp.get(),
            sweel.get(),
            dwheel.get(),
            itog
        )).grid(row=10, column=1)

    def calculate_avg_cost(self, miles, volume, year, marka, model, fuel, kpp, sweel, dwheel, itog):
        self.miles = miles
        self.volume = volume
        self.year = year
        self.brand = marka
        self.model = model.split(',')[0]
        self.fuel_type = fuel
        self.kpp_type = kpp
        self.sweel_type = sweel
        self.privod_type = dwheel

        self.kolesa()
        self.mycar()
        self.aster()
        
        link_kolesa = self.kolesa()
        link_mycar = self.mycar()
        link_aster = self.aster()

        links = [link_kolesa, link_mycar, link_aster]
        links_str = "\n".join(str(link) for link in links)

        if len(self.prices)!=0:
            avg_price = sum(self.prices) / float(len(self.prices))
            avg_price_ = format(round(avg_price), ",d").replace(",", " ")
        else:
            avg_price_ = '-'
        itog.configure(text=f'Ср. стоимость:\n{avg_price_}тг')

        arr = [marka, model, year, fuel, kpp, sweel, dwheel, volume, miles, avg_price]
        data_to_excel(arr, self.wb, "Ср. стоимость авто", self.header)

    def kolesa(self):

        try:
            host = f'https://kolesa.kz/cars/{self.brand.lower()}/{self.model.lower()}/?auto-fuel={self.fuel[self.fuel_type.lower()][0]}&auto-car-transm={self.car_transm[self.kpp_type.lower()][0]}&auto-sweel={self.sweel[self.sweel_type.lower()][0]}&car-dwheel={self.dwheel[self.privod_type.lower()][0]}&auto-car-volume[from]={self.volume}&auto-car-volume[to]={self.volume}&year[from]={self.year}&year[to]={self.year}'
            response = requests.get(host)
            soup = BeautifulSoup(response.text, 'html.parser')

            items_soup = soup.find_all(class_='a-card__info')

            for item in items_soup:
                try:
                    desc = item.find('p', class_='a-card__description').text
                    if 'с пробегом' in desc:
                        desc = re.sub("[^0-9]", "", desc[desc.find('пробегом'):desc.find('км')])
                        if int(desc) in range(int(self.miles * 0.9), int(self.miles * 1.1)):
                            item_price = item.find('span', class_='a-card__price').text
                            pr = re.sub("[^0-9]", "", item_price)
                            self.prices.append(int(pr))
                except (ValueError, AttributeError):
                    continue
            return host

        except ConnectionError:
            pass

    def mycar(self):
        try:
            host = f'https://mycar.kz/cars/{self.brand.lower()}/{self.model.lower()}?yearFrom={self.year}&yearTo={self.year}&engineVolumeFrom={self.volume}&engineVolumeTo={self.volume}&gearboxes={self.car_transm[self.kpp_type.lower()][1]}&engines={self.fuel[self.fuel_type.lower()][1]}&drives={self.dwheel[self.privod_type.lower()][1]}&rightHand={self.sweel[self.sweel_type.lower()][1]}'
            response = requests.get(host)
            soup = BeautifulSoup(response.text, 'html.parser')

            items_soup = soup.find_all(class_='min-h-[114px]')
            for item in items_soup:
                try:
                    desc = item.find('div',
                                     class_='car-card__specification gap-x-3 text-inko-50 text-body3 font-medium pt-2').text
                    if 'км' in desc:
                        desc = re.sub("[^0-9]", "", desc[desc.find(' л'):desc.find('км')])
                        if int(desc) in range(int(self.miles * 0.9), int(self.miles * 1.1)):
                            item_price = item.find('h6', class_='text-h6 font-bold text-inko-100').text
                            pr = re.sub("[^0-9]", "", item_price)
                            self.prices.append(int(pr))
                except (ValueError, AttributeError):
                    continue
            return host
        except ConnectionError:
            pass

    def aster(self):
        try:
            host = f'https://aster.kz/cars/{self.brand.lower()}/{self.model.lower()}?yearFrom={self.year}&yearTo={self.year}&transmission={self.car_transm[self.kpp_type.lower()][2]}&transmissionDriveType={self.dwheel[self.privod_type.lower()][2]}&mileageFrom={int(self.miles*0.9)}&mileageTo={int(self.miles*1.1)}&volumeFrom={self.volume}&volumeTo={self.volume}&steering={self.sweel[self.sweel_type.lower()][2]}'

            request = requests.get(host)
            soup = BeautifulSoup(request.text, 'html.parser')

            if soup.find('span', class_='not-found') is None:
                items_soup = soup.find_all(class_='car fadeIn')
                for item in items_soup:
                    try:
                        item_price = item.find('a', class_='px-3 pt-1 price fw-700 f-18 car-link').text
                        pr = re.sub("[^0-9]", "", item_price)
                        self.prices.append(int(pr))
                    except (ValueError, AttributeError):
                        continue
            else:
                pass
            return host
        except ConnectionError:
            pass
