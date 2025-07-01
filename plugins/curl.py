# curl.py

import shlex
import time
import traceback
import requests

from io import BytesIO
from userbot import bot, udB, ultroid_bot, ULTConfig
from userbot.utils import time_formatter, get_string, get_display_name, inline_mention
from userbot import CMD_HANDLER as cmd
from userbot import aexec
from userbot.include.ult_utils import _parse_eval
from userbot.include.git_helper import KEEP_SAFE
from userbot.utils import edit_or_reply as eor, _ignore_eval
from telethon import events

@bot.on(events.NewMessage(pattern=r"\.curl(?: |$)(.*)", outgoing=True))
async def curl_cmd(event):
    cmd_line = event.pattern_match.group(1)
    if not cmd_line:
        return await event.eor("🔸 **Usage:** `.curl METHOD URL [--data 'payload'] [--header 'Key: Value']`")

    spli = cmd_line.split()
    mode = ""
    reply_msg = None

    async def extract_cmd():
        try:
            return cmd_line.split(maxsplit=1)[1]
        except IndexError:
            await event.eor("->> Wrong Format <<-")
            return None

    if spli[0] in ["-s", "--silent"]:
        await event.delete()
        mode = "silent"
    elif spli[0] in ["-n", "--noedit"]:
        mode = "no-edit"
        reply_msg = await event.reply(get_string("com_1"))
    if mode:
        cmd_line = await extract_cmd()
    if not cmd_line:
        return

    if not mode == "silent" and not reply_msg:
        reply_msg = await event.eor(get_string("com_1"))

    try:
        args = shlex.split(cmd_line)
        method = args[0].upper()
        url = args[1]
        headers = {}
        data = None

        for i, arg in enumerate(args):
            if arg in ("--data", "-d") and i + 1 < len(args):
                data = args[i + 1]
            elif arg in ("--header", "-H") and i + 1 < len(args):
                h = args[i + 1].split(":", 1)
                if len(h) == 2:
                    headers[h[0].strip()] = h[1].strip()

        t0 = time.time()
        response = requests.request(method, url, headers=headers, data=data, timeout=10)
        t1 = time.time() - t0

        status_code = response.status_code
        body = response.text
        headers_out = dict(response.headers)

        out = f"__►__ **CURL** (__in {time_formatter(t1 * 1000)}__)\n"
        out += f"```{cmd_line}```\n\n"
        out += f"__►__ **STATUS**: `{status_code}`\n"
        out += f"__►__ **HEADERS:**\n```{headers_out}```\n"

        if len(body) > 3000:
            out += f"__►__ **BODY (truncated)**:\n```{body[:2000]}...```"
        else:
            out += f"__►__ **BODY:**\n```{body}```"

        if len(out) > 4096:
            with BytesIO(out.encode()) as out_file:
                out_file.name = "curl_response.txt"
                await event.client.send_file(
                    event.chat_id,
                    out_file,
                    force_document=True,
                    thumb=ULTConfig.thumb,
                    caption=f"```{cmd_line}```" if len(cmd_line) < 998 else None,
                    reply_to=event.reply_to_msg_id or event.id,
                )
                return await reply_msg.delete()
        else:
            await reply_msg.edit(out)

    except Exception as e:
        err = traceback.format_exc()
        if mode == "silent":
            log_chat = udB.get_key("LOG_CHANNEL")
            error_msg = f"• <b>CURL ERROR</b>\n\n• <b>CHAT:</b> <code>{get_display_name(event.chat)}</code> [<code>{event.chat_id}</code>]\n"
            error_msg += f"• <b>CMD:</b>\n<code>{cmd_line}</code>\n\n• <b>TRACE:</b>\n<code>{err}</code>"
            if len(error_msg) > 4000:
                with BytesIO(error_msg.encode()) as out_file:
                    out_file.name = "Curl-Error.txt"
                    await event.client.send_file(log_chat, out_file, caption="`CURL ERROR`")
            else:
                await event.client.send_message(log_chat, error_msg, parse_mode="html")
        else:
            await reply_msg.edit(f"❌ **Exception:**\n```{err}```")
          
