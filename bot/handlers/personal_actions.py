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
        if ":" in line:
            _num, nums = line.split(":")
            text = get[0] + _num + ": " + ", ".join(map(lambda x: get[3] + x, nums.split(",")))
        else: text = ", ".join(map(lambda x: get[0] + x, line.split(",")))
        kb_nums.add(types.KeyboardButton(text))
    return kb_nums


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.bot.send_message(message.from_user.id, f"👋 Привет, {message.from_user.first_name}!")
    db.set_ad(message.from_user.id)
    sleep(1)
    await stop(message)


@dp.message_handler(commands=["stop", "help"])
async def stop(message: types.Message):
    db.reset(message.from_user.id)
    if '/help' in message.text:
        await message.reply("help wanted", reply=False)
        sleep(1.5)
    await message.bot.send_message(message.from_user.id, "⤵️ Выберите предмет:", reply_markup=kb)


@dp.message_handler(is_owner=True, commands="post")
async def post(message: types.Message):
    if '/post' != message.text and db.get(message.from_user.id, "post"):
        for user in db.get_users():
            if user != message.from_user.id: await message.forward(user)
        await message.reply(f"✅ Успешно адресованно {len(db.get_users())-1} людям", reply=False)
        sleep(1)
        await stop(message)
    else:
        db.set(message.from_user.id, "post", True)
        await message.reply("Напишите пост:")

@dp.message_handler(content_types=['photo', 'document'])
async def post_msg(message: types.Message):
    if db.get(message.from_user.id, "post"): await post(message)


@dp.message_handler()
async def other(message: types.Message):
    if db.get(message.from_user.id, "post"): await post(message)
    elif not db.get(message.from_user.id, "item"):
        item = get_item(message)
        if item not in parsing.ITEMS:
            await message.reply("⚠️ Предмет не найден", reply_markup=kb)
        else:
            db.set(message.from_user.id, "item", item)
            try:
                if type(parsing.ITEMS[item]['get']) is list:
                    get = []
                    for j in parsing.ITEMS[item]['get']: get.extend([j] + GET[j])
                else: get = [parsing.ITEMS[item]['get']] + GET[parsing.ITEMS[item]['get']]
            except: get = [list(GET.keys())[0]] + GET[list(GET.keys())[0]]
            db.set(message.from_user.id, "get", get)
            request = f"{get[2]}, {get[4]}" if len(get) > 3 else get[1]
            await message.reply(f"Напишите {request}:", reply_markup=get_kb(item, get))
    else:
        item = db.get(message.from_user.id, "item")
        nums = findall(r"\d+", message.text)
        _num = db.get(message.from_user.id, "_num")
        allow_ad, get = False, db.get(message.from_user.id, "get")
        if len(get) > 3 and not _num:
            if len(nums) > 1: _num, nums = nums[0], nums[1:]
            elif len(nums) == 1:
                db.set(message.from_user.id, "_num", nums[0])
                await message.reply(f"Напишите {get[4]}:", reply=False)
                return
            else:
                await message.reply(f"🧐 Это не похоже на {get[2]}, чтобы остановиться нажми на /stop")
                return

        if not nums:
            item = get_item(message)
            if item not in parsing.ITEMS:
                request = get[4] if _num else get[2]
                await message.reply(f"🧐 Это не похоже на {request}, чтобы остановиться нажми на /stop")
            else:
                db.set(message.from_user.id, "item", None)
                await other(message)
            return
        elif not parsing.ITEMS[item]['site']:
            # if in settings file parameter site is false
            for num in nums:
                sign = get[3] if _num else get[0]
                media, title = [], f"{item.capitalize()} {sign}{num}"
                if type(parsing.ITEMS[item]['url']) is list:
                    for url in parsing.ITEMS[item]['url']:
                        url = url.replace("****", num)
                        if _num: url = url.replace("***", _num)
                        media.append(types.InputMediaPhoto(url, None if media else title))
                else:
                    url = parsing.ITEMS[item]['url'].replace("****", num)
                    if _num: url = url.replace("***", _num)
                    media.append(types.InputMediaPhoto(url, title))
                try: await message.bot.send_media_group(message.from_user.id, media)
                except: await message.bot.send_message(message.from_user.id, f"{sign}{num} не найден")
                else: allow_ad = True
        elif parsing.SITES[parsing.ITEMS[item]['site']]['type'] == "img":
            # return type is img
            for num in nums:
                sign = get[3] if _num else get[0]
                media, title = [], f"{item.capitalize()} {sign}{num}"
                for url in parsing.get_urls(item, num, _num):
                    media.append(types.InputMediaPhoto(url, None if media else title))
                try: await message.bot.send_media_group(message.from_user.id, media)
                except: await message.bot.send_message(message.from_user.id, f"{sign}{num} не найден")
                else: allow_ad = True
        elif parsing.SITES[parsing.ITEMS[item]['site']]['type'] == "text":
            # return type is text
            for num in nums:
                sign = get[3] if _num else get[0]
                text, url = parsing.get_urls(item, num, _num)
                if not text: await message.bot.send_message(message.from_user.id, f"{sign}{num} не найден")
                else:
                    text += f'\n\n<a href="{url}">{item.capitalize()} {sign}{num}</a>'
                    await message.bot.send_message(message.from_user.id, text)
                    allow_ad = True
        if allow_ad:
            db.reset(message.from_user.id)
            db.set_nums(item, nums, _num)
            if db.ad(message.from_user.id) and AD_MESSAGE:
                sleep(1)
                await message.bot.send_message(message.from_user.id, AD_MESSAGE)
                sleep(3)
            sleep(2)
            await message.bot.send_message(message.from_user.id, "⤵️ Выберите предмет:", reply_markup=kb)
        else:
            sleep(1)
            request = get[4] if _num else get[2]
            await message.bot.send_message(message.from_user.id,
                f"Напишите {request} еще раз или нажмите /stop для остановки")
