from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.deep_linking import decode_payload
from aiogram.types import Message
from aiogram.utils.deep_linking import get_start_link

import settings
import DB
import pay

storage = MemoryStorage()
tmp_add = {}


class MyStates(StatesGroup):
    admin_send_price = State()
    admin_send_preview = State()
    admin_send_content = State()


API_TOKEN = settings.tg_token

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


async def get_link(name: str) -> str:
    return await get_start_link(name, encode=True)


@dp.message_handler(commands=["add"])
async def text_handler_add1(message: types.Message):
    if message.from_user.username not in settings.admins:
        return 1
    tmp_add[message.from_user.username] = {"name": message.text.replace("/add ", "", 1)}
    await MyStates.admin_send_price.set()
    await message.answer("Отправьте цену")


@dp.message_handler(state=MyStates.admin_send_price)
async def text_handler_add2(message: types.Message, state: FSMContext):
    if message.text == "0":
        await state.finish()
        del tmp_add[message.from_user.username]
        return 1
    await MyStates.admin_send_preview.set()
    tmp_add[message.from_user.username]["price"] = message.text
    await message.answer("Отправьте превью контента (0 для выхода)")


@dp.message_handler(content_types=["any"], state=MyStates.admin_send_preview)
async def text_handler_add3(message: types.Message, state: FSMContext):
    print(1)
    if message.text == "0":
        await state.finish()
        del tmp_add[message.from_user.username]
        return 1
    await MyStates.admin_send_content.set()
    tmp_add[message.from_user.username]["preview"] = {"msg_id": message.message_id, "chat_id": message.chat.id}
    tmp_add[message.from_user.username]["content"] = []
    await message.answer("Отправьте сообщения с контентом. Отправьте 1 для завершения, 0 для отмены")


@dp.message_handler(content_types=["any"], state=MyStates.admin_send_content)
async def text_handler_add4(message: types.Message, state: FSMContext):
    if message.text == "0":
        await state.finish()
        del tmp_add[message.from_user.username]
        return 1
    if message.text == "1":
        await state.finish()
        DB.add(tmp_add[message.from_user.username])
        await message.answer(await get_link(tmp_add[message.from_user.username]["name"]))
        del tmp_add[message.from_user.username]
        return 1
    tmp_add[message.from_user.username]["content"].append({"msg_id": message.message_id, "chat_id": message.chat.id})


@dp.message_handler(commands=["buy"])
async def text_handler_buy(message: types.Message):
    name = message.text.replace("/buy ", "", 1)
    content = DB.get(name)
    if content == 404:
        await message.answer("Такой контент не найден")
        return 1
    url = await pay.create(content, message.chat.id)
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton('Купить', url=url)
    keyboard.add(button)
    await bot.copy_message(chat_id=message.chat.id, from_chat_id=content["preview"]["chat_id"],
                           message_id=content["preview"]["msg_id"],
                           reply_markup=keyboard)


@dp.message_handler(commands=["list"])
async def text_handler_list(message: types.Message):
    await message.answer("\n".join(DB.get_names()))


@dp.message_handler(commands=["start"])
async def handler_start(message: Message):
    args = message.get_args()
    payload = decode_payload(args)
    if payload == "":
        # просто привет
        return 1
    content = DB.get(payload)
    if content == 404:
        await message.answer("Контент не найден")
    url = await pay.create(content, message.chat.id)
    keyboard = InlineKeyboardMarkup()
    button = InlineKeyboardButton('Купить', url=url)
    keyboard.add(button)
    await bot.copy_message(chat_id=message.chat.id, from_chat_id=content["preview"]["chat_id"],
                           message_id=content["preview"]["msg_id"],
                           reply_markup=keyboard)


async def send_on_pay(payload: str):
    chat_id = payload.split()[0]
    name = " ".join(payload.split()[1:])
    for msg in DB.get(name)["content"]:
        await bot.copy_message(chat_id=chat_id, from_chat_id=msg["chat_id"], message_id=msg["msg_id"])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
