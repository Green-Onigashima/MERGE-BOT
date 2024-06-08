import os


class Config(object):
    API_HASH =("0b691c3e86603a7e34aae0b5927d725a")
    BOT_TOKEN = ("6850585424:AAH8A5F9FgvEua16inW0jKEDqWkFpfobScM")
    TELEGRAM_API = ("7324525")
    OWNER = ("1895952308")
    OWNER_USERNAME = ("StupidBoi69")
    PASSWORD = ("6342")
    DATABASE_URL = ("mongodb+srv://jidap30478:jidap30478@cluster0.l7j63yf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    LOGCHANNEL = ("-1001788923244")  # Add channel id as -100 + Actual ID
    GDRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "root")
    USER_SESSION_STRING = os.environ.get("USER_SESSION_STRING", None)
    IS_PREMIUM = True
    START_PIC = ("https://graph.org/file/b2e20c24139dd72dbac09.jpg")
    MODES = ["video-video", "video-audio", "video-subtitle", "extract-streams"]
