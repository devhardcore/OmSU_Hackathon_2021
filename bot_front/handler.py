import json
import os

from vkbottle import Keyboard, Text, EMPTY_KEYBOARD
from vkbottle.bot import Bot, Message
from vkbottle_types import BaseStateGroup

from backend.backend import push_event, eventbrite_service, get_organization_id, get_all_events
from bot_front.entity import EventCreate
from bot_front.keyboard import keyboard
from bot_front.utils import event_to_str

bot = Bot(os.environ["VK_TOKEN"])


class CreateStates(BaseStateGroup):
    NAME_STATE = 0
    DESCRIPTION_STATE = 1
    COUNT_STATE = 2
    START_TIME_STATE = 3
    END_TIME_STATE = 4


@bot.on.message(text=["!start", "start", "help", "!help", "привет", "Привет", "Начать", "начать", "Старт", "старт"])
async def greeting(message: Message):
    await message.answer(message="Ниже появились кнопки. Ты можешь выбрать: 'Создать' или 'Посмотреть все'",
                         keyboard=keyboard.get_json())


@bot.on.message(text=["!create", "!создать", "Создать"])
async def create_event(message: Message):
    event = EventCreate()
    await bot.state_dispenser.set(message.peer_id, CreateStates.NAME_STATE, obj=event)
    await message.answer(message="Введите название вашего мероприятия", keyboard=EMPTY_KEYBOARD)


@bot.on.message(state=CreateStates.NAME_STATE)
async def name_handler(message: Message):
    event: EventCreate = message.state_peer.payload.get("obj")
    event.name = message.text
    await bot.state_dispenser.set(message.peer_id, CreateStates.DESCRIPTION_STATE, obj=event)
    return "Введите описание мероприятия (до 140 символов)"


@bot.on.message(state=CreateStates.DESCRIPTION_STATE)
async def summary_handler(message: Message):
    event: EventCreate = message.state_peer.payload.get("obj")
    event.summary = message.text
    await message.answer(
        message="Выберите количество человек: 1-10, 10-30, >30",
        keyboard=(
            Keyboard(one_time=False, inline=False)
                .add(Text("1-10", payload={"count": 5}))
                .add(Text("10-30", payload={"count": 25}))
                .add(Text(">30", payload={"count": 50}))
        ).get_json()
    )
    await bot.state_dispenser.set(message.peer_id, CreateStates.COUNT_STATE, obj=event)


@bot.on.message(state=CreateStates.COUNT_STATE)
async def count_handler(message: Message):
    event: EventCreate = message.state_peer.payload.get("obj")
    data = json.loads(message.payload)
    event.count = int(data.get("count", 1))
    await bot.state_dispenser.set(message.peer_id, CreateStates.START_TIME_STATE, obj=event)
    await message.answer(message="Введите время начала мероприятия в формате: 31-12-2022 18:56",
                         keyboard=EMPTY_KEYBOARD)


@bot.on.message(state=CreateStates.START_TIME_STATE)
async def start_handler(message: Message):
    event: EventCreate = message.state_peer.payload.get("obj")
    event.start = message.text
    await bot.state_dispenser.set(message.peer_id, CreateStates.END_TIME_STATE, obj=event)
    return "Введите время конца мероприятия в формате: 31-12-2022 18:56"


@bot.on.message(state=CreateStates.END_TIME_STATE)
async def end_handler(message: Message):
    event: EventCreate = message.state_peer.payload.get("obj")
    event.end = message.text
    await bot.state_dispenser.delete(message.peer_id)
    await message.answer(message=f"Спасибо. Ваше событие было опубликовано!", keyboard=keyboard.get_json())
    push_event(eventbrite_service, event.name, event.start, event.end, event.summary, event.count)


@bot.on.message(text=["!show", "!show all", "!показать", "показать", "список", "Посмотреть все"])
async def show_all(message: Message):
    try:
        await bot.state_dispenser.delete(message.peer_id)
    except Exception as e:
        pass

    organization_id = get_organization_id(eventbrite_service)
    return "\n\n".join([event_to_str(event) for event in get_all_events(eventbrite_service, organization_id)]) \
           or "Пусто!"
