import os
import time
import zipfile
import shutil
from . import downloader, ultroid_cmd, ULTConfig
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

@ultroid_cmd(pattern="nozip$")
async def safe_zip_extract(event):
    """Extract zip files and upload files/folders (safe for Ultroid)."""
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return await event.eor("Reply to a .zip file.")

    if not hasattr(reply.media, "document"):
        return await event.eor("Invalid media.")

    if not reply.file.name.endswith(".zip"):
        return await event.eor("Only .zip files are supported in safe mode.")

    msg = await event.eor("Extracting...")

    t = time.time()
    downloaded = await downloader(
        reply.file.name,
        reply.media.document,
        msg,
        t,
        "Downloading...",
    )
    zip_path = downloaded.name

    if os.path.isdir("nozip"):
        shutil.rmtree("nozip")
    os.mkdir("nozip")

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("nozip")
    except Exception as e:
        return await msg.edit(f"Extraction failed: `{e}`")

    # Walk extracted files and folders
    all_paths = []
    for root, dirs, files in os.walk("nozip"):
        for name in files:
            all_paths.append(os.path.join(root, name))
        for name in dirs:
            all_paths.append(os.path.join(root, name))

    if not all_paths:
        return await msg.edit("No files or folders extracted.")

    for path in all_paths:
        if os.path.isdir(path):
            continue  # folders can't be uploaded directly
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

    shutil.rmtree("nozip")
    os.remove(zip_path)
    await msg.delete()


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
