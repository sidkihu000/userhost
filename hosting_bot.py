# -*- coding: utf-8 -*-
"""
================================━━━━━━━━================================
                 ✨ SID PREMIUM MASTER USERBOT ENGINE ✨
================================━━━━━━━━================================
Core Architecture: pyTelegramBotAPI (Hoster) + Telethon (Live Runtimes)
Features: OTP/2FA, Dynamic Animations, 100+ Commands, Full Raid Integrated
"""

import os
import sys
import time
import json
import logging
import sqlite3
import asyncio
import atexit
import psutil
import threading
import random
import shutil
import re
import secrets
from datetime import datetime

import telebot
from telebot import types
from flask import Flask, request, jsonify
from threading import Thread

# Userbot Dependencies
try:
    import yt_dlp
    import qrcode
    from gtts import gTTS
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "qrcode", "gTTS", "requests"])
    import yt_dlp
    import qrcode
    from gtts import gTTS
    import requests

import telethon
from telethon import TelegramClient, events
from telethon.errors import (
    SessionPasswordNeededError, PhoneCodeInvalidError,
    PasswordHashInvalidError, PhoneCodeExpiredError, FloodWaitError
)
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.types import ChatAdminRights
from telethon.sessions import StringSession

# ──────────────────────────────────────────────────────────────────────────────
# SYSTEM LOGGING & PATHS
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SID-ENGINE] - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("SidHostMaster")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
RUNTIMES_DIR = os.path.join(BASE_DIR, 'sid_runtimes')
DATA_STORAGE_DIR = os.path.join(BASE_DIR, 'sid_metadata')
DATABASE_PATH = os.path.join(DATA_STORAGE_DIR, 'sid_hosting.db')

os.makedirs(RUNTIMES_DIR, exist_ok=True)
os.makedirs(DATA_STORAGE_DIR, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# WEB LAYER & CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────
web_app = Flask('SidHostServer')

@web_app.route('/')
def health_check(): return "<h3>Sid Engine Core Status: ONLINE 🟢</h3>", 200
def initialize_keepalive_server(): web_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

BOT_TOKEN = '8760438442:AAHODDkjr0rclSB7rnR67ac3UDX8tXYwCKY'
DEFAULT_API_ID = 32082988
DEFAULT_API_HASH = "a81844a473550947cfff864a8c7489cd"

BOY_PRESETS = ["SID KENG 👑", "DEADLY SID 💀", "REBEL SID 🔥", "SID RULE SERVER 😎"]
GIRL_PRESETS = ["SID BADDIE 🎀", "ANGEL SID ✨", "ROSE SID 🌸", "CUTE SID 💅🏻"]

# ─── FULL RAID TEXT ARRAYS ───
RAPIST_MESSAGES = [
    "Gᴜʟᴀᴍɪ ᴋʀ ——➤(🎀)", "Tᴇʀɪ Mᴀ Cʜᴜᴅɪ ——➤(🎀)", "Sᴀʟᴀᴍ Tʜᴏᴋ ——➤(🎀)", "Cʜɪɴᴀᴀʀ ——➤(🎀)",
    "Mᴀᴢᴅᴏᴏʀ ——➤(🎀)", "Hᴀᴡᴀʙᴀᴢᴢ ——➤(🎀)", "𝐃ɪᴘᴇsʜ अब्बू  ʙᴏʟ——➤(🎀)", "Tmkl ——➤(🎀)",
    "Kᴀᴍᴢᴏʀ Kᴜᴛɪʏᴀ ——➤(🎀)", "Bʜᴇᴇᴋ Mᴀɴɢ ——➤(🎀)", "RɴᴅɪMᴏɴ ——➤(🎀)", "Cʜᴜᴅᴀɪ Kɪᴅᴅᴇ ——➤(🎀)",
    "Gʜᴀᴛɪʏᴀ Bᴇᴛᴀ ——➤(🎀)", "Tᴇʀᴀ Bᴀᴀᴘ x𝐃ɪᴘᴇsʜ ——➤(🎀)", "GAɴᴅ Mᴀʀᴀ ᴍᴜʟʟᴇ ——➤(🎀)",
    "Cʜᴜᴅᴇɢɪ Tᴇʀɪ MA ——➤(🎀)", "BɪᴛCʜ ——➤(🎀)", "HɪJᴅᴜSᴏɴ ——➤(🎀)", "Nᴀʟɪ Sᴀғ Kᴀʀ ᴊAᴋᴇ ——➤(🎀)",
    "GʜɪNᴏɴɪ Rɴ Dz ——➤(🎀)", "Cʜᴏᴛɪ Jᴀᴀᴛ ——➤(🎀)", "TᴇRɪ Mᴀ Kalwɪ ——➤(🎀)", "HɪJᴀB PᴇʜᴇN ——➤(🎀)", "Tᴍᴋc Mᴇ KᴏYʟA ——➤(🎀)"
]

HOMIES_MESSAGES = [
    "𝐑𝐄𝐁𝐄𝐋 𝐁𝐀𝐀𝐏 👑", "𝐀𝐊𝐒𝐇𝐔 𝐊𝐄𝐍𝐆 🔥", "𝐃𝐈𝐏𝐄𝐒𝐇 𝐆𝐀𝐖𝐃 😈", "𝐒𝐈𝐃 𝐑𝐔𝐋𝐄 𝐒𝐄𝐑𝐕𝐄𝐑 😎",
    "𝐀𝐑𝐘𝐀𝐍 पिताश्री 😇", "𝐃𝐄𝐀𝐃𝐋𝐘 𝐌𝐀𝐑𝐂𝐎 💀", "𝐒𝐇𝐈𝐕 𝐁𝐁𝐔  💥", "𝐁𝐇𝐀𝐕𝐈𝐒𝐇𝐘𝐀 𝐒𝐇𝐄𝐑𝐑 🦁",
    "𝐆𝐎𝐃 𝐀𝐑𝐄𝐒 🛐", "𝐍𝐈𝐒𝐇𝐀𝐍𝐓 𝐁𝐀𝐃𝐃𝐈𝐄 🎀", "𝐏𝐎𝐒𝐄𝐈𝐃𝐎𝐍 𝐓𝐇𝐄 𝐆𝐑𝐄𝐀𝐓 🌚", "𝐌𝐈𝐊𝐄𝐘 𝐌𝐔𝐓𝐇𝐌𝐀𝐑𝐄 ✊🏻💦",
    "𝐌𝐔𝐙𝐀𝐍 𝐏𝐀𝐈👺", "𝐒𝐏𝐀𝐍𝐂𝐄𝐑 𝐆𝐎𝐀𝐓 🐐", "𝐑𝐄𝐗𝐗𝐘 𝐁𝐈𝐇𝐀𝐑𝐈 😈💪🏻", "𝐃𝐎𝐌𝐀 𝐏𝐀𝐇𝐀𝐃𝐈 🏳️‍🌈",
    "𝐀𝐁𝐇𝐈 𝐁𝐇𝐀𝐈 💋", "𝐕𝐀𝐈𝐁𝐇𝐀𝐕 𝐁𝐇𝐀𝐈 💋", "𝐘𝐀𝐒𝐇 𝐂𝐇𝐇𝐀𝐊𝐀 👌🏻🎀"
]

DIPESH_MESSAGES = [
    "Teri ma Kali randy 💔🦋", "Chal Ma Chuda mere se 🖕", "Chal 𝐃ɪᴘᴇsʜ ko Baap Bol",
    "Teri ma mar du randyke 😂🦋", "KHAKE BURGUR TERI MA CHODU GHAR GHAR", "BAAP BOL MUJHE GAREEB",
    "Teri ma bhooki randy", "Chal na gawar", "Hakla kyun rha tu😂", "𝒯𝑒𝑟𝑖 𝑀𝑎 𝐺𝑎𝑑ℎ𝑒 𝐾𝑎 𝐿𝑜𝑑𝑎 𝐿𝑒𝑡𝑖 𝒉𝒆𝒉𝒆😂",
    "Tᴇʀᴀ ʙᴀᴀᴘ Sᴛᴀᴛɪᴏɴ Mᴀɪ ʟᴀɴɢᴅᴀ Cʜᴀʟᴛᴀ 😂", "𝘛𝘦𝘳𝘪 𝘉𝘦𝘩𝘦𝘯 𝘒...𝘒𝘩𝘶𝘭𝘦𝘦 𝘈𝘢𝘮 𝘗𝘦𝘭𝘶 𝘒𝘶𝘵𝘪𝘺𝘢 𝘣𝘢𝘯𝘢𝘬𝘦 REBEL Bʜɪ TᴇRᴇ JᴀIsA KʀᴛA TʜA Usʜᴇ ʜɪᴊᴅᴀ ʙᴀɴᴀ ᴅɪʏᴀ😂",
    "Cʜᴜᴘ Bɪʜᴀʀɪ ʙᴀᴜɴᴇ😂", "𝑻𝒆𝒓𝒊 𝑴𝒂 𝑺𝒂𝒕𝒓𝒂𝒏𝒈𝒊 𝑹𝒂𝒏𝒅🩷🤍🩶🖤💜👌🏻", "Cʜᴜᴅᴋᴇ Pɢʟ Bᴀɴ Gʏᴀ ᴄʏᴀ 😂",
    "HɪᴊDᴏ Kᴇ RᴀJᴀ TᴜJʜE MᴇRᴇ LᴀNᴅ Kɪ sᴀʟᴀᴍɪ 😂", "Zᴏᴏ Kᴇ GᴏRɪLᴀ Sᴇ TᴇRɪ Mᴀ CʜᴜDᴡAU Oʀ ʙᴀᴄᴄʜᴇ Kᴀ NᴀMᴇ ᴅᴜ LADCHT DAS",
    "GᴀO Kᴇ SᴀRᴘᴀNᴄH Nᴇ TᴇRɪ Mᴀ ᴄʜᴏᴅɪ😂", "Chup rndyk kone mein baith 😂😂😂",
    "Teri Maa Ke भोसड़े में Theater Kholke सैयारा चाला दूंगा 🔈🔈🔥🔥🔥🔥😂😂😂🔈🔈🔈",
    "_✍🏻 𝐘ᴇ 𝐃ᴇ𝐊ʜ ˢᶜʳⁱᵖᵗ ˡⁱᵏʰ ʳᵃʰᵃ ʰᵘ 𝐓ᴇʀɪ 𝐌ᴀA 𝐊ᴇ 𝐁ʜ𝐎sᴅᴇ 𝐌ᴇIɴ 😂😂😂", "SᴜAʀ TᴇRɪ MᴀA Kɪ CʜUᴛ 😌😌💤💤",
    "𝐓𝐔 𝐈𝐃𝐑 𝐂𝐎𝐌𝐄𝐁𝐀𝐂𝐊 𝐃𝐄𝐓𝐀 𝐑𝐄𝐇 𝐆𝐘𝐀 𝐔𝐃𝐇𝐑 𝐃ɪᴘᴇsʜ 𝐓ᴇʀ𝐈 𝐌ᴀA 𝐂ʜᴏᴅ 𝐆ʏA 🩷🩶🩵", "Choding ho rhi hai teri maa ki 😬👨🏻‍💻🔥",
    "Teri Maa Ki Chut Mein Loda Daluga Beta 🥵💯", "🧐 Teri maa ka bh🤪sda dikh rha hai 😎",
    " 😉🔥 Cya 😉🔥 re 😉 🔥 sapri 😉🔥 try 😉🔥 maa 😉🔥 tujh 😉🔥 nehlati 😉🔥 ny 😉🔥 ey 😉🔥 Cya 😉🔥",
    " Oye Madarchod Uth 😤😡🥵 Teri Maa Ka Choding Tem 😈👻🦶🏻", " Teri Maa Ko Football ⚽ bnake uske 𝗕𝗛😈𝗦𝗗𝗘 pe laat 🦶🏻 marunga 🤩🔥",
    "इस मंगलवार को ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴋᴀ ʙʜᴀɴᴅᴀʀᴀ ʜᴏɢᴀ 😈😘👌🏻", " TᗴᖇI ᗰᗩᗩ Kᗩ ᗷOOᖇ ᗷᗴTᗩ 🤣🤮🔥😏🔥😂💞🌧️",
    "𝐌𝐀𝐀 𝐊𝐄 𝐋𝐎𝐃𝐄 🤮", "𝗣𝗘𝗛𝗟𝗘 𝗧𝗘𝗥𝗜 𝗕𝗘𝗛𝗘𝗡 𝗖𝗛𝗢𝗗𝗨𝗚𝗔 𝗙𝗜𝗥 𝗧𝗘𝗥𝗜 𝗠𝗔A 😆😂😆🔥🤢😂🤍😤",
    "ƇӇƲƤ ƬЄƦƖ Mƛƛ Ƙƛ ƁӇƠƧƊƛ ♻️", " 𝘚𝘱𝘢𝘮𝘮𝘦𝘳 𝘣𝘢𝘯𝘦𝘨𝘢 𝘳𝘢𝘯𝘥𝘪𝘬𝘦 🤢🔥", " 𝐀𝐉𝐀 𝐌🇨 𝐁𝐀𝐍𝐀𝐔 𝐓𝐔𝐉𝐇𝐄 𝐒𝐏𝐀𝐌𝐌𝐄𝐑 👻💥🤍😹👑",
    "𝘣𝘰𝘭 𝐃ɪᴘᴇsʜ 𝘉𝘢𝘢𝘱 की जय 👑", " 😍 Teri 😡 Randi 🤪 Maa 😤 Ko 😎 Pel 😭 Dunga 😍",
    "Idhar Aa Beta 🤪💔 Teri Maa Chodu 😂😘", " Oye Mazdur kaam pe ja 🔥⛏️🔥⛏️⛏️🔥⛏️💞💞🔥💞⛏️🔥💞⛏️⛏️",
    "Teri Maa Chodne K liye Pura Gc Khada Hai 🥴😁🩷💯", " Teri Maa Bio Mein #Proudrandi 💔🥀 likhti hai 🤩🔥🩷",
    "Rndyk lund se utr 😩👏🏻", "Arey Yarr Apni Maa Matt Nangi Kar 😩🔥💞😩⛏️🔥🥀🤩💞😩🔥😩🩷💞",
    " Tu hasta reh gya yaaro mein 😁💯💔 Teri maa chudgyi baazaro mein 😂🌹",
    "Teri Maa Chudwa denge re 🪖🔥⛏️🥴🤪💔🩷💯😁😩💞", " 🩷 Gud ❤️ nyt 🧡 rndyk 💛 kal 🩵 Aaunga 💙 Teri 🖤 Maa 🩶 Chodne 🤍",
    " 🥶 Are 😱 Mc 😩 Ye 🤔 Kaise 🤪 Kiya 😏 Teri 😎 Maa 😬 Randi 🙄 Hai 🤮 100% 😂",
    "🩷🩵🤍🩶🖤❤️💚 Ye sare dill teri maa k naam beta 😂😜🔥", " Hat peche hat tera baap Rebel aya 😂😂🥴😹🤲🏻💪🏻",
    "Leave le rndyk psnd nai aya tu meko 🤢👎🏻", "Teri maa chodu 💯 if yes then reply to my message 💀💀💀💪🏻🔥💯👆🏻💔😂😂💔💔💔",
    "#𝐃ɪᴘᴇsʜ 𝘉𝘢𝘢𝘱 𝐊𝐎 𝐃𝐁𝐀 𝐍𝐇𝐈 𝐏𝐀R𝐄 ᴄʏᴀ?? 🥶🥱😂", "😹 Tᴇʀɪ 🤪 RᴀNᴅɪ 😫 MᴀA 🤗 Kᴇ 🤢 BᴜR 🤣 Pᴇ 😤 LᴀAᴛ 🙄 MᴀR 😆 Kᴇ 😍 Tᴇʀɪ 😍 BᴇHᴇN 😈 CʜᴏOᴅ 😅 DᴜGᴀ 🤩",
    "GᴀRᴇᴇʙ Ghar Ke Ladke Baap Log Ke Gc Mein Kya Krr Rha 🤢👞", " 🔮 𝐘𝐄 𝐃𝐄𝐊𝐇 𝐉𝐀D𝐔 𝐒𝐄 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐂𝐇𝐎𝐃 𝐃𝐈y𝐀 😂🪄😂🪄",
    " Teri Maa Ko बाहुबली style mein chodunga 🥶💔🤪😹", "Tumhare Pitashree 𝐃ɪᴘᴇsʜ 💯🔥🗿🌙",
    " Tery behn bole fuck me 𝐃ɪᴘᴇsʜ daddy 😍🌹💋", " तेरी माँ 𝐃ɪᴘᴇsʜ पापा ki दीवानी Since 2k10 😂🖕🏻🔥", " Cover le सस्ती रंडी k काले बच्चे 🤢🤮🖕🏻🥀"
]

ATTACK_LIST = ["⚔️ Teri aukat nahi mujhse ladhne ki randike 😂🔥", "💥 Chal bhaag yahan se chutiye warna maar khayega 🤣⚔️", "🗡️ Tera baap aaya hai sunta nahi kya 👑😈"]
ROAST_LIST = ["🔥 Teri zindagi ek bakwas webseries ki tarah hai — 1 season mein flop 😂📺", "🤣 Bhai teri personality ek sada hua pyaz jaisi hai — khole toh aansu aaye 🧅💀", "😹 Tu itna bura lagta hai ke teri photo dekh ke mosquito bhi bhaag jata hai 🦟😂"]
DISS_LIST = ["🎤 Tera naam sun ke log mute kar dete hain khud ko 🔇😂", "💀 Tu diss kar raha hai — khud ko diss kar pehle 🪞😹", "🎙️ Teri rap jaisi hai — no flow no bars no future 🎵😂"]
WAR_LIST = ["⚔️ War shuru ho gayi — aur tu pehle hi haar gaya 😂🔥", "💣 Bhai main war mein nahi aata — main war khatam karne aata hoon 😈⚡", "🏴‍☠️ Tera jhanda uraya — apna wala lehraya 😎💀"]
SAVAGE_LIST = ["😈 Main savage hoon — tujhe explanation nahi deta 🔥💀", "💀 Teri feelings mere liye statistics hain — irrelevant 😂😈", "🔥 Main woh nahi hoon jo tujhe comfortable feel karaaye 😎💀"]

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 4: STATE MANAGEMENT SYSTEM
# ──────────────────────────────────────────────────────────────────────────────
GLOBAL_DB_LOCK = threading.Lock()
active_runtimes = {}
onboarding_states = {}

def execute_db_migration():
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS hosted_sessions
                         (user_id INTEGER PRIMARY KEY, session_key TEXT, gender TEXT, system_preset TEXT, api_id INTEGER, api_hash TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_metadata
                         (user_id INTEGER PRIMARY KEY, first_name TEXT, joined_at INTEGER, phone TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS sudo_users
                         (user_id INTEGER PRIMARY KEY)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS blocked_users
                         (user_id INTEGER PRIMARY KEY)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS welcome_video
                         (id INTEGER PRIMARY KEY, file_id TEXT, is_video_note INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS api_config
                         (id INTEGER PRIMARY KEY, api_id INTEGER, api_hash TEXT)''')
        conn.commit()
        conn.close()

execute_db_migration()
bot = telebot.TeleBot(BOT_TOKEN)

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 5: INTERACTIVE ANIMATION ENGINE UI
# ──────────────────────────────────────────────────────────────────────────────
class SidAnimationLibrary:
    @staticmethod
    def play_terminal_pulse(chat_id, target_msg_id, final_message_text, markup=None):
        frames = [
            "🟢 `[▱▱▱▱▱▱▱▱▱] Booting Sid Kernel...`",
            "🟡 `[▰▰▰▱▱▱▱▱▱] Injecting Modules...`",
            "🟠 `[▰▰▰▰▰▰▱▱▱] Bypassing Security...`",
            "🔴 `[▰▰▰▰▰▰▰▰▱] Establishing Uplink...`",
            "✅ `[▰▰▰▰▰▰▰▰▰] Link Established!`"
        ]
        def pipeline():
            try:
                for frame in frames:
                    bot.edit_message_text(frame, chat_id, target_msg_id, parse_mode='Markdown')
                    time.sleep(0.6)
                bot.edit_message_text(final_message_text, chat_id, target_msg_id, reply_markup=markup, parse_mode='Markdown')
            except Exception as e: logger.error(f"UI error: {e}")
        Thread(target=pipeline, daemon=True).start()

# ──────────────────────────────────────────────────────────────────────────────
# HOSTER DASHBOARD & OTP FLOW (improved with state-based handler)
# ──────────────────────────────────────────────────────────────────────────────

@bot.message_handler(commands=['start', 'menu', 'sid'])
def display_dashboard_interface(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("👦 Deploy Boy Userbot", callback_data="deploy_boy"),
        types.InlineKeyboardButton("👧 Deploy Girl Userbot", callback_data="deploy_girl"),
        types.InlineKeyboardButton("⚡ Server Telemetry", callback_data="telemetry"),
        types.InlineKeyboardButton("🛑 Terminate Container", callback_data="terminate")
    )
    markup.row(
        types.InlineKeyboardButton("📊 My Account", callback_data="my_account"),
        types.InlineKeyboardButton("📚 Commands", callback_data="cmd_list"),
        types.InlineKeyboardButton("📞 Support", callback_data="support")
    )
    welcome_text = f"👑 **SID PREMIUM USERBOT ARCHITECTURE** 👑\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✨ Welcome, {message.from_user.first_name}.\n\n» **Engine:** `v6.0-SID-DYNAMIC`\n» **Status:** `ONLINE & SECURE`\n\nSelect your deployment module:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data in ["deploy_boy", "deploy_girl"])
def trigger_deployment(call):
    bot.answer_callback_query(call.id)
    gender_choice = "BOY" if "boy" in call.data else "GIRL"
    onboarding_states[call.from_user.id] = {
        'step': 'PHONE_INPUT',
        'gender': gender_choice,
        'api_id': DEFAULT_API_ID,
        'api_hash': DEFAULT_API_HASH,
        'phone': None,
        'client': None,
        'phone_code_hash': None
    }
    bot.send_message(call.message.chat.id, f"📱 **SID {gender_choice} MODULE**\nEnter phone number with country code (e.g., `+919876543210`):", parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.from_user.id in onboarding_states)
def handle_onboarding(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text.strip() if message.text else ""

    if text.lower() == '/cancel':
        onboarding_states.pop(user_id, None)
        bot.send_message(chat_id, "❌ Registration cancelled.")
        return

    state = onboarding_states[user_id]

    if state['step'] == 'PHONE_INPUT':
        # Save phone and send OTP
        state['phone'] = text
        progress_msg = bot.send_message(chat_id, "`⚡ Generating SID runtime...`", parse_mode='Markdown')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            client = TelegramClient(os.path.join(RUNTIMES_DIR, f"temp_{user_id}"), state['api_id'], state['api_hash'], loop=loop)
            loop.run_until_complete(client.connect())
            state['client'] = client
            result = loop.run_until_complete(client.send_code_request(state['phone']))
            state['phone_code_hash'] = result.phone_code_hash
            state['step'] = 'OTP_INPUT'
            bot.delete_message(chat_id, progress_msg.message_id)
            bot.send_message(chat_id, f"📥 **OTP Sent to {state['phone']}**\nEnter code (spaces allowed):", parse_mode='Markdown')
        except Exception as e:
            bot.send_message(chat_id, f"❌ **Error:** `{e}`")
            onboarding_states.pop(user_id, None)

    elif state['step'] == 'OTP_INPUT':
        clean_code = text.replace(" ", "")
        client = state['client']
        loop = client.loop
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(client.sign_in(state['phone'], code=clean_code, phone_code_hash=state['phone_code_hash']))
            # Success → show preset selection
            select_preset_interface(chat_id, user_id)
        except SessionPasswordNeededError:
            state['step'] = 'PASSWORD_2FA_INPUT'
            bot.send_message(chat_id, "🔒 **2FA Detected**\nEnter your password:")
        except Exception as e:
            bot.send_message(chat_id, f"❌ **Fault:** `{e}`")
            onboarding_states.pop(user_id, None)

    elif state['step'] == 'PASSWORD_2FA_INPUT':
        client = state['client']
        loop = client.loop
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(client.sign_in(password=text))
            select_preset_interface(chat_id, user_id)
        except Exception as e:
            bot.send_message(chat_id, f"❌ **2FA Fault:** `{e}`")
            onboarding_states.pop(user_id, None)

def select_preset_interface(chat_id, user_id):
    gender = onboarding_states[user_id]['gender']
    presets = BOY_PRESETS if gender == "BOY" else GIRL_PRESETS
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, p in enumerate(presets):
        markup.add(types.InlineKeyboardButton(f"🎭 {p}", callback_data=f"finalize_{i}_{user_id}"))
    bot.send_message(chat_id, f"✅ **Authentication Successful!**\nChoose your personality:", reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith("finalize_"))
def finalize_and_deploy(call):
    _, index_str, target_uid_str = call.data.split("_")
    user_id = int(target_uid_str)
    if call.from_user.id != user_id:
        return bot.answer_callback_query(call.id, "❌ Not your session.")
    bot.answer_callback_query(call.id)

    state = onboarding_states.pop(user_id, None)
    if not state:
        return bot.send_message(call.message.chat.id, "❌ Session expired.")

    gender = state['gender']
    preset_choice = (BOY_PRESETS if gender == "BOY" else GIRL_PRESETS)[int(index_str)]

    client = state['client']
    stable_session = os.path.join(RUNTIMES_DIR, f"active_{user_id}")
    client.loop.run_until_complete(client.disconnect())

    src, dest = os.path.join(RUNTIMES_DIR, f"temp_{user_id}.session"), f"{stable_session}.session"
    if os.path.exists(src):
        if os.path.exists(dest):
            os.remove(dest)
        os.rename(src, dest)

    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO hosted_sessions VALUES (?, ?, ?, ?, ?, ?)',
                       (user_id, dest, gender, preset_choice, state['api_id'], state['api_hash']))
        cursor.execute('INSERT OR REPLACE INTO user_metadata (user_id, phone) VALUES (?, ?)',
                       (user_id, state['phone']))
        conn.commit()
        conn.close()

    p_msg = bot.send_message(call.message.chat.id, "`Initializing...`", parse_mode='Markdown')
    s_txt = f"🚀 **SID {gender} USERBOT DEPLOYED**\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n» **Identity:** `{preset_choice}`\n» **Status:** `ACTIVE`\n\nSend `.sid_menu` in any chat!"
    SidAnimationLibrary.play_terminal_pulse(call.message.chat.id, p_msg.message_id, s_txt)
    threading.Thread(target=deploy_live_userbot_runtime, args=(call.message.chat.id, user_id, gender, preset_choice), daemon=True).start()

# ──────────────────────────────────────────────────────────────────────────────
# CORE TELETHON USERBOT ENGINE (DYNAMIC FUNCTIONS)
# ──────────────────────────────────────────────────────────────────────────────
def deploy_live_userbot_runtime(chat_id, user_id, gender, preset_string):
    """
    Deploys a live userbot for a given user.
    chat_id: optional; if provided, status messages are sent to that chat.
    """
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH); cursor = conn.cursor()
        cursor.execute('SELECT session_key, api_id, api_hash FROM hosted_sessions WHERE user_id = ?', (user_id,))
        record = cursor.fetchone(); conn.close()
    if not record:
        if chat_id:
            bot.send_message(chat_id, "❌ Session record not found.")
        return
    session_key, api_id, api_hash = record

    # Determine if session_key is a file path or a string session
    if os.path.exists(session_key):
        session_file_base = session_key.replace(".session", "")
        client = TelegramClient(session_file_base, int(api_id), api_hash)
    else:
        client = TelegramClient(StringSession(session_key), int(api_id), api_hash)

    active_runtimes[user_id] = {'client': client, 'loop': asyncio.get_event_loop(), 'thread': threading.current_thread()}

    # ── ISOLATED USER STATE ──
    U_STATE = {
        'auth_users': set(), 'muted': {}, 'safe': {}, 'active_raids': {},
        'auto_react': None, 'original_profile': {}, 'start_time': time.time(),
        'spam_delay': 0.1, 'live_forwards': {}, 'gcmute_loops': {}, 'reply_modes': {}
    }

    async def _safe_edit(event, text):
        if event.out:
            return await event.edit(text)
        elif event.sender_id in U_STATE['auth_users']:
            try:
                await event.delete()
            except:
                pass
            return await client.send_message(event.chat_id, text, reply_to=event.reply_to_msg_id)

    async def get_target(event, arg):
        if event.is_reply:
            return (await event.get_reply_message()).sender_id
        if arg:
            try:
                return (await client.get_entity(arg)).id
            except:
                pass
        return None

    def is_authorized(event):
        return event.out or event.sender_id in U_STATE['auth_users']

    async def operational_lifecycle():
        await client.connect()
        try:
            await client(UpdateProfileRequest(first_name=preset_string.split()[0],
                                              about=f"Powered by SID Master Engine 👑 • {preset_string}"))
        except:
            pass

        # ── 1. DYNAMIC EFFECTS & ANIMATIONS ──
        @client.on(events.NewMessage(pattern=r"\.hack", outgoing=True))
        async def sid_hack(event):
            anims = [
                "💻 `Initializing SID Exploit Script...`",
                "💻 `Connecting to Target's Local IP...`",
                "💻 `Bypassing Security Firewalls... [▓▓░░░░]`",
                "💻 `Extracting Database... [▓▓▓▓▓░]`",
                "💻 `Decrypting Mainframe... [▓▓▓▓▓▓]`",
                f"👑 **HACK COMPLETE BY {preset_string}!**\n» System Compromised. Target Destroyed. 😈"
            ]
            for frame in anims:
                await event.edit(frame)
                await asyncio.sleep(0.8)

        @client.on(events.NewMessage(pattern=r"\.load", outgoing=True))
        async def sid_load(event):
            bar = ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]
            for i in range(1, 101, 15):
                frame = bar[(i//15)%len(bar)]
                await event.edit(f"⏳ **Loading Matrix:** `{frame} {i}%`")
                await asyncio.sleep(0.4)
            await event.edit(f"✅ **SID MATRIX FULLY LOADED!**")

        @client.on(events.NewMessage(pattern=r"\.magic", outgoing=True))
        async def sid_magic(event):
            text = "SID IS INCREDIBLE"
            for i in range(len(text)):
                await event.edit(f"🪄 `{text[:i+1]}`")
                await asyncio.sleep(0.2)
            await event.edit(f"✨ **{text}** ✨")

        @client.on(events.NewMessage(pattern=r"\.heart", outgoing=True))
        async def sid_heart(event):
            hearts = ["🤍", "🩷", "💖", "💗", "💓", "💞", "💕"]
            for h in hearts:
                await event.edit(f"Generating love... {h}")
                await asyncio.sleep(0.4)
            await event.edit(f"{hearts[-1]} **SID SENDS LOVE!** {hearts[-1]}")

        @client.on(events.NewMessage(pattern=r"\.matrix", outgoing=True))
        async def sid_matrix(event):
            for _ in range(5):
                bin_str = "".join([str(random.randint(0, 1)) for _ in range(30)])
                await event.edit(f"🟩 `{bin_str}`\n🟩 `{bin_str[::-1]}`\n🟩 `{bin_str}`")
                await asyncio.sleep(0.4)
            await event.edit(f"🟢 **MATRIX BYPASSED** 🟢")

        @client.on(events.NewMessage(pattern=r"\.explode", outgoing=True))
        async def sid_explode(event):
            anims = ["💣 `3...`", "💣 `2...`", "💣 `1...`", "💥 **BOOOOOOOOM** 💥"]
            for frame in anims:
                await event.edit(frame)
                await asyncio.sleep(1)

        @client.on(events.NewMessage(pattern=r"\.typing", outgoing=True))
        async def sid_typing(event):
            txt = event.raw_text.replace(".typing", "").strip()
            if not txt:
                return await event.edit("❌ Provide text.")
            current = ""
            for char in txt:
                current += char
                await event.edit(current + " |")
                await asyncio.sleep(0.1)
            await event.edit(current)

        # ── 2. ENGINE STATS & PING ──
        @client.on(events.NewMessage(pattern=r"\.sid$|\.alive$", outgoing=True))
        async def sid_alive(event):
            uptime = time.time() - U_STATE['start_time']
            h, r = divmod(int(uptime), 3600); m, s = divmod(r, 60)
            if gender == "BOY":
                txt = f"👑 **SID ENGINE IS DOMINATING** 👑\n━━━━━━━━━━━━━━━━━━━━\n» **Master:** `{preset_string}`\n» **Vibe:** `Aggressive & Unstoppable` 🔥\n» **Uptime:** `{h}h {m}m {s}s`"
            else:
                txt = f"🌸 **SID ENGINE IS THRIVING** 🌸\n━━━━━━━━━━━━━━━━━━━━\n» **Queen:** `{preset_string}`\n» **Vibe:** `Aesthetic & Flawless` ✨\n» **Uptime:** `{h}h {m}m {s}s`"
            await _safe_edit(event, txt)

        @client.on(events.NewMessage(pattern=r"\.ping", outgoing=True))
        async def sid_ping(event):
            start = time.time()
            await event.edit("⚡ `Pinging...`")
            ms = round((time.time() - start) * 1000, 2)
            if gender == "BOY":
                await event.edit(f"😈 **SID NETWORK SPEED**\n» `{ms} ms` - *Too fast for you.*")
            else:
                await event.edit(f"🎀 **SID NETWORK SPEED**\n» `{ms} ms` - *Lightning fast bestie!* ✨")

        # ── 3. RAID COMMANDS ──
        def register_raid(cmd, text_array):
            @client.on(events.NewMessage(pattern=rf"\.{cmd}"))
            async def start_raid(event):
                if not is_authorized(event):
                    return
                tgt = await get_target(event, event.raw_text.split(" ", 1)[1] if len(event.raw_text.split())>1 else "")
                if not tgt:
                    return await _safe_edit(event, "❌ Reply to a user.")
                if cmd not in U_STATE['active_raids']:
                    U_STATE['active_raids'][cmd] = set()
                U_STATE['active_raids'][cmd].add(tgt)
                await _safe_edit(event, f"🔥 **{cmd.upper()} RAID ON** → `{tgt}`")

            @client.on(events.NewMessage(pattern=rf"\.s{cmd}"))
            async def stop_raid(event):
                if not is_authorized(event):
                    return
                if cmd in U_STATE['active_raids']:
                    U_STATE['active_raids'][cmd].clear()
                await _safe_edit(event, f"🛑 **{cmd.upper()} RAID OFF**")

        register_raid("attack", ATTACK_LIST)
        register_raid("roast", ROAST_LIST)
        register_raid("diss", DISS_LIST)
        register_raid("war", WAR_LIST)
        register_raid("savage", SAVAGE_LIST)
        register_raid("rebel", DIPESH_MESSAGES)
        register_raid("sid", RAPIST_MESSAGES)       # renamed from akshu
        register_raid("homies", HOMIES_MESSAGES)

        @client.on(events.NewMessage())
        async def raid_trigger(event):
            if event.out:
                return
            sender = event.sender_id
            for cmd, targets in U_STATE['active_raids'].items():
                if sender in targets:
                    array_map = {
                        "attack": ATTACK_LIST,
                        "roast": ROAST_LIST,
                        "diss": DISS_LIST,
                        "war": WAR_LIST,
                        "savage": SAVAGE_LIST,
                        "rebel": DIPESH_MESSAGES,
                        "sid": RAPIST_MESSAGES,
                        "homies": HOMIES_MESSAGES
                    }
                    try:
                        await event.reply(random.choice(array_map[cmd]))
                    except FloodWaitError as e:
                        await asyncio.sleep(e.seconds)
                    except:
                        pass

        # ── 4. UTILITIES (Music, QR, TTS, Clone) ──
        @client.on(events.NewMessage(pattern=r"\.song", outgoing=True))
        async def sid_song(event):
            song_name = event.raw_text.replace(".song", "").strip()
            if not song_name:
                return await _safe_edit(event, "❌ Provide a song name")
            await _safe_edit(event, f"🎵 Downloading: `{song_name}`...")
            file_base = f"sid_song_{event.id}"
            opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{file_base}.%(ext)s',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
                'quiet': True,
                'default_search': 'ytsearch1'
            }
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.extract_info(song_name, download=True)
                    if os.path.exists(f"{file_base}.mp3"):
                        await client.send_file(event.chat_id, f"{file_base}.mp3", reply_to=event.reply_to_msg_id)
                        os.remove(f"{file_base}.mp3")
                        try:
                            await event.delete()
                        except:
                            pass
                    else:
                        await _safe_edit(event, "❌ Failed.")
            except Exception as e:
                await _safe_edit(event, f"❌ Error: {e}")

        @client.on(events.NewMessage(pattern=r"\.qr", outgoing=True))
        async def sid_qr(event):
            txt = event.raw_text.replace(".qr", "").strip()
            if not txt:
                return await _safe_edit(event, "❌ Provide text.")
            await _safe_edit(event, "⚡ Generating QR...")
            f = f"qr_{event.id}.png"
            qrcode.make(txt).save(f)
            await client.send_file(event.chat_id, f, caption="🔳 QR Code")
            os.remove(f)
            await event.delete()

        @client.on(events.NewMessage(pattern=r"\.tts", outgoing=True))
        async def sid_tts(event):
            txt = event.raw_text.replace(".tts", "").strip()
            if not txt:
                return await _safe_edit(event, "❌ Provide text.")
            await _safe_edit(event, "🗣️ Generating TTS...")
            f = f"tts_{event.id}.mp3"
            gTTS(text=txt, lang="hi").save(f)
            await client.send_file(event.chat_id, f, voice_note=True)
            os.remove(f)
            await event.delete()

        @client.on(events.NewMessage(pattern=r"\.copy", outgoing=True))
        async def sid_copy(event):
            tgt = await get_target(event, event.raw_text.replace(".copy", "").strip())
            if not tgt:
                return await _safe_edit(event, "❌ Provide target.")
            await _safe_edit(event, "🔄 Cloning Profile...")
            try:
                target_ent = await client.get_entity(tgt)
                me = await client.get_me()
                if not U_STATE['original_profile']:
                    U_STATE['original_profile']['first'] = me.first_name or ""
                    U_STATE['original_profile']['last'] = me.last_name or ""
                await client(UpdateProfileRequest(first_name=target_ent.first_name or "",
                                                  last_name=target_ent.last_name or ""))
                ph = await client.download_profile_photo(target_ent)
                if ph:
                    my_ph = await client.get_profile_photos('me')
                    if my_ph:
                        await client(DeletePhotosRequest(id=[p for p in my_ph]))
                    await client(UploadProfilePhotoRequest(file=await client.upload_file(ph)))
                    os.remove(ph)
                await _safe_edit(event, f"🎭 Identity theft successful. Now acting as {target_ent.first_name}")
            except Exception as e:
                await _safe_edit(event, f"❌ Error: {e}")

        @client.on(events.NewMessage(pattern=r"\.back", outgoing=True))
        async def sid_back(event):
            if not U_STATE['original_profile']:
                return await _safe_edit(event, "❌ No backup found.")
            await _safe_edit(event, "🔄 Reverting...")
            try:
                await client(UpdateProfileRequest(first_name=U_STATE['original_profile']['first'],
                                                  last_name=U_STATE['original_profile']['last']))
                await _safe_edit(event, "✅ Original Profile Restored!")
            except Exception as e:
                await _safe_edit(event, f"❌ Error: {e}")

        # ── 5. ADMIN, MUTE & PROTECT ──
        @client.on(events.NewMessage(pattern=r"\.mute"))
        async def sid_mute(event):
            if not is_authorized(event):
                return
            tgt = await get_target(event, event.raw_text.replace(".mute", "").strip())
            if tgt:
                U_STATE['muted'][tgt] = event.chat_id
                await _safe_edit(event, "🤫 Muted in this chat.")

        @client.on(events.NewMessage(pattern=r"\.unmute"))
        async def sid_unmute(event):
            if not is_authorized(event):
                return
            tgt = await get_target(event, event.raw_text.replace(".unmute", "").strip())
            if tgt in U_STATE['muted']:
                del U_STATE['muted'][tgt]
                await _safe_edit(event, "🔊 Unmuted.")

        @client.on(events.NewMessage())
        async def enforce_mute(event):
            if event.sender_id in U_STATE['muted'] and event.chat_id == U_STATE['muted'][event.sender_id]:
                try:
                    await event.delete()
                except:
                    pass

        @client.on(events.NewMessage(pattern=r"\.safe"))
        async def sid_safe(event):
            if not is_authorized(event):
                return
            tgt = await get_target(event, event.raw_text.replace(".safe", "").strip())
            if tgt:
                if event.chat_id not in U_STATE['safe']:
                    U_STATE['safe'][event.chat_id] = set()
                U_STATE['safe'][event.chat_id].add(tgt)
                await _safe_edit(event, "🛡 User is safe from deletion.")

        @client.on(events.NewMessage(pattern=r"\.unsafe"))
        async def sid_unsafe(event):
            if not is_authorized(event):
                return
            tgt = await get_target(event, event.raw_text.replace(".unsafe", "").strip())
            if tgt and event.chat_id in U_STATE['safe'] and tgt in U_STATE['safe'][event.chat_id]:
                U_STATE['safe'][event.chat_id].discard(tgt)
                await _safe_edit(event, "⚠️ User is unsafe.")

        @client.on(events.NewMessage(pattern=r"\.purge"))
        async def sid_purge(event):
            if not is_authorized(event):
                return
            if event.is_reply:
                msgs = [m.id async for m in client.iter_messages(event.chat_id, min_id=event.reply_to_msg_id - 1)]
                if msgs:
                    for i in range(0, len(msgs), 100):
                        await client.delete_messages(event.chat_id, msgs[i:i+100])
                    x = await client.send_message(event.chat_id, f"🗑️ Purged {len(msgs)-1} messages.")
                    await asyncio.sleep(2)
                    await x.delete()

        # ── 6. MENU ──
        @client.on(events.NewMessage(pattern=r"\.sid_menu|\.menu"))
        async def sid_menu(event):
            if not is_authorized(event):
                return
            MENU = f"""
            ===================================
                     {gender} SID MASTER MENU 👑
            ===================================
            🔥 **RAID COMMANDS**
            • `.attack` / `.sattack` (Stop)
            • `.roast` / `.sroast`
            • `.rebel` / `.srebel`
            • `.sid` / `.ssid`          ← renamed from .akshu
            • `.homies` / `.shomies`

            ✨ **ANIMATIONS & EFFECTS**
            • `.hack` (Terminal Hack)
            • `.load` (Progress Bar)
            • `.magic` (Text Reveal)
            • `.heart` (Love Burst)
            • `.matrix` (Binary Code)
            • `.explode` (Bomb Effect)
            • `.typing [text]`

            🛠 **UTILITIES**
            • `.song [name]` (YT Download)
            • `.qr [text]` (Generate QR)
            • `.tts [text]` (Voice note)
            • `.copy [reply]` / `.back` (Clone)
            • `.ping` / `.alive` / `.sid`

            🛑 **ADMIN / CONTROL**
            • `.mute` / `.unmute`
            • `.safe` / `.unsafe`
            • `.purge` (Reply to start)

            ===================================
            Powered by SID Core v6.0
            ==================================="""
            await _safe_edit(event, MENU)

        await client.run_until_disconnected()

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(operational_lifecycle())
    except Exception as e:
        logger.error(f"Context dropped: {e}")
        if chat_id:
            bot.send_message(chat_id, f"❌ Userbot crashed: {e}")
    finally:
        active_runtimes.pop(user_id, None)

# ──────────────────────────────────────────────────────────────────────────────
# SYSTEM METRICS & SHUTDOWN
# ──────────────────────────────────────────────────────────────────────────────
@bot.callback_query_handler(func=lambda call: call.data == "telemetry")
def display_telemetry(call):
    txt = f"📊 **SID TELEMETRY DATA**\n━━━━━━━━━━━━━━━━━━━━\n🟢 **Active Containers:** `{len(active_runtimes)}`\n🧠 **Host RAM Usage:** `{psutil.virtual_memory().percent}%`\n⚙️ **Host CPU Load:** `{psutil.cpu_percent}%`\n\n» *Architecture fully dynamic & scaled.*"
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "terminate")
def terminate_worker(call):
    user_id = call.from_user.id
    if user_id in active_runtimes:
        active_runtimes[user_id]['loop'].create_task(active_runtimes[user_id]['client'].disconnect())
        bot.answer_callback_query(call.id, "🛑 SID Container Terminated Successfully.", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❌ No active runtimes detected.", show_alert=True)

# ════════════════════════════════════════════════════════════════════════════════
# ─── ADDITIONS FOR OWNER, SUDO, BLOCK, ETC. ───
# ════════════════════════════════════════════════════════════════════════════════

OWNER_ID = 123456789  # ← REPLACE WITH YOUR OWNER TELEGRAM ID
SUPPORT_USERNAME = "@YourSupport"  # ← REPLACE
MAX_ACCOUNTS_PER_USER = 3
MAX_USERBOTS = 50
START_TIME = time.time()

def is_owner(user_id):
    return user_id == OWNER_ID

def is_premium(user_id):
    return is_owner(user_id) or db_is_sudo(user_id)

def db_is_sudo(user_id):
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('SELECT 1 FROM sudo_users WHERE user_id = ?', (user_id,))
        res = c.fetchone() is not None
        conn.close()
        return res

def get_accounts(user_id):
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('SELECT session_key, gender, system_preset, api_id, api_hash FROM hosted_sessions WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        conn.close()
    if row:
        return [{
            'slot': 0,
            'session_key': row[0],
            'gender': row[1],
            'system_preset': row[2],
            'api_id': row[3],
            'api_hash': row[4],
            'hosted': True,
            'hosted_at': int(time.time()),
        }]
    return []

def get_account(user_id, slot):
    accounts = get_accounts(user_id)
    if slot < len(accounts):
        return accounts[slot]
    return None

def remove_account(user_id, slot):
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM hosted_sessions WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

def get_all_users():
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('SELECT user_id FROM hosted_sessions')
        rows = c.fetchall()
        conn.close()
    return [str(r[0]) for r in rows]

def hosted_count():
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM hosted_sessions')
        cnt = c.fetchone()[0]
        conn.close()
    return cnt

def user_count():
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('SELECT COUNT(DISTINCT user_id) FROM hosted_sessions')
        cnt = c.fetchone()[0]
        conn.close()
    return cnt

def block_user(user_id):
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO blocked_users (user_id) VALUES (?)', (user_id,))
        conn.commit()
        conn.close()

def unblock_user(user_id):
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM blocked_users WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

def is_blocked(user_id):
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('SELECT 1 FROM blocked_users WHERE user_id = ?', (user_id,))
        res = c.fetchone() is not None
        conn.close()
        return res

def get_blocked():
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('SELECT user_id FROM blocked_users')
        rows = [r[0] for r in c.fetchall()]
        conn.close()
        return rows

def add_sudo(user_id):
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO sudo_users (user_id) VALUES (?)', (user_id,))
        conn.commit()
        conn.close()

def remove_sudo(user_id):
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM sudo_users WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

def get_sudo_users():
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('SELECT user_id FROM sudo_users')
        rows = [r[0] for r in c.fetchall()]
        conn.close()
        return rows

def get_welcome_video():
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('SELECT file_id, is_video_note FROM welcome_video LIMIT 1')
        row = c.fetchone()
        conn.close()
    if row:
        return {'file_id': row[0], 'is_video_note': bool(row[1])}
    return None

def set_welcome_video(data):
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM welcome_video')
        c.execute('INSERT INTO welcome_video (id, file_id, is_video_note) VALUES (1, ?, ?)',
                  (data['file_id'], 1 if data['is_video_note'] else 0))
        conn.commit()
        conn.close()

def remove_welcome_video():
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM welcome_video')
        conn.commit()
        conn.close()

def get_api_profile():
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('SELECT api_id, api_hash FROM api_config LIMIT 1')
        row = c.fetchone()
        conn.close()
    if row:
        return {'api_id': row[0], 'api_hash': row[1]}
    return None

def save_api_profile(api_id, api_hash):
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM api_config')
        c.execute('INSERT INTO api_config (id, api_id, api_hash) VALUES (1, ?, ?)', (api_id, api_hash))
        conn.commit()
        conn.close()

def _get_api_id_hash():
    prof = get_api_profile()
    if prof:
        return prof['api_id'], prof['api_hash']
    return DEFAULT_API_ID, DEFAULT_API_HASH

def _masked_api_hash():
    prof = get_api_profile()
    if prof:
        h = prof['api_hash']
        return h[:4] + '****' + h[-4:] if len(h) >= 8 else '****'
    return 'Not set'

def _api_ready():
    return get_api_profile() is not None

# ─── RUNNER WRAPPER ───
class RunnerWrapper:
    @staticmethod
    def is_running(user_id, slot):
        return user_id in active_runtimes

    @staticmethod
    def get_uptime(user_id, slot):
        if user_id in active_runtimes:
            return "N/A"
        return None

    @staticmethod
    def running_count():
        return len(active_runtimes)

    @staticmethod
    def start_userbot(uid, slot, api_id, api_hash, session_string, uid_str):
        with GLOBAL_DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH)
            c = conn.cursor()
            c.execute('SELECT gender, system_preset FROM hosted_sessions WHERE user_id = ?', (uid,))
            row = c.fetchone()
            conn.close()
        if row:
            gender, preset = row
            threading.Thread(target=deploy_live_userbot_runtime, args=(None, uid, gender, preset), daemon=True).start()
            return True
        return False

    @staticmethod
    def restart_userbot(uid, slot, api_id, api_hash, session_string, uid_str):
        if uid in active_runtimes:
            try:
                loop = active_runtimes[uid]['loop']
                loop.create_task(active_runtimes[uid]['client'].disconnect())
            except:
                pass
            active_runtimes.pop(uid, None)
        return RunnerWrapper.start_userbot(uid, slot, api_id, api_hash, session_string, uid_str)

    @staticmethod
    def stop_userbot(uid, slot):
        if uid in active_runtimes:
            try:
                loop = active_runtimes[uid]['loop']
                loop.create_task(active_runtimes[uid]['client'].disconnect())
            except:
                pass
            active_runtimes.pop(uid, None)
        return True

    @staticmethod
    def stop_all_for_user(uid):
        RunnerWrapper.stop_userbot(uid, 0)

runner = RunnerWrapper()

def uptime_str():
    e = int(time.time() - START_TIME)
    h, r = divmod(e, 3600); m, s = divmod(r, 60)
    return f"{h}h {m}m {s}s"

def _phone_label(acct):
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('SELECT phone FROM user_metadata WHERE user_id = ?', (acct.get('user_id'),))
        row = c.fetchone()
        conn.close()
    return row[0] if row else "Unknown"

# ─── BOT COMMANDS (owner, user, etc.) ───
@bot.message_handler(commands=['myaccounts'])
def cmd_myaccounts(message):
    uid = message.from_user.id
    if is_blocked(uid):
        bot.reply_to(message, "🚫 You are blocked.")
        return
    accounts = get_accounts(uid)
    if not accounts:
        bot.reply_to(message, "📱 No accounts hosted. Use /host to deploy.")
        return
    for acct in accounts:
        slot = acct['slot']
        alive = runner.is_running(uid, slot)
        phone = _phone_label(acct)
        status = "🟢 Running" if alive else "🔴 Stopped"
        bot.reply_to(message, f"📱 Account #{slot+1}\nPhone: {phone}\nStatus: {status}")

@bot.message_handler(commands=['status'])
def cmd_status(message):
    uid = message.from_user.id
    if is_blocked(uid):
        return
    accounts = get_accounts(uid)
    if not accounts:
        bot.reply_to(message, "❌ No userbot found.")
        return
    lines = []
    for acct in accounts:
        slot = acct['slot']
        alive = runner.is_running(uid, slot)
        uptime = runner.get_uptime(uid, slot) if alive else "—"
        phone = _phone_label(acct)
        icon = "🟢" if alive else "🔴"
        lines.append(f"{icon} Account #{slot+1} — {phone}\n   Uptime: {uptime}")
    bot.reply_to(message, "📊 Userbot Status\n\n" + "\n\n".join(lines))

@bot.message_handler(commands=['restart'])
def cmd_restart(message):
    uid = message.from_user.id
    if is_blocked(uid):
        return
    accounts = get_accounts(uid)
    if not accounts:
        bot.reply_to(message, "❌ No userbot to restart.")
        return
    acct = accounts[0]
    slot = acct['slot']
    msg = bot.reply_to(message, "🔄 Restarting...")
    ok = runner.restart_userbot(uid, slot, "", "", "", str(uid))
    if ok:
        bot.edit_message_text("✅ Account restarted successfully!", msg.chat.id, msg.message_id)
    else:
        bot.edit_message_text("❌ Restart failed.", msg.chat.id, msg.message_id)

@bot.message_handler(commands=['logout'])
def cmd_logout(message):
    uid = message.from_user.id
    if is_blocked(uid):
        return
    accounts = get_accounts(uid)
    if not accounts:
        bot.reply_to(message, "❌ No account to logout.")
        return
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Yes, Logout", callback_data="confirm_logout"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_logout")
    )
    bot.reply_to(message, "⚠️ Are you sure you want to logout and delete session?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "confirm_logout")
def confirm_logout(call):
    uid = call.from_user.id
    runner.stop_userbot(uid, 0)
    remove_account(uid, 0)
    session_path = os.path.join(RUNTIMES_DIR, f"active_{uid}.session")
    if os.path.exists(session_path):
        os.remove(session_path)
    bot.answer_callback_query(call.id, "Logged out successfully.")
    bot.edit_message_text("👋 Account logged out. Use /host to deploy again.", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_logout")
def cancel_logout(call):
    bot.answer_callback_query(call.id, "Logout cancelled.")
    bot.edit_message_text("Logout cancelled.", call.message.chat.id, call.message.message_id)

@bot.message_handler(commands=['support'])
def cmd_support(message):
    bot.reply_to(message, f"📞 Support: {SUPPORT_USERNAME}\nFor help, use /help or contact admin.")

@bot.message_handler(commands=['help'])
def cmd_help(message):
    text = """
❓ Help & Commands
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔹 /start       - Welcome screen
🔹 /host        - Deploy userbot
🔹 /myaccounts  - View accounts
🔹 /status      - Check status
🔹 /restart     - Restart userbot
🔹 /logout      - Logout account
🔹 /support     - Contact support
🔹 /help        - This menu
    """
    bot.reply_to(message, text)

@bot.message_handler(commands=['stats'])
def cmd_stats(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "🔒 Owner only.")
        return
    total = user_count()
    hosted = hosted_count()
    running = runner.running_count()
    blocked = len(get_blocked())
    sudos = len(get_sudo_users())
    bot.reply_to(message, f"""
📊 Bot Statistics
━━━━━━━━━━━━━━━━━━━━
👥 Total Users: {total}
🚀 Hosted: {hosted}
🟢 Running: {running}
🔴 Stopped: {hosted - running}
🚫 Blocked: {blocked}
👑 Sudo: {sudos}
🕒 Uptime: {uptime_str()}
    """)

@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(message):
    if not is_owner(message.from_user.id):
        return
    if not message.reply_to_message and not message.text.replace('/broadcast','').strip():
        bot.reply_to(message, "Reply to a message or provide text: /broadcast Hello")
        return
    users = get_all_users()
    if not users:
        bot.reply_to(message, "No users to broadcast.")
        return
    sent = 0
    failed = 0
    for uid_str in users:
        try:
            uid = int(uid_str)
            if is_blocked(uid):
                continue
            if message.reply_to_message:
                bot.copy_message(uid, message.chat.id, message.reply_to_message.message_id)
            else:
                bot.send_message(uid, message.text.replace('/broadcast','').strip())
            sent += 1
        except Exception as e:
            failed += 1
    bot.reply_to(message, f"✅ Broadcast sent to {sent} users. Failed: {failed}")

@bot.message_handler(commands=['sudolist'])
def cmd_sudolist(message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split()
    if len(args) >= 3 and args[1] == 'add':
        try:
            uid = int(args[2])
            add_sudo(uid)
            bot.reply_to(message, f"✅ Added {uid} to sudo.")
        except:
            bot.reply_to(message, "❌ Invalid ID.")
        return
    if len(args) >= 3 and args[1] == 'del':
        try:
            uid = int(args[2])
            remove_sudo(uid)
            bot.reply_to(message, f"✅ Removed {uid} from sudo.")
        except:
            bot.reply_to(message, "❌ Invalid ID.")
        return
    sudos = get_sudo_users()
    if not sudos:
        bot.reply_to(message, "No sudo users.")
    else:
        bot.reply_to(message, "👑 Sudo Users:\n" + "\n".join(str(u) for u in sudos))

@bot.message_handler(commands=['block'])
def cmd_block(message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /block <user_id>")
        return
    try:
        uid = int(args[1])
        if uid == OWNER_ID:
            bot.reply_to(message, "Cannot block owner.")
            return
        block_user(uid)
        runner.stop_all_for_user(uid)
        bot.reply_to(message, f"🚫 User {uid} blocked.")
    except:
        bot.reply_to(message, "Invalid ID.")

@bot.message_handler(commands=['unblock'])
def cmd_unblock(message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /unblock <user_id>")
        return
    try:
        uid = int(args[1])
        unblock_user(uid)
        bot.reply_to(message, f"✅ User {uid} unblocked.")
    except:
        bot.reply_to(message, "Invalid ID.")

@bot.message_handler(commands=['blockeduser'])
def cmd_blockeduser(message):
    if not is_owner(message.from_user.id):
        return
    blocked = get_blocked()
    if not blocked:
        bot.reply_to(message, "No blocked users.")
    else:
        bot.reply_to(message, "🚫 Blocked users:\n" + "\n".join(str(u) for u in blocked))

@bot.message_handler(commands=['secretfunction'])
def cmd_secretfunction(message):
    if not is_owner(message.from_user.id):
        return
    bot.reply_to(message, """
🔐 Secret Commands
━━━━━━━━━━━━━━━━━━━━
🔹 /sudolist add <uid>
🔹 /sudolist del <uid>
🔹 /block <uid>
🔹 /unblock <uid>
🔹 /blockeduser
🔹 /stats
🔹 /broadcast
🔹 /restartall
🔹 /setdp
🔹 /setwelcomevideo
🔹 /removewelcomevideo
    """)

@bot.message_handler(commands=['setdp'])
def cmd_setdp(message):
    if not is_owner(message.from_user.id):
        return
    if not message.reply_to_message or not message.reply_to_message.photo:
        bot.reply_to(message, "Reply to a photo with /setdp")
        return
    photo = message.reply_to_message.photo[-1]
    file_id = photo.file_id
    try:
        bot.set_chat_photo(photo=file_id)
        bot.reply_to(message, "✅ Display photo updated.")
    except Exception as e:
        bot.reply_to(message, f"❌ Failed: {e}")

@bot.message_handler(commands=['setwelcomevideo'])
def cmd_setwelcomevideo(message):
    if not is_owner(message.from_user.id):
        return
    if not message.reply_to_message:
        bot.reply_to(message, "Reply to a video or video note.")
        return
    vid = message.reply_to_message.video
    vnote = message.reply_to_message.video_note
    if vid:
        set_welcome_video({'file_id': vid.file_id, 'is_video_note': False})
        bot.reply_to(message, "✅ Welcome video set.")
    elif vnote:
        set_welcome_video({'file_id': vnote.file_id, 'is_video_note': True})
        bot.reply_to(message, "✅ Welcome video note set.")
    else:
        bot.reply_to(message, "Reply must be video or video note.")

@bot.message_handler(commands=['removewelcomevideo'])
def cmd_removewelcomevideo(message):
    if not is_owner(message.from_user.id):
        return
    remove_welcome_video()
    bot.reply_to(message, "🗑️ Welcome video removed.")

@bot.message_handler(commands=['setapi'])
def cmd_setapi(message):
    if not is_owner(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "Usage: /setapi <api_id> <api_hash>")
        return
    try:
        api_id = int(args[1])
        api_hash = args[2]
        save_api_profile(api_id, api_hash)
        bot.reply_to(message, f"✅ API profile saved.\nID: {api_id}\nHash: {api_hash[:4]}****")
    except:
        bot.reply_to(message, "❌ Invalid input.")

@bot.message_handler(commands=['apistatus'])
def cmd_apistatus(message):
    if not is_owner(message.from_user.id):
        return
    prof = get_api_profile()
    if prof:
        bot.reply_to(message, f"📡 API Status\nID: {prof['api_id']}\nHash: {_masked_api_hash()}")
    else:
        bot.reply_to(message, "⚠️ No API profile set. Use /setapi")

@bot.message_handler(commands=['restartall'])
def cmd_restartall(message):
    if not is_owner(message.from_user.id):
        return
    count = 0
    for uid_str in get_all_users():
        uid = int(uid_str)
        if is_blocked(uid):
            continue
        accounts = get_accounts(uid)
        for acct in accounts:
            if runner.restart_userbot(uid, acct['slot'], "", "", "", uid_str):
                count += 1
    bot.reply_to(message, f"✅ Restarted {count} userbots.")

@bot.message_handler(commands=['refresh'])
def cmd_refresh(message):
    if not is_owner(message.from_user.id):
        return
    bot.reply_to(message, f"🔄 Bot state refreshed.\nRunning: {runner.running_count()}\nHosted: {hosted_count()}")

# ─── EXTRA CALLBACKS ───
@bot.callback_query_handler(func=lambda call: call.data == "my_account")
def callback_my_account(call):
    uid = call.from_user.id
    accounts = get_accounts(uid)
    if not accounts:
        bot.answer_callback_query(call.id, "No accounts hosted.")
        bot.edit_message_text("No accounts hosted. Use /host to deploy.", call.message.chat.id, call.message.message_id)
        return
    acct = accounts[0]
    phone = _phone_label(acct)
    alive = runner.is_running(uid, 0)
    status = "🟢 Running" if alive else "🔴 Stopped"
    bot.edit_message_text(f"📱 Your Account\nPhone: {phone}\nStatus: {status}", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "cmd_list")
def callback_cmd_list(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text("""
⚡ SID Advance V6 Commands
━━━━━━━━━━━━━━━━━━━━
⚔️ Raid: .attack .roast .diss .war .savage .rebel .sid .homies
✨ Animations: .hack .load .magic .heart .matrix .explode .typing
🛠 Utilities: .song .qr .tts .copy .back .ping .alive .sid
🛑 Admin: .mute .unmute .safe .unsafe .purge
""", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "support")
def callback_support(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text(f"📞 Support: {SUPPORT_USERNAME}", call.message.chat.id, call.message.message_id)

# ─── HEALTH CHECK ───
def health_check_loop():
    while True:
        time.sleep(300)
        try:
            for uid_str in get_all_users():
                uid = int(uid_str)
                if is_blocked(uid):
                    continue
                if uid not in active_runtimes:
                    accounts = get_accounts(uid)
                    for acct in accounts:
                        if acct.get('hosted'):
                            runner.start_userbot(uid, acct['slot'], "", "", "", uid_str)
        except Exception as e:
            logger.error(f"Health check error: {e}")

# ─── WEB API ───
def start_web_api():
    web_loop = asyncio.new_event_loop()
    def run_web_loop():
        asyncio.set_event_loop(web_loop)
        web_loop.run_forever()
    Thread(target=run_web_loop, daemon=True).start()

    web_pending = {}
    web_app = Flask('SidWebAPI')

    def _run_async(coro, timeout=30):
        future = asyncio.run_coroutine_threadsafe(coro, web_loop)
        return future.result(timeout=timeout)

    @web_app.route('/api/health')
    def health():
        return jsonify({"status": "ok"})

    @web_app.route('/api/accounts')
    def list_accounts():
        out = []
        for uid_str in get_all_users():
            uid = int(uid_str)
            for acct in get_accounts(uid):
                slot = acct.get('slot', 0)
                out.append({
                    'uid': uid,
                    'slot': slot,
                    'phone': _phone_label(acct),
                    'status': 'running' if runner.is_running(uid, slot) else 'stopped',
                    'uptime': runner.get_uptime(uid, slot) or '0s'
                })
        return jsonify({"accounts": out})

    @web_app.route('/api/login/send_code', methods=['POST'])
    def login_send_code():
        data = request.get_json() or {}
        phone = data.get('phone', '').strip()
        if not phone:
            return jsonify({"status": "error", "message": "Phone required"}), 400
        try:
            api_id, api_hash = _get_api_id_hash()
            async def _send():
                client = TelegramClient(StringSession(), api_id, api_hash)
                await client.connect()
                result = await client.send_code_request(phone)
                return client, result.phone_code_hash
            client, phone_code_hash = _run_async(_send())
            pending_id = secrets.token_urlsafe(16)
            web_pending[pending_id] = {
                'client': client,
                'phone': phone,
                'phone_code_hash': phone_code_hash,
                'owner_id': data.get('owner_id', OWNER_ID)
            }
            return jsonify({"status": "ok", "pending_id": pending_id})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    @web_app.route('/api/login/verify_code', methods=['POST'])
    def login_verify_code():
        data = request.get_json() or {}
        pending_id = data.get('pending_id')
        code = data.get('code', '').strip()
        pending = web_pending.get(pending_id)
        if not pending:
            return jsonify({"status": "error", "message": "Session expired"}), 400
        try:
            async def _verify():
                await pending['client'].sign_in(pending['phone'], code, phone_code_hash=pending['phone_code_hash'])
                return pending['client'].session.save()
            session_string = _run_async(_verify())
            web_pending.pop(pending_id, None)
            uid = pending['owner_id']
            ok = runner.start_userbot(uid, 0, "", "", session_string, str(uid))
            if ok:
                with GLOBAL_DB_LOCK:
                    conn = sqlite3.connect(DATABASE_PATH)
                    c = conn.cursor()
                    c.execute('INSERT OR REPLACE INTO hosted_sessions (user_id, session_key, gender, system_preset, api_id, api_hash) VALUES (?, ?, ?, ?, ?, ?)',
                              (uid, session_string, 'BOY', 'SID BOT', _get_api_id_hash()[0], _get_api_id_hash()[1]))
                    conn.commit()
                    conn.close()
                return jsonify({"status": "ok", "account": {"uid": uid, "phone": pending['phone']}})
            else:
                return jsonify({"status": "error", "message": "Deploy failed"}), 400
        except SessionPasswordNeededError:
            return jsonify({"status": "needs_2fa"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    @web_app.route('/api/login/verify_password', methods=['POST'])
    def login_verify_password():
        data = request.get_json() or {}
        pending_id = data.get('pending_id')
        password = data.get('password', '')
        pending = web_pending.get(pending_id)
        if not pending:
            return jsonify({"status": "error", "message": "Session expired"}), 400
        try:
            async def _verify():
                await pending['client'].sign_in(password=password)
                return pending['client'].session.save()
            session_string = _run_async(_verify())
            web_pending.pop(pending_id, None)
            uid = pending['owner_id']
            ok = runner.start_userbot(uid, 0, "", "", session_string, str(uid))
            if ok:
                with GLOBAL_DB_LOCK:
                    conn = sqlite3.connect(DATABASE_PATH)
                    c = conn.cursor()
                    c.execute('INSERT OR REPLACE INTO hosted_sessions (user_id, session_key, gender, system_preset, api_id, api_hash) VALUES (?, ?, ?, ?, ?, ?)',
                              (uid, session_string, 'BOY', 'SID BOT', _get_api_id_hash()[0], _get_api_id_hash()[1]))
                    conn.commit()
                    conn.close()
                return jsonify({"status": "ok", "account": {"uid": uid, "phone": pending['phone']}})
            else:
                return jsonify({"status": "error", "message": "Deploy failed"}), 400
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    @web_app.route('/api/accounts/<int:uid>/<int:slot>/start', methods=['POST'])
    def start_account(uid, slot):
        acct = get_account(uid, slot)
        if not acct:
            return jsonify({"error": "not found"}), 404
        ok = runner.start_userbot(uid, slot, "", "", acct.get('session_key', ''), str(uid))
        return jsonify({"ok": ok})

    @web_app.route('/api/accounts/<int:uid>/<int:slot>/stop', methods=['POST'])
    def stop_account(uid, slot):
        runner.stop_userbot(uid, slot)
        return jsonify({"ok": True})

    @web_app.route('/api/accounts/<int:uid>/<int:slot>/restart', methods=['POST'])
    def restart_account(uid, slot):
        acct = get_account(uid, slot)
        if not acct:
            return jsonify({"error": "not found"}), 404
        ok = runner.restart_userbot(uid, slot, "", "", acct.get('session_key', ''), str(uid))
        return jsonify({"ok": ok})

    port = int(os.environ.get("WEB_PORT", 8081))
    Thread(target=lambda: web_app.run(host="0.0.0.0", port=port, debug=False), daemon=True).start()
    logger.info(f"🌐 Web dashboard API running on port {port}")

# ─── SAFE SHUTDOWN ───
def safe_shutdown():
    logger.info("Initiating safe shutdown...")
    for uid, e in list(active_runtimes.items()):
        try:
            e['loop'].run_until_complete(e['client'].disconnect())
        except:
            pass

atexit.register(safe_shutdown)

# ─── MAIN ───
if __name__ == '__main__':
    logger.info("Initializing SID Master Thread Pools...")
    Thread(target=initialize_keepalive_server, daemon=True).start()
    Thread(target=start_web_api, daemon=True).start()
    Thread(target=health_check_loop, daemon=True).start()
    logger.info("SID Host Master Online. Entering infinite polling...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            logger.critical(f"Loop Collapsed: {e}. Retrying...")
            time.sleep(5)
