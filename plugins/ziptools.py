import os
import time
import zipfile
import shutil
from . import (
    HNDLR,
    ULTConfig,
    asyncio,
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
        return await event.eor("Reply to a file to zip it.")

    xx = await event.eor("Downloading...")
    if reply.media:
        if hasattr(reply.media, "document"):
            file = reply.media.document
            image = await downloader(
                reply.file.name, reply.media.document, xx, t, "Downloading..."
            )
            file = image.name
        else:
            file = await event.download_media(reply)

    zip_name = os.path.splitext(file)[0] + ".zip"
    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file, arcname=os.path.basename(file))
    except Exception as e:
        return await xx.edit(f"Zipping failed: `{e}`")

    n_file, _ = await event.client.fast_uploader(
        zip_name, show_progress=True, event=event, message="Uploading...", to_delete=True
    )
    await event.client.send_file(
        event.chat_id,
        n_file,
        force_document=True,
        thumb=ULTConfig.thumb,
        caption=f"`{n_file.name}`",
        reply_to=reply.id
    )
    os.remove(zip_name)
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
            return await status.edit("Only .zip files supported.")
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

    ok = get_all_files("unzip")
    for x in ok:
        n_file, _ = await event.client.fast_uploader(
            x, show_progress=True, event=event, message="Uploading...", to_delete=True
        )
        await event.client.send_file(
            event.chat_id,
            n_file,
            force_document=True,
            thumb=ULTConfig.thumb,
            caption=f"`{n_file.name}`",
        )
    await status.delete()
    shutil.rmtree("unzip")
    os.remove(file)


@ultroid_cmd(pattern="addzip$")
async def azipp(event):
    reply = await event.get_reply_message()
    t = time.time()
    if not (reply and reply.media):
        return await event.eor("Reply to a file to add to batch.")

    xx = await event.eor("Adding to zip batch...")
    if not os.path.isdir("zipbatch"):
        os.mkdir("zipbatch")

    if hasattr(reply.media, "document"):
        file = reply.media.document
        image = await downloader(
            f"zipbatch/{reply.file.name}", reply.media.document, xx, t, "Downloading..."
        )
        file = image.name
    else:
        file = await event.download_media(reply.media, "zipbatch/")

    await xx.edit(f"Downloaded `{file}`. Use `{HNDLR}dozip` to zip all added files.")


@ultroid_cmd(pattern="dozip( (.*)|$)")
async def do_zip(event):
    if not os.path.isdir("zipbatch"):
        return await event.eor("No files added. Use `.addzip` first.")

    xx = await event.eor("Creating zip...")
    zip_name = "ultroid.zip"

    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk("zipbatch"):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, "zipbatch")
                    zipf.write(full_path, arcname)
    except Exception as e:
        return await xx.edit(f"Batch zipping failed: `{e}`")

    k = time.time()
    xxx = await uploader(zip_name, zip_name, k, xx, "Uploading zip...")
    await event.client.send_file(
        event.chat_id,
        xxx,
        force_document=True,
        thumb=ULTConfig.thumb,
    )
    shutil.rmtree("zipbatch")
    os.remove(zip_name)
    await xx.delete()
