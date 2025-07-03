# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available

• `{i}zip <reply to file>`
    zip the replied file
    To set password on zip: `{i}zip <password>` reply to file

• `{i}unzip <reply to zip file>`
    unzip the replied file.

• `{i}azip <reply to file>`
   add file to batch for batch upload zip

• `{i}dozip`
   upload batch zip the files u added from `{i}azip`
   To set Password: `{i}dozip <password>`

"""
import zipfile
import os
import time

from . import (
    HNDLR,
    ULTConfig,
    asyncio,
    bash,
    downloader,
    get_all_files,
    get_string,
    ultroid_cmd,
    uploader,
)


@ultroid_cmd(pattern="zip( (.*)|$)")
async def zipp(event):
    reply = await event.get_reply_message()
    t = time.time()
    if not reply:
        await event.eor(get_string("zip_1"))
        return
    xx = await event.eor(get_string("com_1"))
    if reply.media:
        if hasattr(reply.media, "document"):
            file = reply.media.document
            image = await downloader(
                reply.file.name, reply.media.document, xx, t, get_string("com_5")
            )
            file = image.name
        else:
            file = await event.download_media(reply)
    inp = file.replace(file.split(".")[-1], "zip")
    if event.pattern_match.group(1).strip():
        await bash(
            f"zip -r --password {event.pattern_match.group(1).strip()} {inp} {file}"
        )
    else:
        await bash(f"zip -r {inp} {file}")
    k = time.time()
    n_file, _ = await event.client.fast_uploader(
        inp, show_progress=True, event=event, message="Uploading...", to_delete=True
    )
    await event.client.send_file(
        event.chat_id,
        n_file,
        force_document=True,
        thumb=ULTConfig.thumb,
        caption=f"`{n_file.name}`",
        reply_to=reply,
    )
    os.remove(inp)
    os.remove(file)
    await xx.delete()

@ultroid_cmd(pattern="unzip( (.*)|$)")
async def unzipp(event):
    reply = await event.get_reply_message()
    file = event.pattern_match.group(1).strip()
    t = time.time()
    if not ((reply and reply.media) or file):
        return await event.eor("Reply to a zip file to extract.")

    status = await event.eor("Extracting...")

    if reply.media:
        if not hasattr(reply.media, "document"):
            return await status.edit("Invalid media.")
        if not reply.file.name.endswith(".zip"):
            return await status.edit("Only .zip files supported (safe mode).")
        image = await downloader(
            reply.file.name, reply.media.document, status, t, "Downloading..."
        )
        file = image.name

    if os.path.isdir("unzip"):
        shutil.rmtree("unzip")
    os.mkdir("unzip")

    try:
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall("unzip")
    except Exception as e:
        return await status.edit(f"Extraction failed: `{e}`")

    all_paths = []
    for root, dirs, files in os.walk("unzip"):
        for name in files:
            all_paths.append(os.path.join(root, name))
        for name in dirs:
            all_paths.append(os.path.join(root, name))

    if not all_paths:
        return await status.edit("No files or folders extracted.")

    for path in all_paths:
        if os.path.isdir(path):
            continue  # skip folders (can't send directly)
        try:
            up_msg = await event.client.send_message(
                event.chat_id, f"Uploading: `{os.path.basename(path)}`"
            )
            n_file, _ = await event.client.fast_uploader(
                path,
                show_progress=True,
                event=event,
                message="Uploading...",
                to_delete=True,
                status_msg=up_msg
            )
            await event.client.send_file(
                event.chat_id,
                n_file,
                force_document=True,
                thumb=ULTConfig.thumb,
                caption=f"`{n_file.name}`",
                reply_to=reply.id
            )
            await up_msg.delete()
        except Exception as e:
            await event.reply(f"Upload error: `{e}`")

    shutil.rmtree("unzip")
    os.remove(file)
    await status.delete()

@ultroid_cmd(pattern="addzip$")
async def azipp(event):
    reply = await event.get_reply_message()
    t = time.time()
    if not (reply and reply.media):
        await event.eor(get_string("zip_1"))
        return
    xx = await event.eor(get_string("com_1"))
    if not os.path.isdir("zip"):
        os.mkdir("zip")
    if reply.media:
        if hasattr(reply.media, "document"):
            file = reply.media.document
            image = await downloader(
                f"zip/{reply.file.name}",
                reply.media.document,
                xx,
                t,
                get_string("com_5"),
            )

            file = image.name
        else:
            file = await event.download_media(reply.media, "zip/")
    await xx.edit(
        f"Downloaded `{file}` succesfully\nNow Reply To Other Files To Add And Zip all at once"
    )


@ultroid_cmd(pattern="dozip( (.*)|$)")
async def do_zip(event):
    if not os.path.isdir("zip"):
        return await event.eor(get_string("zip_2").format(HNDLR))
    xx = await event.eor(get_string("com_1"))
    if event.pattern_match.group(1).strip():
        await bash(
            f"zip -r --password {event.pattern_match.group(1).strip()} ultroid.zip zip/*"
        )
    else:
        await bash("zip -r ultroid.zip zip/*")
    k = time.time()
    xxx = await uploader("ultroid.zip", "ultroid.zip", k, xx, get_string("com_6"))
    await event.client.send_file(
        event.chat_id,
        xxx,
        force_document=True,
        thumb=ULTConfig.thumb,
    )
    await bash("rm -rf zip")
    os.remove("ultroid.zip")
    await xx.delete()
