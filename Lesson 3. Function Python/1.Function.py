print("--Привіт! Ми вивчаємо функції.--")

def printInfo():
    print("Сьогодні дуже класна погода :)")
# Виклик фукнції у Python
printInfo()

def carInfo():
    def myCar(): # Локальна функція доступна в межах блоку коду
        print("Renault Megan")
    def myGirlCar(): # Локальна функція доступна в межах блоку коду
        print("Жигулі 6")
    myCar()
    myGirlCar()

carInfo()