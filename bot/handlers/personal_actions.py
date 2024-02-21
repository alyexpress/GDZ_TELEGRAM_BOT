from aiogram import types
from dispatcher import dp
from bot import db
from config import GET, AD_MESSAGE
import parsing

from time import sleep
from re import search, findall


kb = types.ReplyKeyboardMarkup(row_width=2, input_field_placeholder="Выберите из списка ниже:")
for i in parsing.ITEMS.keys():
    kb.insert(types.KeyboardButton(f"{parsing.ITEMS[i].get('sign', '')} {i.capitalize()}"))

def get_item(message):
    # function to get item from message by re search
    try: return search(r"[А-я\s]+", message.text).group(0).lower().strip()
    except: return

def get_kb(item, get):
    kb_nums = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if not db.get_nums(item): return types.ReplyKeyboardRemove()
    for line in db.get_nums(item):
        kb_nums.add(types.KeyboardButton(", ".join(map(lambda x: get[0] + x, line))))
    return kb_nums


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.bot.send_message(message.from_user.id, f"👋 Привет, {message.from_user.first_name}!")
    sleep(1)
    await message.bot.send_message(message.from_user.id, "⤵️ Выберите предмет:", reply_markup=kb)
    db.set_ad(message.from_user.id)
    db.set(message.from_user.id, "item", None)


@dp.message_handler(commands="stop")
async def stop(message: types.Message):
    await message.bot.send_message(message.from_user.id, "⤵️ Выберите предмет:", reply_markup=kb)
    db.set(message.from_user.id, "item", None)


@dp.message_handler(is_owner=True, commands="post")
async def post(message: types.Message):
    await message.reply("Ok")
    if db.ad(message.from_user.id): await message.reply("ad")


@dp.message_handler()
async def other(message: types.Message):
    if not db.get(message.from_user.id, "item"):
        item = get_item(message)
        if item not in parsing.ITEMS:
            await message.reply("⚠️ Предмет не найден", reply_markup=kb)
        else:
            db.set(message.from_user.id, "item", item)
            try:
                if type(parsing.ITEMS[item]['get']) is list:
                    get = [parsing.ITEMS[item]['get'][0]] + GET[parsing.ITEMS[item]['get'][0]]
                else: get = [parsing.ITEMS[item]['get']] + GET[parsing.ITEMS[item]['get']]
            except: get = GET[list(GET.keys())[0]]
            db.set(message.from_user.id, "get", get)
            await message.reply(f"Напишите {get[1]}:", reply_markup=get_kb(item, get))
    else:
        item = db.get(message.from_user.id, "item")
        nums = findall(r"\d+", message.text)
        allow_ad, get = False, db.get(message.from_user.id, "get")
        if not nums:
            item = get_item(message)
            if item not in parsing.ITEMS:
                await message.reply(f"🧐 Это не похоже на {get[2]}, чтобы остановиться нажми на /stop")
            else:
                db.set(message.from_user.id, "item", None)
                await other(message)
            return
        elif not parsing.ITEMS[item]['site']:
            # if in settings file parameter site is false
            for num in nums:
                media, title = [], f"{item.capitalize()} {get[0]}{num}"
                if type(parsing.ITEMS[item]['url']) is list:
                    for url in parsing.ITEMS[item]['url']:
                        media.append(types.InputMediaPhoto(url.replace("****", num), None if media else title))
                else: media.append(types.InputMediaPhoto(parsing.ITEMS[item]['url'].replace("****", num), title))
                try: await message.bot.send_media_group(message.from_user.id, media)
                except: await message.bot.send_message(message.from_user.id, f"{get[0]}{num} не найден")
                else: allow_ad = True
        elif parsing.SITES[parsing.ITEMS[item]['site']]['type'] == "img":
            # return type is img
            for num in nums:
                media, title = [], f"{item.capitalize()} {get[0]}{num}"
                for url in parsing.get_urls(item, num): media.append(types.InputMediaPhoto(url, None if media else title))
                try: await message.bot.send_media_group(message.from_user.id, media)
                except: await message.bot.send_message(message.from_user.id, f"{get[0]}{num} не найден")
                else: allow_ad = True
        elif parsing.SITES[parsing.ITEMS[item]['site']]['type'] == "text":
            # return type is text
            for num in nums:
                text, url = parsing.get_urls(item, num)
                if not text: await message.bot.send_message(message.from_user.id, f"{get[0]}{num} не найден")
                else:
                    await message.bot.send_message(message.from_user.id,
                                                   text + f'\n\n<a href="{url}">{item.capitalize()} {get[0]}{num}</a>')
                    allow_ad = True
        if allow_ad:
            db.set(message.from_user.id, "item", None)
            db.set_nums(item, nums)
            if db.ad(message.from_user.id) and AD_MESSAGE:
                sleep(1)
                await message.bot.send_message(message.from_user.id, AD_MESSAGE)
                sleep(3)
            sleep(2)
            await message.bot.send_message(message.from_user.id, "⤵️ Выберите предмет:", reply_markup=kb)
        else:
            sleep(1)
            await message.bot.send_message(message.from_user.id,
                                            f"Напишите {get[2]} еще раз или нажмите /stop для остановки")
