import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import math


def get_input(
    location, choice
):  # функция преобразует входные текстовые данные в два списка со значениями поля и магнитного момента
    input_data = open(location, "r")
    if choice:
        field, moment = get_text_LakeShore_VSM(input_data)
    else:
        field, moment = get_text_simple_VSM(input_data)
    input_data.close()
    return field, moment


def get_text_LakeShore_VSM(
    input_data,
):  # функция обрабатывает текстовый файл полученный с вибрационного магнитометра LakeShore
    field = []
    moment = []
    data = list(map(str.strip, input_data.readlines()))
    for i in range(len(data)):
        data[i] = data[i].replace(",", ".")
    ind = data.index("Field(Oe)\t Moment(emu)")
    del data[: ind + 1]
    data = [i for i in data if i]
    for s in data:
        field.append(float(s.split()[0]))
        moment.append(float(s.split()[1]))
    return field, moment


def get_text_simple_VSM(
    input_data,
):  # функция обрабатывает текстовый файл полученный с простого вибрационного магнитометра, где файл состоит только из столбцов с данными
    try:
        if mass.get() == 0:
            show_input_data_error()
        else:
            field = []
            moment = []
            data = list(map(str.strip, input_data.readlines()))
            for i in range(len(data)):
                data[i] = data[i].replace(",", ".")
            data = [i for i in data if i]
            for s in data:
                field.append(float(s.split()[0]) * 1000)
                moment.append(float(s.split()[1]) * float(mass.get()))
            return field, moment
    except tk.TclError:
        check_correct_input()


def plot_graph(x, y):  # функция строит график по полученным и обработанным данным
    plt.figure()
    plt.plot(x, y, color="black", marker="o", markersize=4)
    plt.xlabel("Field, Oe")
    plt.ylabel("Moment, emu")
    plt.title("Петля гистерезиса исследуемого образца moment(H)")
    plt.show()


def run_program_plot():  # функция выполняет запуск программы, передавая в фунции параметры, введенные пользователем
    location = file_path.get()
    choice_VSM = True if enabled_lakeshore.get() == 1 else False
    field, moment = get_input(location, choice_VSM)
    plot_graph(field, moment)


def get_file_path():  # функция выполняет записть пути к файлу в нужном для Python формате
    path = filedialog.askopenfile()
    file_path.set(path.name)


def replot_with_other_axes():  # функция перестраивает петлю гистерезиса из осей M(H) в оси B(H)
    location = file_path.get()
    choice_VSM = True if enabled_lakeshore.get() == 1 else False
    x, y = get_input(location, choice_VSM)
    y1 = []
    try:
        if density.get() == 0:
            show_input_data_error()
        else:
            try:
                for i in range(len(x)):
                    y1.append(
                        x[i] + 4 * math.pi * y[i] / mass.get() * density.get()
                    )  # mass, density прочитать при вводе
                plt.figure()
                plt.plot(x, y1, color="black", marker="o", markersize=4)
                plt.xlabel("Field, Oe")
                plt.ylabel("B, G")
                plt.title("Петля гистерезиса исследуемого образца B(H)")
                plt.show()
            except ZeroDivisionError:
                show_input_data_error()
    except tk.TclError:
        check_correct_input()


def count_Hc():  # функция вычисляет коэрцитивную силу
    location = file_path.get()
    choice_VSM = True if enabled_lakeshore.get() == 1 else False
    x, y = get_input(location, choice_VSM)
    may_be_Hc = []
    for i in range(1, len(x) - 1):  # исключаем первую точку, в которой поле мб равно 0
        if y[i] * y[i + 1] <= 0:  # смена знака намагниченности
            if y[i] == 0:
                may_be_Hc.append(math.fabs(x[i]))
            elif y[i + 1] == 0:
                may_be_Hc.append(math.fabs(x[i + 1]))
            else:
                may_be_Hc.append(math.fabs(x[i] + x[i + 1]) / 2)
    Hc = round(max(may_be_Hc), 2)
    result_Hc.set(f"Hc = {str(Hc)} Oe")


def count_Mr_Br():  # функция вычисляет остаточную намагниченность и остаточную индукцию путём домножения на 4пи
    location = file_path.get()
    choice_VSM = True if enabled_lakeshore.get() == 1 else False
    x, y = get_input(location, choice_VSM)
    may_be_Mr = []
    for i in range(len(x) - 1):
        if x[i] * x[i + 1] <= 0:  # смена знака поля
            if x[i] == 0:
                may_be_Mr.append(math.fabs(y[i]))
            elif x[i + 1] == 0:
                may_be_Mr.append(math.fabs(y[i + 1]))
            else:
                may_be_Mr.append(math.fabs(y[i] + y[i + 1]) / 2)
    Mr = max(  # допустим, возьмем максимальную остачу, отрицательную либо положительную
        may_be_Mr
    )
    Br = round_to(Mr * 4 * math.pi, 3)
    Mr = round_to(Mr, 3)
    result_Mr.set(f"Mr = {str(Mr)} emu")
    result_Br.set(f"Br = {str(Br)} G")


def round_to(num, digits):  # округление до нужного числа значащих цифр
    if num - int(num) == 0:  # целое число
        return num
    else:
        decimal_const = math.floor(math.log10(num))
        a = round(num * 10**-decimal_const, digits - 1)  # промежуточное число
        b = int(a * 10 ** (digits - 1))
        return b * 10 ** (decimal_const - digits + 1)


def show_input_data_error():  # выдает ошибку если пользователь ошибся при вводе
    messagebox.showerror(
        title="Ошибка",
        message="Проверьте корректность введенных массы и плотности",
    )


def check_correct_input():  # функция позволяет вводить десятичные числа через запятую
    messagebox.showerror(
        title="Ошибка",
        message="Вводить десятичные числа необходимо через точку",
    )


root = tk.Tk()  # создаем окно интерфейса и задаем его внешний вид
root.title("Приложение для обработки измерительных данных вибрационного магнитометра")
root.geometry("1300x720")
root.resizable(True, True)
root.minsize(720, 720)
root.maxsize(1920, 1080)

# далее создаем кнопки для пользовательского интерфейса

btn_plot1 = tk.Button(
    text="Построить график moment(H)", width=50, command=run_program_plot
)
btn_plot1.grid(row=3, column=0)

btn_Hc = tk.Button(text="Рассчитать Hc", width=50, command=count_Hc)
btn_Hc.grid(row=5, column=0)

btn_Mr = tk.Button(text="Рассчитать Mr и Br", width=50, command=count_Mr_Br)
btn_Mr.grid(row=6, column=0)

btn_plot2 = tk.Button(
    text="Построить график B(H)", width=50, command=replot_with_other_axes
)
btn_plot2.grid(row=4, column=0)

file_path = tk.StringVar()
btn_path = tk.Button(text="Открыть файл", width=50, command=get_file_path)
btn_path.grid(row=0, column=1)

enabled_lakeshore = tk.IntVar()
enabled_checkbutton = tk.Checkbutton(text="LakeShoreVSM", variable=enabled_lakeshore)
enabled_checkbutton.grid(row=1, column=1)

# создаем поля для ввода массы и плотности

mass = tk.DoubleVar()
entry_mass = tk.Entry(textvariable=mass, width=50)
entry_mass.grid(row=2, column=1)

density = tk.DoubleVar()
entry_density = tk.Entry(textvariable=density, width=50)
entry_density.grid(row=2, column=2)

# создаем текстовые метки для отображения информации с инструкциями и реззультатов вычислений и переменные, которые их хранят

label_path = tk.Label(
    text="Выберите файл с данными для обработки",
    font=("Arial", 16),
)
label_path.grid(row=0, column=0)

label_choose_VSM = tk.Label(
    text="Поставьте галочку, если использовали LakeShoreVSM: ",
    font=("Arial", 16),
)
label_choose_VSM.grid(row=1, column=0)

label_entry = tk.Label(
    text="Введите массу в граммах(слева) и плотность в г/см^3(справа)",
    font=("Arial", 16),
)
label_entry.grid(row=2, column=0)

result_Hc = tk.StringVar()
label_Hc = tk.Label(
    textvariable=result_Hc,
    font=("Arial", 16),
)
label_Hc.grid(row=5, column=1)

result_Mr = tk.StringVar()
label_Mr = tk.Label(
    textvariable=result_Mr,
    font=("Arial", 16),
)
label_Mr.grid(row=6, column=1)

result_Br = tk.StringVar()
label_Br = tk.Label(
    textvariable=result_Br,
    font=("Arial", 16),
)
label_Br.grid(row=7, column=1)

root.mainloop()
