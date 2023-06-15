import os
import openpyxl
from tkinter import *
from tkinter.ttk import Notebook, Frame
from iznos import Iznos
from avg_cost import Avg_cost
from proj.data import close_excel
from proj.remont import Remont
from pathlib import Path


def quit(wb, window):
    file_path = close_excel(wb)
    window.destroy()
    os.system(file_path)


def run_tkinter(wb):
    # Tkinter settings
    window = Tk()
    window.title("Application (passenger cars)")
    window.geometry('660x300')

    # Tabs
    tab_control = Notebook(window)
    tab1 = Frame(tab_control)
    tab2 = Frame(tab_control)
    tab3 = Frame(tab_control)
    tab_control.add(tab1, text='Физ износ')
    tab_control.add(tab2, text='Ср. стоимость ТС')
    tab_control.add(tab3, text='Стоимость ремонта')

    tab_control.pack(expand=1, fill='both')

    iznos = Iznos(tab1, wb)
    iznos.start()

    avg_cost = Avg_cost(tab2, wb)
    avg_cost.start()

    remont = Remont(tab3, wb)
    remont.start()

    Button(window, text="Завершить", command=lambda: quit(wb, window)).pack()

    window.mainloop()


if __name__ == '__main__':
    wb = openpyxl.Workbook()
    run_tkinter(wb)
