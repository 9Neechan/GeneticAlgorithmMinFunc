import random
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd
import matplotlib.pyplot as plt

INPUT_FUNS = ["(x - 2)**4 + (x - 2*y)**2"]


# ------------------------------------algorithm-realisation-------------------------------------------------------------
def func(x, y):
    return eval(INPUT_FUNS[0])  # (x - 2)**4 + (x - 2*y)**2


def generate_initial_population(size, start, end):
    population = []
    for i in range(size):
        x = random.uniform(start, end)
        y = random.uniform(start, end)
        it = [x, y, func(x, y)]
        population.append(it)
    return population


def crossover(parent1, parent2):
    child1 = [parent1[0], parent2[1], func(parent1[0], parent2[1])]
    child2 = [parent2[0], parent1[1], func(parent2[0], parent1[1])]
    return child1, child2


def mutate(child):
    x = child[0]
    y = child[1]
    if random.random() > 0.5:
        x += random.uniform(-0.5, 0.5)
    else:
        y += random.uniform(-0.5, 0.5)
    return [x, y, func(x, y)]


def genetic_algorithm(num_generations, population_size, start, end):
    dataForTable = []
    snapshot_arr = []
    # Генерируем исходную популяцию
    population = generate_initial_population(population_size, start, end)

    for i in range(num_generations):
        for _ in range(population_size):
            # Производим новых потомков с мутирующими генами
            parent1 = random.choice(population)
            parent2 = random.choice(population)
            child1, child2 = crossover(parent1, parent2)
            child1 = mutate(child1)
            child2 = mutate(child2)
            population.append(child1)
            population.append(child2)

        # Отбираем лучших из поколения
        population = sorted(population, key=lambda z: z[2])
        population = population[:population_size]
        # записываем данные для изуализации таблицы
        dataForTable.append(population[0])

        # Отрисовка и сохранение графика
        x = list(map(lambda x: x[0], population))
        y = list(map(lambda x: x[1], population))
        snapshot_name = f"pictures/g{i}.png"
        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.suptitle(f"Номер поколения: {i}")
        ax2.set_xlabel("значения функции")
        ax2.plot(x, y, 'go')
        ax2.set_xlim(start, end)
        ax2.set_ylim(start, end)
        ax1.set_xlabel("значения функции вблизи")
        ax1.plot(x, y, 'go')
        plt.savefig(snapshot_name, dpi=70, bbox_inches='tight')
        plt.close()
        snapshot_arr.append(snapshot_name)

    # Сохраняем таблицу
    data = pd.DataFrame(dataForTable)
    data.columns = ['X', 'Y', 'Наименьшее значение F(x,y)']

    return population[0], data


#-------------------------------img-and-table-frames-logic--------------------------------------------------------------
class ShowResult:
    def __init__(self, data):
        # Счётчик для изображений
        self.i = 0
        self.max_i = int(num_generations.item.get()) - 1
        # Рамка для наших изображений
        self.canvas = Canvas(frame_btn, width=420, height=345, borderwidth=2)

        # Добавим 1-ое изображение
        self.photo = None
        self.show_img()

        # Кнопки для перелистывания изображений
        self.button_next = ttk.Button(frame_btn, text="Далее", command=self.next_img, state=NORMAL)
        self.button_next.grid(row=1, column=1)
        self.button_back = ttk.Button(frame_btn, text="Назад", command=self.previous_img, state=DISABLED)
        self.button_back.grid(row=1, column=0)

        # Выведем таблицу
        self.data = data
        self.show_table()

    def next_img(self) -> None:
        self.i += 1
        self.button_back['state'] = NORMAL
        self.show_img()
        if self.i == self.max_i:
            self.button_next['state'] = DISABLED

    def previous_img(self) -> None:
        self.i -= 1
        self.button_next['state'] = NORMAL
        self.show_img()
        if self.i == 0:
            self.button_back['state'] = DISABLED

    def show_img(self):
        self.photo = ImageTk.PhotoImage(Image.open("pictures/g{0}.png".format(self.i)))
        self.canvas.create_image(3, 3, anchor='nw', image=self.photo)
        self.canvas.grid(column=0, row=0, columnspan=2)

    def show_table(self) -> None:
        # Создаем виджет таблицы
        treeview = ttk.Treeview(frame_scroll, columns=list(self.data.columns), show='headings')
        treeview.pack(side=LEFT, fill=BOTH, expand=1)
        # Добавляем колонки в таблицу
        for col in self.data.columns:
            treeview.heading(col, text=col)
        # Добавляем строки в таблицу и заполняем значения ячеек данными из дата-фрейма
        for i, row in self.data.iterrows():
            treeview.insert('', END, values=list(row))
        # Создаем scrollbar widget и добавляем его в таблицу
        scrollbar = ttk.Scrollbar(frame_scroll, orient=VERTICAL, command=treeview.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        treeview.configure(yscrollcommand=scrollbar.set)


#------------------------------------------------buttons-logic----------------------------------------------------------

def checkButtonState(*args) -> None:
    """ Кнопка активируется когда все атрибуты input введены """
    if num_generations.item.get() and population_size.item.get() and start.item.get() and end.item.get() and combobox:
        btn_start['state'] = NORMAL
    else:
        btn_start['state'] = DISABLED
    if num_generations.item.get() or population_size.item.get() or start.item.get() or end.item.get() or combobox:
        btn_clean['state'] = NORMAL


def clickButton() -> None:
    """ По нажатию кнопки производятся расчёты """
    btn_start['state'] = DISABLED
    xy_bestScore, data = genetic_algorithm(population_size=int(population_size.item.get()),
                                           num_generations=int(num_generations.item.get()),
                                           start=min(int(start.item.get()), int(end.item.get())),
                                           end=max(int(start.item.get()), int(end.item.get())))

    # Перед тем как сгенерировать новые виджеты, удалим старые
    for widget in frame_input.winfo_children():
        if widget.winfo_name() == "result_label":
            widget.destroy()
    for widget in frame_btn.winfo_children():
        widget.destroy()
    for widget in frame_scroll.winfo_children():
        widget.destroy()

    # Создаём новые
    ShowResult(data)
    text = "x={0} y={1}; \n Наименьшее значение F(x,y): {2}".format(xy_bestScore[0], xy_bestScore[1], xy_bestScore[2])
    Label(frame_input, text=text, fg='green', font=('Arial', 10), name="result_label").pack()


def cleanButton() -> None:
    """ По нажатию кнопки удаляем старые данные """
    population_size.item.delete(0, END)
    num_generations.item.delete(0, END)
    start.item.delete(0, END)
    end.item.delete(0, END)
    combobox.set('')
    for widget in frame_input.winfo_children():
        if widget.winfo_name() == "result_label":
            widget.destroy()
    for widget in frame_btn.winfo_children():
        widget.destroy()
    for widget in frame_scroll.winfo_children():
        widget.destroy()


#---------------------------------------user-input----------------------------------------------------------------------

class UserInput:
    """ Класс определяющий шаблон для атрибутов ввода tkinter """

    def __init__(self, text, from_, to, increment, initial_value):
        # Текстовые переменные tkinter
        self.var = StringVar()  # текст вводимый пользователем
        self.var.set(initial_value)

        # Определяем структуру объекта ввода
        Label(frame_input, text=text).pack()
        self.item = ttk.Spinbox(frame_input, validate='key', textvariable=self.var,
                                from_=from_, to=to, increment=increment)
        self.item.pack()
        self.var.trace('w', checkButtonState)

#-------------------------------------------------UI--------------------------------------------------------------------

# Создаётся окно пользователя
root_window = Tk()
root_window.title("GENETIC ALGORITHM")
root_window.geometry('1000x660')

# Создание фреймов и настройка их свойств
frame_input = Frame(root_window, bd=3, relief=GROOVE)
Label(frame_input, text="ГЕНЕТИЧЕСКИЙ АЛГОРИТМ", font=('Arial', 16)).pack(pady=10)
frame_input.grid(column=0, row=0, rowspan=2, sticky='NSEW')

frame_img = LabelFrame(root_window, bd=3, relief=GROOVE, text="Графики")
frame_img.grid(column=1, row=0, sticky='NSEW')

frame_table = LabelFrame(root_window, bd=3, relief=GROOVE, text="Таблица")
frame_table.grid(column=1, row=1, sticky='NSEW')
# Дополнительные мини-фреймы
frame_btn = Frame(frame_img)
frame_btn.pack(fill=BOTH, expand=1)
frame_scroll = Frame(frame_table)
frame_scroll.pack(fill=BOTH, expand=1)

# Задание параметров для столбцов и строк
root_window.columnconfigure(0, weight=1)
root_window.columnconfigure(1, weight=4)
root_window.rowconfigure(0, weight=1)
root_window.rowconfigure(1, weight=1)

# Ввод функции которую мы хотим исследовать
Label(frame_input, text="Целевая функция:").pack()
var_txt = StringVar()
combobox = ttk.Combobox(frame_input, textvariable=var_txt)
combobox['values'] = INPUT_FUNS
combobox['state'] = 'readonly'
combobox.pack(padx=5, pady=5)
var_txt.trace('w', checkButtonState)

# Ввод данных
population_size = UserInput(text="Размер популяции первого поколения:", initial_value="10", from_=2, to=999, increment=1)
num_generations = UserInput(text="Количество поколений:", initial_value="10", from_=1, to=999, increment=1)
start = UserInput(text="Нижняя граница диапазона поиска:", initial_value="-5", from_=-99999, to=99999, increment=1)
end = UserInput(text="Верхняя граница диапазона поиска:", initial_value="5", from_=-99999, to=99999, increment=1)

# Запуск программы
btn_start = ttk.Button(frame_input, text="Рассчитать", command=clickButton, state=DISABLED)
btn_start.pack(padx=5, pady=5)

# Очистить старые значения
btn_clean = ttk.Button(frame_input, text="Очистить", command=cleanButton, state=DISABLED)
btn_clean.pack(padx=5, pady=5)

root_window.mainloop()

"""
https://www.tutorialspoint.com/execute_matplotlib_online.php 

import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, projection='3d')

x, y = np.meshgrid(np.linspace(-5, 5, 10), np.linspace(-5, 5, 10))
z = (x - 2)**4 + (x - 2*y)**2

ax.plot_surface(x, y, z)
plt.show()
"""