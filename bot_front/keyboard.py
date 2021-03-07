from vkbottle import Text, Keyboard, KeyboardButtonColor

keyboard = Keyboard(one_time=False, inline=False)
keyboard.add(Text("Создать"), color=KeyboardButtonColor.POSITIVE)
keyboard.add(Text("Посмотреть все"))
