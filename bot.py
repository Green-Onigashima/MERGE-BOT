from dotenv import load_dotenv
#
from base64 import standard_b64encode, standard_b64decode
import pytz
from datetime import datetime
import requests
from pymongo import MongoClient
#
load_dotenv(
    "config.env",
    override=True,
)
import asyncio
import os
import shutil
import time

import psutil
import pyromod
from PIL import Image
from pyrogram import Client, filters,enums
from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    PeerIdInvalid,
    UserIsBlocked,
)
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    User,
)

from __init__ import (
    AUDIO_EXTENSIONS,
    BROADCAST_MSG,
    LOGGER,
    MERGE_MODE,
    SUBTITLE_EXTENSIONS,
    UPLOAD_AS_DOC,
    UPLOAD_TO_DRIVE,
    VIDEO_EXTENSIONS,
    bMaker,
    formatDB,
    gDict,
    queueDB,
    replyDB,
)
from config import Config
from helpers import database
from helpers.utils import UserSettings, get_readable_file_size, get_readable_time

botStartTime = time.time()
parent_id = Config.GDRIVE_FOLDER_ID

paid_promotion = Config.PAID_PROMOTION
shortener_site = Config.SHORTENER_SITE
shortener_api = Config.SHORTENER_API
bot_username = Config.BOT_USERNAME


jr = MongoClient(Config.DATABASE_URL)
jrbots = jr["STUPIDBOI69"]
collection = jrbots["tokens"]

def shorten_url(url):
    # SHORTNER KA API AND URL 
    resp = requests.get(f'{shortener_site}/api?api={shortener_api}&url={url}').json()
    if resp['status'] == 'success':
        SHORT_LINK = resp['shortenedUrl']
    return SHORT_LINK

def str_to_b64(__str: str) -> str:
    str_bytes = __str.encode('ascii')
    bytes_b64 = standard_b64encode(str_bytes)
    b64 = bytes_b64.decode('ascii')
    return b64

def b64_to_str(b64: str) -> str:
    bytes_b64 = b64.encode('ascii')
    bytes_str = standard_b64decode(bytes_b64)
    __str = bytes_str.decode('ascii')
    return __str

def get_current_time():
    tz = pytz.timezone('Asia/Kolkata')
    return int(datetime.now(tz).timestamp())

def get_readable_time(seconds):
    dt = datetime.fromtimestamp(int(seconds))
    return dt.strftime('%Y-%m-%d %H:%M:%S')




class MergeBot(Client):
    def start(self):
        super().start()
        try:
            self.send_message(chat_id=int(Config.OWNER), text="<b>Bot Started!</b>")
        except Exception as err:
            LOGGER.error("Boot alert failed! Please start bot in PM")
        return LOGGER.info("Bot Started!")

    def stop(self):
        super().stop()
        return LOGGER.info("Bot Stopped")


mergeApp = MergeBot(
    name="MergeBot",
    api_hash=Config.API_HASH,
    api_id=int(Config.API_ID),
    bot_token=Config.BOT_TOKEN,
    workers=300,
    plugins=dict(root="plugins"),
    app_version="7.0+StupidBoi-MergeBot",
)


if os.path.exists("downloads") == False:
    os.makedirs("downloads")


@mergeApp.on_message(filters.command(["log"]) & filters.user(Config.OWNER_USERNAME))
async def sendLogFile(c: Client, m: Message):
    await m.reply_document(document="./mergebotlog.txt")
    return

'''
@mergeApp.on_message(filters.command(["login"]) & filters.private)
async def loginHandler(c: Client, m: Message):
    user = UserSettings(m.from_user.id, m.from_user.first_name)
    if user.banned:
        await m.reply_text(text=f"**Banned User Detected!**\n  🛡️ Unfortunately you can't use me\n\n𝖢𝗈𝗇𝗍𝖺𝖼𝗍 ➜ <a href=https://t.me/Snowball_Official>𝖮𝗐𝗇𝖾𝗋</a>",quote=True)
        return
    if user.user_id == int(Config.OWNER):
        user.allowed = True
    if user.allowed:
        await m.reply_text(text=f"**Dont Spam**\n  ⚡ You can use me!!", quote=True)
    else:
        try:
            passwd = m.text.split(" ", 1)[1]
        except:
            await m.reply_text("**Command:**\n  `/login <password>`\n\n**Usage:**\n  `password`: Get the password from owner",quote=True,parse_mode=enums.parse_mode.ParseMode.MARKDOWN)
        passwd = passwd.strip()
        if passwd == Config.PASSWORD:
            user.allowed = True
            await m.reply_text(
                text=f"**Login passed ✅,**\n  ⚡ Now you can use me!!", quote=True
            )
        else:
            await m.reply_text(
                text=f"**Login failed ❌,**\n  🛡️ Unfortunately you can't use me\n\n𝖢𝗈𝗇𝗍𝖺𝖼𝗍 ➜ <a href=https://t.me/Snowball_Official>𝖮𝗐𝗇𝖾𝗋</a>",
                quote=True,
            )
    user.set()
    del user
    return
'''


@mergeApp.on_message(filters.command(["stats"]) & filters.private)
async def stats_handler(c: Client, m: Message):
    currentTime = get_readable_time(time.time() - botStartTime)
    total, used, free = shutil.disk_usage(".")
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    stats = (
        f"<b>╭─BOT STATISTICS───────────</b>\n"
        f"<b>│</b>\n"
        f"<b>├⏳ Bot Uptime            : {currentTime}</b>\n"
        f"<b>├💾 Total Disk Space  : {total}</b>\n"
        f"<b>├📀 Total Used Space : {used}</b>\n"
        f"<b>├💿 Total Free Space  : {free}</b>\n"
        f"<b>├🔺 Total Upload         : {sent}</b>\n"
        f"<b>├🔻 Total Download    : {recv}</b>\n"
        f"<b>├🖥 CPU   : {cpuUsage}%</b>\n"
        f"<b>├⚙️ RAM  : {memory}%</b>\n"
        f"<b>├💿 DISK  : {disk}%</b>\n"
	f"<b>╰───────────BOT STATISTICS─</b>"
    )
    await m.reply_text(text=stats, quote=True)


@mergeApp.on_message(
    filters.command(["broadcast"])
    & filters.private
    & filters.user(Config.OWNER_USERNAME))
	
async def broadcast_handler(c: Client, m: Message):
    msg = m.reply_to_message
    userList = await database.broadcast()
    len = userList.collection.count_documents({})
    status = await m.reply_text(text=BROADCAST_MSG.format(str(len), "0"), quote=True)
    success = 0
    for i in range(len):
        try:
            uid = userList[i]["_id"]
            if uid != int(Config.OWNER):
                await msg.copy(chat_id=uid)
            success = i + 1
            await status.edit_text(text=BROADCAST_MSG.format(len, success))
            LOGGER.info(f"Message sent to {userList[i]['name']} ")
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await msg.copy(chat_id=userList[i]["_id"])
            LOGGER.info(f"Message sent to {userList[i]['name']} ")
        except InputUserDeactivated:
            await database.deleteUser(userList[i]["_id"])
            LOGGER.info(f"{userList[i]['_id']} - {userList[i]['name']} : deactivated\n")
        except UserIsBlocked:
            await database.deleteUser(userList[i]["_id"])
            LOGGER.info(
                f"{userList[i]['_id']} - {userList[i]['name']} : blocked the bot\n"
            )
        except PeerIdInvalid:
            await database.deleteUser(userList[i]["_id"])
            LOGGER.info(
                f"{userList[i]['_id']} - {userList[i]['name']} : user id invalid\n"
            )
        except Exception as err:
            LOGGER.warning(f"{err}\n")
        await asyncio.sleep(3)
    await status.edit_text(
        text=BROADCAST_MSG.format(len, success)
        + f"**Failed: {str(len-success)}**\n\n📡 Broadcast completed sucessfully.",)


#####
@mergeApp.on_message(filters.command(["start"]) & filters.private)
async def start_handler(c: Client, m: Message):
    if m.text.startswith("/start ") and len(m.text) > 7:
        user_id = m.from_user.id
        try:
            ad_msg = b64_to_str(m.text.split("/start ")[1])
            if int(user_id) != int(ad_msg.split(":")[0]):
                await c.send_message(
                    m.chat.id,
                    f"<b>ℹ️ Hi {m.from_user.mention},\nYour verification is invalid, click on below button and complete the verification to get access.</b>",
                    reply_to_message_id=m.id,
                )
                return
            if int(ad_msg.split(":")[1]) < get_current_time():
                await c.send_message(
                    m.chat.id,
                    f"<b>ℹ️ Hi {m.from_user.mention},\nYour verification is invalid, click on below button and complete the verification to get access.</b>",
                    reply_to_message_id=m.id,
                )
                return
            if int(ad_msg.split(":")[1]) > int(get_current_time() + 86400):  #Timeout
                await c.send_message(
                    m.chat.id,
                    "**Dont try to be over smart**",
                    reply_to_message_id=m.id,
                )
                return
            query = {"user_id": user_id}
            collection.update_one(
                query, {"$set": {"time_out": int(ad_msg.split(":")[1])}}, upsert=True
            )
            await c.send_message(
                m.chat.id,
                f"<b>Hurray 😁 {m.from_user.mention}!\nNow you are successfully verified to use this bot,\n\nHit /help to find out more about how to use me to my full potential.</b>",
                reply_to_message_id=m.id,
            )
            return
        except BaseException:
            await c.send_message(
                m.chat.id,
                "**Invalid Token**",
                reply_to_message_id=m.id,
            )
            return
		
    res = await m.reply_text(
        text=f"""<b>ℹ️ Hi {m.from_user.first_name},
I'm merger and extractor bot,
I can merge files, videos, audios, subtitles; in one video or file
and I can also extract that too.

Hit /help to learn, how to use this bot.</b>""",
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📢 Paid Promotion", url=f"https://t.me/{paid_promotion}")],
                [
                    InlineKeyboardButton("⛅ More Bots", url="https://t.me/jr_bots"),
                    InlineKeyboardButton("🌨️ Developer", url=f"https://t.me/StupidBoi69"),
                ],
                [InlineKeyboardButton("📴 Close", callback_data="close")],
            ]
        ),
    )

'''
    res = await m.reply_text(
        text=f"""<b>
Hi There; {m.from_user.mention}!

I'm merge bot, I can merge videos / audios / subtitles.
And, I am also capable of extracting <u>audios</u> and <u>subtitles</u> from the video.

Hit /help to find out more about how to use me to my full potential.</b>""",
        quote=True,
    )
'''

@mergeApp.on_message(
    (filters.document | filters.video | filters.audio) & filters.private)
async def files_handler(c: Client, m: Message):
    user_id = m.from_user.id
    uid = m.from_user.id
    user = UserSettings(user_id, m.from_user.first_name)
    
    if Config.PAID_BOT.upper() == "YES":
        result = collection.find_one({"user_id": uid})
        if result is None:
            ad_code = str_to_b64(f"{uid}:{str(get_current_time() + 86400)}") #Timeout
            ad_url = shorten_url(f"https://t.me/{bot_username}?start={ad_code}") 
            await c.send_message(
                m.chat.id,
                f"""<b>ℹ️ Hi {m.from_user.mention},
Your verification is expired, click on below button and complete the verification to get access.</b>""",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton("↪️ Get free access for 24-hrs ↩️", url=ad_url)
                    ]]
                ),
                reply_to_message_id=m.id,
            )
            return
        elif int(result["time_out"]) < get_current_time():
            ad_code = str_to_b64(f"{uid}:{str(get_current_time() + 86400)}") #Timeout
            ad_url = shorten_url(f"https://t.me/{bot_username}?start={ad_code}") 
            await c.send_message(
                m.chat.id,
                f"""<b>ℹ️ Hi {m.from_user.mention},
Your verification is expired, click on below button and complete the verification to get access.</b>""",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton("↪️ Get free access for 24-hrs ↩️", url=ad_url)
                    ]]
                ),
                reply_to_message_id=m.id,
            )
            return
        elif int(result["time_out"]) < get_current_time():
            ad_code = str_to_b64(f"{uid}:{str(get_current_time() + 86400)}") #Timeout
            ad_url = shorten_url(f"https://t.me/{bot_username}?start={ad_code}")
            await c.send_message(
                m.chat.id,
                f"""<b>ℹ️ Hi {m.from_user.mention},
Your verification is expired, click on below button and complete the verification to get access.</b>""",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton("↪️ Get free access for 24-hrs ↩️", url=ad_url)
                    ]]
                ),
                reply_to_message_id=m.id,
            )
            return
		
		
    if user.merge_mode == 4: # extract_mode
        return
    input_ = f"downloads/{str(user_id)}/input.txt"
    if os.path.exists(input_):
        await m.reply_text("**Sorry Bro,\nAlready One process in Progress!\nDon't Spam.**")
        return
    media = m.video or m.document or m.audio
    if media.file_name is None:
        await m.reply_text("File Not Found")
        return
    currentFileNameExt = media.file_name.rsplit(sep=".")[-1].lower()
    if currentFileNameExt in "conf":
        await m.reply_text(
            text="**💾 Config file found, Do you want to save it?**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Yes", callback_data=f"rclone_save"),
                        InlineKeyboardButton("No", callback_data="rclone_discard"),
                    ]
                ]
            ),
            quote=True,
        )
        return


    # if MERGE_MODE.get(user_id) is None:
    #     userMergeMode = database.getUserMergeSettings(user_id)
    #     if userMergeMode is not None:
    #         MERGE_MODE[user_id] = userMergeMode
    #     else:
    #         database.setUserMergeMode(uid=user_id, mode=1)
    #         MERGE_MODE[user_id] = 1

    if user.merge_mode == 1:

        if queueDB.get(user_id, None) is None:
            formatDB.update({user_id: currentFileNameExt})
        if formatDB.get(
            user_id, None
        ) is not None and currentFileNameExt != formatDB.get(user_id):
            await m.reply_text(
                f"**First you sent a {formatDB.get(user_id).upper()} file so now send only that type of file.**",
                quote=True,
            )
            return
        if currentFileNameExt not in VIDEO_EXTENSIONS:
            await m.reply_text(
                "**This Video Format not Allowed!\nOnly send MP4 or MKV or WEBM.**",
                quote=True,
            )
            return
        editable = await m.reply_text("Please Wait ...", quote=True)
        MessageText = "**Okay,\nNow Send Me Next Video or Press **Merge Now** Button!**"

        if queueDB.get(user_id, None) is None:
            queueDB.update({user_id: {"videos": [], "subtitles": [], "audios": []}})
        if (
            len(queueDB.get(user_id)["videos"]) >= 0
            and len(queueDB.get(user_id)["videos"]) < 10
        ):
            queueDB.get(user_id)["videos"].append(m.id)
            queueDB.get(m.from_user.id)["subtitles"].append(None)

            # LOGGER.info(
            #     queueDB.get(user_id)["videos"], queueDB.get(m.from_user.id)["subtitles"]
            # )

            if len(queueDB.get(user_id)["videos"]) == 1:
                reply_ = await editable.edit(
                    "**Send me some more videos to merge them into single file**",
                    reply_markup=InlineKeyboardMarkup(
                        bMaker.makebuttons(["Cancel"], ["cancel"])
                    ),
                )
                replyDB.update({user_id: reply_.id})
                return
            if queueDB.get(user_id, None)["videos"] is None:
                formatDB.update({user_id: currentFileNameExt})
            if replyDB.get(user_id, None) is not None:
                await c.delete_messages(
                    chat_id=m.chat.id, message_ids=replyDB.get(user_id)
                )
            if len(queueDB.get(user_id)["videos"]) == 10:
                MessageText = "**Okay, Now Just Press **Merge Now** Button Plox!**"
            markup = await makeButtons(c, m, queueDB)
            reply_ = await editable.edit(
                text=MessageText, reply_markup=InlineKeyboardMarkup(markup)
            )
            replyDB.update({user_id: reply_.id})
        elif len(queueDB.get(user_id)["videos"]) > 10:
            markup = await makeButtons(c, m, queueDB)
            await editable.text(
                "Max 10 videos allowed", reply_markup=InlineKeyboardMarkup(markup)
            )

    elif user.merge_mode == 2:
        editable = await m.reply_text("Please Wait ...", quote=True)
        MessageText = (
            "**Okay,\nNow Send Me Some More <u>Audios</u> or Press **Merge Now** Button!**"
        )

        if queueDB.get(user_id, None) is None:
            queueDB.update({user_id: {"videos": [], "subtitles": [], "audios": []}})
        if len(queueDB.get(user_id)["videos"]) == 0:
            queueDB.get(user_id)["videos"].append(m.id)
            # if len(queueDB.get(user_id)["videos"])==1:
            reply_ = await editable.edit(
                text="**Now, Send all the audios you want to merge**",
                reply_markup=InlineKeyboardMarkup(
                    bMaker.makebuttons(["Cancel"], ["cancel"])
                ),
            )
            replyDB.update({user_id: reply_.id})
            return
        elif (
            len(queueDB.get(user_id)["videos"]) >= 1
            and currentFileNameExt in AUDIO_EXTENSIONS
        ):
            queueDB.get(user_id)["audios"].append(m.id)
            if replyDB.get(user_id, None) is not None:
                await c.delete_messages(
                    chat_id=m.chat.id, message_ids=replyDB.get(user_id)
                )
            markup = await makeButtons(c, m, queueDB)

            reply_ = await editable.edit(
                text=MessageText, reply_markup=InlineKeyboardMarkup(markup)
            )
            replyDB.update({user_id: reply_.id})
        else:
            await m.reply("**This Filetype is not valid**")
            return

    elif user.merge_mode == 3:

        editable = await m.reply_text("Please Wait ...", quote=True)
        MessageText = "**Okay,\nNow Send Me Some More <u>Subtitles</u> or Press **Merge Now** Button!**"
        if queueDB.get(user_id, None) is None:
            queueDB.update({user_id: {"videos": [], "subtitles": [], "audios": []}})
        if len(queueDB.get(user_id)["videos"]) == 0:
            queueDB.get(user_id)["videos"].append(m.id)
            # if len(queueDB.get(user_id)["videos"])==1:
            reply_ = await editable.edit(
                text="Now, Send all the subtitles you want to merge",
                reply_markup=InlineKeyboardMarkup(
                    bMaker.makebuttons(["Cancel"], ["cancel"])
                ),
            )
            replyDB.update({user_id: reply_.id})
            return
        elif (
            len(queueDB.get(user_id)["videos"]) >= 1
            and currentFileNameExt in SUBTITLE_EXTENSIONS
        ):
            queueDB.get(user_id)["subtitles"].append(m.id)
            if replyDB.get(user_id, None) is not None:
                await c.delete_messages(
                    chat_id=m.chat.id, message_ids=replyDB.get(user_id)
                )
            markup = await makeButtons(c, m, queueDB)

            reply_ = await editable.edit(
                text=MessageText, reply_markup=InlineKeyboardMarkup(markup)
            )
            replyDB.update({user_id: reply_.id})
        else:
            await m.reply("This Filetype is not valid")
            return


@mergeApp.on_message(filters.photo & filters.private)
async def photo_handler(c: Client, m: Message):
    user = UserSettings(m.chat.id, m.from_user.first_name)
    # if m.from_user.id != int(Config.OWNER):
    if not user.allowed:
        res = await m.reply_text(
            text=f"""<b>ℹ️ Hi {m.from_user.first_name},
Unfortunately you can't use me, Contact @StupidBoi69</b>""",
            quote=True,
        )
        del user
        return
    thumbnail = m.photo.file_id
    msg = await m.reply_text("**⏺️ Saving Thumbnail....**", quote=True)
    user.thumbnail = thumbnail
    user.set()
    # await database.saveThumb(m.from_user.id, thumbnail)
    LOCATION = f"downloads/{m.from_user.id}_thumb.jpg"
    await c.download_media(message=m, file_name=LOCATION)
    await msg.edit_text(text="**⏺️ Custom Thumbnail Saved!**")
    del user


@mergeApp.on_message(filters.command(["extract"]) & filters.private)
async def media_extracter(c: Client, m: Message):
    user = UserSettings(uid=m.from_user.id, name=m.from_user.first_name)
    if not user.allowed:
        return
    if user.merge_mode == 4:
        if m.reply_to_message is None:
            await m.reply(text="<b>Reply /extract to a video or document file</b>")
            return
        rmess = m.reply_to_message
        if rmess.video or rmess.document:
            media = rmess.video or rmess.document
            mid=rmess.id
            file_name = media.file_name
            if file_name is None:
                await m.reply("**File name not found; Contact @StupidBoi69**")
                return
            markup = bMaker.makebuttons(
                set1=["Video", "Audio", "Subtitle", "Cancel"],
                set2=[f"extract_video_{mid}", f"extract_audio_{mid}", f"extract_subtitle_{mid}", 'cancel'],
                isCallback=True,
                rows=2,
            )
            await m.reply(
                text="**Choose from below what you want to extract?**",
                quote=True,
                reply_markup=InlineKeyboardMarkup(markup),
            )
    else:
        await m.reply(
            text="<b>Change settings and set mode to extract\nthen use /extract command</b>"
        )


@mergeApp.on_message(filters.command(["help"]) & filters.private)
async def help_msg(c: Client, m: Message):
    await m.reply_text(
        text="""<b>Follow These Steps:

1) Send me the custom thumbnail (required).
2) Go to settings and choose the merge mode.
3) Send a video then send videos / audios / subtitles which you want to merge.
3) After sending all files select merge options.
4) Select the upload mode.
5) Select rename if you want to give custom file name else press default.

Now, hit /about to learn more about this bot. </b>""",
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("📴 Close", callback_data="close")]]
        ),
    )


@mergeApp.on_message(filters.command(["about"]) & filters.private)
async def about_handler(c: Client, m: Message):
    await m.reply_text(
        text="""<b>
────────────────────────
<u>Features:</u>

-Ban/Unban users
-Extract audios and subtitles
-Merge videos / audios / subtitles
-Merge Up to 10 Videos in One
-Merge 2GB+ files (4GB Support)
-Upload as Documents/Video
-Custom Thumbnail Support
-Owner Can Broadcast Message to All Users
────────────────────────
<u>What's Special for Owner:</u>

- Added token based verification authorisation system. (for earning purpose)
────────────────────────

-If anyone wants to purchase bot for earning; Then contact @StupidBoi69</b>
		""",
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Purchase Premium Membership", url=f"https://t.me/{Config.OWNER_USERNAME}")],
                [
                    InlineKeyboardButton(
                        "Source Code", url=f"www.google.com"
                    ),
                    InlineKeyboardButton(
                        "Feedback", url=f"https://t.me/{Config.OWNER_USERNAME}"
                    ),
                ],
                [InlineKeyboardButton("📴 Close", callback_data="close")],
            ]
        ),
    )


@mergeApp.on_message(
    filters.command(["savethumb", "setthumb", "savethumbnail"]) & filters.private
)
async def save_thumbnail(c: Client, m: Message):
    if m.reply_to_message:
        if m.reply_to_message.photo:
            await photo_handler(c, m.reply_to_message)
        else:
            await m.reply(text="Please reply to a valid photo")
    else:
        await m.reply(text="Please reply to a message")
    return


@mergeApp.on_message(filters.command(["showthumbnail"]) & filters.private)
async def show_thumbnail(c: Client, m: Message):
    try:
        user = UserSettings(m.from_user.id, m.from_user.first_name)
        thumb_id = user.thumbnail
        LOCATION = f"downloads/{str(m.from_user.id)}_thumb.jpg"
        if os.path.exists(LOCATION):
            await m.reply_photo(
                photo=LOCATION, caption="**🖼️ Your custom thumbnail**", quote=True
            )
        elif thumb_id is not None :
            await c.download_media(message=str(thumb_id), file_name=LOCATION)
            await m.reply_photo(
                photo=LOCATION, caption="**🖼️ Your custom thumbnail**", quote=True
            )
        else: 
            await m.reply_text(text="**❌ Custom thumbnail not found**", quote=True)
        del user
    except Exception as err:
        LOGGER.info(err)
        await m.reply_text(text="**❌ Custom thumbnail not found**", quote=True)


@mergeApp.on_message(filters.command(["deletethumbnail"]) & filters.private)
async def delete_thumbnail(c: Client, m: Message):
    try:
        user = UserSettings(m.from_user.id, m.from_user.first_name)
        user.thumbnail = None
        user.set()
        if os.path.exists(f"downloads/{str(m.from_user.id)}"):
            os.remove(f"downloads/{str(m.from_user.id)}")
            await m.reply_text("**✅ Deleted Sucessfully**", quote=True)
            del user
        else: raise Exception("Thumbnail file not found")
    except Exception as err:
        await m.reply_text(text="**❌ Custom thumbnail not found**", quote=True)

@mergeApp.on_message(filters.command(["ban","unban"]) & filters.private)
async def ban_user(c:Client,m:Message):
    incoming=m.text.split(' ')[0]
    if incoming == '/ban':
        if m.from_user.id == int(Config.OWNER):
            try:
                abuser_id = int(m.text.split(" ")[1])
                if abuser_id == int(Config.OWNER):
                    await m.reply_text("**I can't ban you master,\nPlease don't abandon me.**",quote=True)
                else:
                    try:
                        user_obj: User = await c.get_users(abuser_id)
                        udata  = UserSettings(uid=abuser_id,name=user_obj.first_name)
                        udata.banned=True
                        udata.allowed=False
                        udata.set()
                        await m.reply_text(f"**Pooof, {user_obj.first_name} has been BANNED**",quote=True)
                        acknowledgement = f"""<b>
Dear {user_obj.first_name},
I found your messages annoying and forwarded them to our team of moderators for inspection. The moderators have confirmed the report and your account is now banned.
While the account is banned, you will not be able to do certain things, like merging videos/audios/subtitles or extract audios from Telegram media.

Your account can be released only by @{Config.OWNER_USERNAME}.</b>"""
                        try:
                            await c.send_message(
                                chat_id=abuser_id,
                                text=acknowledgement
                            )
                        except Exception as e:
                            await m.reply_text(f"An error occured while sending acknowledgement\n\n{e}",quote=True)
                            LOGGER.error(e)
                    except Exception as e:
                        LOGGER.error(e)
            except:
                await m.reply_text("<b>Command:\n/unban <user_id>\n\nUsage:\nuser_id: User ID of the user</b>",quote=True,parse_mode=enums.parse_mode.ParseMode.MARKDOWN)
        else:
            await m.reply_text("<b>Only for OWNER\nCommand:\n/unban <user_id>\n\nUsage:\nuser_id: User ID of the user</b>",quote=True,parse_mode=enums.parse_mode.ParseMode.MARKDOWN)
        return
    elif incoming == '/unban':
        if m.from_user.id == int(Config.OWNER):
            try:
                abuser_id = int(m.text.split(" ")[1])
                if abuser_id == int(Config.OWNER):
                    await m.reply_text("**I can't ban you master,\nPlease don't abandon me.**",quote=True)
                else:
                    try:
                        user_obj: User = await c.get_users(abuser_id)
                        udata  = UserSettings(uid=abuser_id,name=user_obj.first_name)
                        udata.banned=False
                        udata.allowed=True
                        udata.set()
                        await m.reply_text(f"**Pooof, {user_obj.first_name} has been UN_BANNED**",quote=True)
                        release_notice = f"""<b>
Good news {user_obj.first_name}, the ban has been uplifted on your account. You're free as a bird!</b>"""
                        try:
                            await c.send_message(
                                chat_id=abuser_id,
                                text=release_notice
                            )
                        except Exception as e:
                            await m.reply_text(f"An error occured while sending release notice\n\n{e}",quote=True)
                            LOGGER.error(e)                      
                    except Exception as e:
                        LOGGER.error(e)
            except:
                await m.reply_text("<b>Command:\n/unban <user_id>\n\nUsage:\nuser_id: User ID of the user</b>",quote=True,parse_mode=enums.parse_mode.ParseMode.MARKDOWN)
        else:
            await m.reply_text("<b>Only for OWNER\nCommand:\n/unban <user_id>\n\nUsage:\nuser_id: User ID of the user</b>",quote=True,parse_mode=enums.parse_mode.ParseMode.MARKDOWN)
        return
async def showQueue(c: Client, cb: CallbackQuery):
    try:
        markup = await makeButtons(c, cb.message, queueDB)
        await cb.message.edit(
            text="**Okay,\nNow Send Me Next Video or Press Merge Now Button!**",
            reply_markup=InlineKeyboardMarkup(markup),
        )
    except ValueError:
        await cb.message.edit("**Send Some more videos**")
    return


async def delete_all(root):
    try:
        shutil.rmtree(root)
    except Exception as e:
        LOGGER.info(e)


async def makeButtons(bot: Client, m: Message, db: dict):
    markup = []
    user = UserSettings(m.chat.id, m.chat.first_name)
    if user.merge_mode == 1:
        for i in await bot.get_messages(
            chat_id=m.chat.id, message_ids=db.get(m.chat.id)["videos"]
        ):
            media = i.video or i.document or None
            if media is None:
                continue
            else:
                markup.append(
                    [
                        InlineKeyboardButton(
                            f"{media.file_name}",
                            callback_data=f"showFileName_{i.id}",
                        )
                    ]
                )

    elif user.merge_mode == 2:
        msgs: list[Message] = await bot.get_messages(
            chat_id=m.chat.id, message_ids=db.get(m.chat.id)["audios"]
        )
        msgs.insert(
            0,
            await bot.get_messages(
                chat_id=m.chat.id, message_ids=db.get(m.chat.id)["videos"][0]
            ),
        )
        for i in msgs:
            media = i.audio or i.document or i.video or None
            if media is None:
                continue
            else:
                markup.append(
                    [
                        InlineKeyboardButton(
                            f"{media.file_name}",
                            callback_data=f"tryotherbutton",
                        )
                    ]
                )

    elif user.merge_mode == 3:
        msgs: list[Message] = await bot.get_messages(
            chat_id=m.chat.id, message_ids=db.get(m.chat.id)["subtitles"]
        )
        msgs.insert(
            0,
            await bot.get_messages(
                chat_id=m.chat.id, message_ids=db.get(m.chat.id)["videos"][0]
            ),
        )
        for i in msgs:
            media = i.video or i.document or None

            if media is None:
                continue
            else:
                markup.append(
                    [
                        InlineKeyboardButton(
                            f"{media.file_name}",
                            callback_data=f"tryotherbutton",
                        )
                    ]
                )

    markup.append([InlineKeyboardButton("🔀 Merge Now", callback_data="merge")])
    markup.append([InlineKeyboardButton("🚮 Clear Files", callback_data="cancel")])
    return markup


LOGCHANNEL = Config.LOGCHANNEL
try:
    if Config.USER_SESSION_STRING is None:
        raise KeyError
    LOGGER.info("Starting USER Session")
    userBot = Client(
        name="merge-bot-user",
        session_string=Config.USER_SESSION_STRING,
        no_updates=True,
    )

except KeyError:
    userBot = None
    LOGGER.warning("No User Session, Default Bot session will be used")


if __name__ == "__main__":
    # with mergeApp:
    #     bot:User = mergeApp.get_me()
    #     bot_username = bot.username
    try:
        with userBot:
            userBot.send_message(
                chat_id=int(LOGCHANNEL),
                text=f"<b>Bot booted with Premium Account,\n\nThanks for using <a href='https://t.me/{bot_username}'>this bot</a>",
                disable_web_page_preview=True,
            )
            user = userBot.get_me()
            Config.IS_PREMIUM = user.is_premium
    except Exception as err:
        LOGGER.error(f"{err}")
        Config.IS_PREMIUM = False
        pass

    mergeApp.run()
