print("---Else If----")

age = int(input("Вкажіть Ваш вік: "))
# else if - elif
if age<18:
    print("Трошки підрости і можна вчитися на права")
elif age>=18 and age<25:
    print("Ви прозовник, але призвати не можуть :)")
elif age>=25 and age<60:
    print("Чисто можуть призвати на службу")
else:
    print("Ви пенціонер. Живемо і кайфуємо.")


