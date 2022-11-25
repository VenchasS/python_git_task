import os

print("Выберите что желаете запустить:")
print("1) Формирование exel")
print("2) Формирование графиков")
res = input()
if (int(res) == 1):
    os.system("1.py")
if (int(res) == 2):
    os.system("2.py")
