import asyncio
import os
import time

from bot import (LOGGER, UPLOAD_AS_DOC, UPLOAD_TO_DRIVE, delete_all, formatDB,
                 gDict, queueDB)
from config import Config
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helpers.display_progress import Progress
from helpers.ffmpeg_helper import MergeSub, MergeVideo, take_screen_shot
from helpers.rclone_upload import rclone_driver, rclone_upload
from helpers.uploader import uploadVideo
from helpers.utils import UserSettings
from PIL import Image
from pyrogram import Client
from pyrogram.errors import MessageNotModified
from pyrogram.errors.rpc_error import UnknownError
from pyrogram.types import CallbackQuery

async def mergeNow(c: Client, cb: CallbackQuery, new_file_name: str):
    omess = cb.message.reply_to_message
    vid_list = list()
    sub_list = list()
    sIndex = 0
    await cb.message.edit_text("**⭕ Processing...**")
    duration = 0
    list_message_ids = queueDB.get(cb.from_user.id)["videos"]
    list_message_ids.sort()
    list_subtitle_ids = queueDB.get(cb.from_user.id)["subtitles"]
    
    if list_message_ids is None:
        await cb.answer("Queue Empty", show_alert=True)
        await cb.message.delete()
        return
    
    if not os.path.exists(f"downloads/{str(cb.from_user.id)}/"):
        os.makedirs(f"downloads/{str(cb.from_user.id)}/")
    
    input_ = f"downloads/{str(cb.from_user.id)}/input.txt"
    all_videos = len(list_message_ids)
    n = 1

    for i in await c.get_messages(chat_id=cb.from_user.id, message_ids=list_message_ids):
        media = i.video or i.document
        await cb.message.edit_text(f"**<u>Downloading:</u>⤵️\n{media.file_name}**")
        LOGGER.info(f"Downloading: {media.file_name}")
        await asyncio.sleep(5)
        
        file_dl_path = None
        sub_dl_path = None
        
        try:
            c_time = time.time()
            prog = Progress(cb.from_user.id, c, cb.message)
            file_dl_path = await c.download_media(
                message=media,
                file_name=f"downloads/{str(cb.from_user.id)}/{str(i.id)}/vid.mkv",
                progress=prog.progress_for_pyrogram,
                progress_args=(f"**<u>Downloading:</u>⤵️\n{media.file_name}**", c_time, f"\n**🔽 Downloading: {n}/{all_videos}**"),
            )
            n += 1
            if gDict.get(cb.message.chat.id) and cb.message.id in gDict[cb.message.chat.id]:
                return
            await cb.message.edit_text(f"**<u>Downloading:</u>⤵️\n{media.file_name}**")
            LOGGER.info(f"Downloading: {media.file_name}")
            await asyncio.sleep(5)
        except UnknownError as e:
            LOGGER.error(e)
            pass
        except Exception as downloadErr:
            LOGGER.error(f"Failed to download. Error: {downloadErr}")
            queueDB.get(cb.from_user.id)["videos"].remove(i.id)
            await cb.message.edit_text("**File Skipped!**")
            await asyncio.sleep(4)
            continue

        if list_subtitle_ids[sIndex] is not None:
            a = await c.get_messages(chat_id=cb.from_user.id, message_ids=list_subtitle_ids[sIndex])
            sub_dl_path = await c.download_media(message=a, file_name=f"downloads/{str(cb.from_user.id)}/{str(a.id)}/")
            LOGGER.info(f"Got subtitle: {a.document.file_name}")
            file_dl_path = await MergeSub(file_dl_path, sub_dl_path, cb.from_user.id)
            LOGGER.info("Added subtitles")
        sIndex += 1

        metadata = extractMetadata(createParser(file_dl_path))
        try:
            if metadata.has("duration"):
                duration += metadata.get("duration").seconds
            vid_list.append(f"file '{file_dl_path}'")
        except:
            await delete_all(root=f"downloads/{str(cb.from_user.id)}")
            queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
            formatDB.update({cb.from_user.id: None})
            await cb.message.edit_text("**Video is corrupted; Try to add thumbnail first.**")
            return

    _cache = list(set(vid_list))
    vid_list = _cache
    LOGGER.info(f"Trying to merge videos for user {cb.from_user.id}")
    await cb.message.edit_text("**🔀 Trying to merge videos...**")
    
    with open(input_, "w") as _list:
        _list.write("\n".join(vid_list))
    
    merged_video_path = await MergeVideo(input_file=input_, user_id=cb.from_user.id, message=cb.message, format_="mkv")
    
    if merged_video_path is None:
        await cb.message.edit_text("**🔴 Failed to merge video!**")
        await delete_all(root=f"downloads/{str(cb.from_user.id)}")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        return
    
    try:
        await cb.message.edit_text("**🟢 Video is successfully merged!**")
    except MessageNotModified:
        await cb.message.edit_text("**🟢 Video is successfully merged!**")
    
    LOGGER.info(f"Video merged for: {cb.from_user.first_name}")
    await asyncio.sleep(3)
    file_size = os.path.getsize(merged_video_path)
    os.rename(merged_video_path, new_file_name)
    await cb.message.edit_text(f"**<u>Renaming:</u>\n**{new_file_name.rsplit('/', 1)[-1]}**")
    await asyncio.sleep(3)
    merged_video_path = new_file_name
    
    if UPLOAD_TO_DRIVE.get(f"{cb.from_user.id}"):
        await rclone_driver(omess, cb, merged_video_path)
        await delete_all(root=f"downloads/{str(cb.from_user.id)}")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        return
    
    if file_size > 2147483648 and not Config.IS_PREMIUM:  # 2GB
        await cb.message.edit_text(f"**Video is larger than 2GB and cannot be uploaded.\n\nPurchase premium membership for 4GB support from: {Config.OWNER_USERNAME}.**")
        await delete_all(root=f"downloads/{str(cb.from_user.id)}")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        return
    
    if Config.IS_PREMIUM and file_size > 4294967296:  # 4GB
        await cb.message.edit_text("**Video is larger than 4GB and cannot be uploaded due to Telegram limitations.**")
        await delete_all(root=f"downloads/{str(cb.from_user.id)}")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        return
    
    await cb.message.edit_text("**♻️ Extracting video data...**")
    duration = 1
    
    try:
        metadata = extractMetadata(createParser(merged_video_path))
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds
    except Exception as er:
        await delete_all(root=f"downloads/{str(cb.from_user.id)}")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        await cb.message.edit_text("**🔴 Merged video is corrupted; Try to add thumbnail first.**")
        return
    
    try:
        user = UserSettings(cb.from_user.id, cb.from_user.first_name)
        thumb_id = user.thumbnail
        if thumb_id is None:
            raise Exception
        video_thumbnail = f"downloads/{str(cb.from_user.id)}_thumb.jpg"
        await c.download_media(message=str(thumb_id), file_name=video_thumbnail)
    except Exception as err:
        LOGGER.info("Generating thumbnail")
        video_thumbnail = await take_screen_shot(merged_video_path, f"downloads/{str(cb.from_user.id)}", (duration / 2))
    
    width = 1280
    height = 720
    
    try:
        thumb = extractMetadata(createParser(video_thumbnail))
        height = thumb.get("height")
        width = thumb.get("width")
        img = Image.open(video_thumbnail)
        if width > height:
            img.resize((320, height))
        elif height > width:
            img.resize((width, 320))
        img.save(video_thumbnail)
        Image.open(video_thumbnail).convert("RGB").save(video_thumbnail, "JPEG")
    except:
        await delete_all(root=f"downloads/{str(cb.from_user.id)}")
        queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
        formatDB.update({cb.from_user.id: None})
        await cb.message.edit("**🔴 Merged Video is corrupted; Try to add thumbnail first.**")
        return
    await uploadVideo(
        c=c,
        cb=cb,
        merged_video_path=merged_video_path,
        width=width,
        height=height,
        duration=duration,
        video_thumbnail=video_thumbnail,
        file_size=os.path.getsize(merged_video_path),
        upload_mode=UPLOAD_AS_DOC[f"{cb.from_user.id}"],
    )
    await cb.message.delete(True)
    await delete_all(root=f"downloads/{str(cb.from_user.id)}")
    queueDB.update({cb.from_user.id: {"videos": [], "subtitles": [], "audios": []}})
    formatDB.update({cb.from_user.id: None})
    return
