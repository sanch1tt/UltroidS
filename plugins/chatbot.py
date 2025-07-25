# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# https://github.com/TeamUltroid/Ultroid/

from . import get_help
__doc__ = get_help("help_chatbot")

import httpx
from pyUltroid.fns.tools import get_user
from . import LOGS, eod, get_string, inline_mention, udB, ultroid_cmd


@ultroid_cmd(pattern="repai")
async def im_lonely_chat_with_me(event):
    if event.reply_to:
        message = (await event.get_reply_message()).message
    else:
        try:
            message = event.text.split(" ", 1)[1]
        except IndexError:
            return await eod(event, get_string("tban_1"), time=10)

    reply_ = await get_chatbot_reply(message=message)
    await event.eor(reply_)


@ultroid_cmd(pattern="addai")
async def add_chatBot(event):
    await chat_bot_fn(event, type_="add")


@ultroid_cmd(pattern="remai")
async def rem_chatBot(event):
    await chat_bot_fn(event, type_="remov")


@ultroid_cmd(pattern="listai")
async def lister(event):
    key = udB.get_key("CHATBOT_USERS") or {}
    users = key.get(event.chat_id, [])
    if not users:
        return await event.eor(get_string("chab_2"), time=5)
    msg = "**Total List Of AI Enabled Users In This Chat :**\n\n"
    for i in users:
        try:
            user = await event.client.get_entity(int(i))
            user = inline_mention(user)
        except BaseException:
            user = f"`{i}`"
        msg += f"• {user}\n"
    await event.eor(msg, link_preview=False)


async def chat_bot_fn(event, type_):
    if event.reply_to:
        user_ = (await event.get_reply_message()).sender
    else:
        temp = event.text.split(maxsplit=1)
        try:
            user_ = await event.client.get_entity(await event.client.parse_id(temp[1]))
        except BaseException as er:
            LOGS.exception(er)
            user_ = event.chat if event.is_private else None
    if not user_:
        return await eod(event, get_string("chab_1"))
    key = udB.get_key("CHATBOT_USERS") or {}
    chat = event.chat_id
    user = user_.id
    if type_ == "add":
        if key.get(chat):
            if user not in key[chat]:
                key[chat].append(user)
        else:
            key.update({chat: [user]})
    elif type_ == "remov":
        if key.get(chat):
            if user in key[chat]:
                key[chat].remove(user)
            if chat in key and not key[chat]:
                del key[chat]
    udB.set_key("CHATBOT_USERS", key)
    await event.eor(f"**ChatBot:**\n{type_}ed {inline_mention(user_)}")


# ✅ Gemini API Chat Function
async def get_chatbot_reply(message: str) -> str:
    try:
        api_key = udB.get_key("GOOGLEAPI")
        if not api_key:
            return "`GOOGLEAPI key not set. Use .setdb GOOGLEAPI <your-key>`"
        
        headers = {"Content-Type": "application/json"}
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

        payload = {
            "contents": [{"parts": [{"text": message}]}]
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                return f"`Error from Gemini API:` {resp.text}"
            data = resp.json()
            reply = data["candidates"][0]["content"]["parts"][0]["text"]
            return reply
    except Exception as e:
        LOGS.exception(e)
        return "`Something went wrong with Gemini API.`"
