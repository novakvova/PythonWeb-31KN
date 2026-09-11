print("-------Функції за параметрами-------")

def add(x,y):
    return x+y
def sub(x,y):
    return x-y
def mul(x,y):
    return x*y
def div(x,y):
    return x/y

a = float(input("Вкажіть a: "))
b = float(input("Вкажіть b: "))
# передача іменованих параметрів
print(f"{a}+{b}=",add(x=a,y=b))
print(f"{a}-{b}=",sub(a,b))
print(f"{a}*{b}=",mul(a,b))
print(f"{a}/{b}=",div(a,b))

# У функцію можна передавати не визначеню кількість параметрів
def sum(*numbers):
    result = 0
    for n in numbers:
        result += n
    return result

print("Сума чисел (2 6 8 -1 23 67 2 9) ", sum(2,6,8,-1,23,67,2,9))

