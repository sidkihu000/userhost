# -*- coding: utf-8 -*-
"""
================================━━━━━━━━================================
                 ✨ SID TELEGRAM USERBOT MASTER ENGINE ✨
================================━━━━━━━━================================
Core Architecture: pyTelegramBotAPI (Master Controller) + Telethon (Dynamic Runtimes)
Features: OTP/2FA, Gender-Segmented Profiles, Full Raid/Utility Commands Integrated
"""

import os
import sys
import time
import json
import uuid
import shutil
import logging
import sqlite3
import asyncio
import atexit
import psutil
import threading
from datetime import datetime

import telebot
from telebot import types
from flask import Flask
from threading import Thread

# Userbot Dependencies
import yt_dlp
import telethon
from telethon import TelegramClient, events
from telethon.errors import (
    SessionPasswordNeededError, 
    PhoneCodeInvalidError, 
    PasswordHashInvalidError,
    PhoneCodeExpiredError
)
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.types import ChatAdminRights

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 1: SYSTEM LOGGING & ENVIRONMENT
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [SID-ENGINE] - [%(levelname)s] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SidHostMaster")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
RUNTIMES_DIR = os.path.join(BASE_DIR, 'sid_runtimes')
DATA_STORAGE_DIR = os.path.join(BASE_DIR, 'sid_metadata')
DATABASE_PATH = os.path.join(DATA_STORAGE_DIR, 'sid_hosting.db')

os.makedirs(RUNTIMES_DIR, exist_ok=True)
os.makedirs(DATA_STORAGE_DIR, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 2: WEB RECOVERY LAYER (FLASK KEEPALIVE)
# ──────────────────────────────────────────────────────────────────────────────
web_app = Flask('SidHostServer')

@web_app.route('/')
def health_check():
    return "<h3>Sid Engine Core Status: ONLINE 🟢</h3>", 200

def initialize_keepalive_server():
    server_port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=server_port)

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 3: CONSTANTS, PRESETS & RESOURCE PAYLOADS
# ──────────────────────────────────────────────────────────────────────────────
BOT_TOKEN = '6248614957:AAGII_pN7RJiz6xxuTV-4zf9KGt2_s6ncYU'
PRIMARY_OWNER_ID = 2119464081

DEFAULT_API_ID = 32082988
DEFAULT_API_HASH = "a81844a473550947cfff864a8c7489cd"

# Aesthetics
BOY_PRESETS = ["SID KENG 👑", "DEADLY SID 💀", "REBEL SID 🔥", "SID RULE SERVER 😎"]
GIRL_PRESETS = ["SID BADDIE 🎀", "ANGEL SID ✨", "ROSE SID 🌸", "CUTE SID 💅🏻"]

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
            "🟢 `[▱▱▱▱▱▱▱▱▱▱] 0% - Booting Sid Kernel...`",
            "🟡 `[▰▰▰▱▱▱▱▱▱▱] 30% - Injecting Subroutines...`",
            "🟠 `[▰▰▰▰▰▰▱▱▱▱] 60% - Allocating Secure Memory...`",
            "🔴 `[▰▰▰▰▰▰▰▰▰▱] 90% - Establishing Telegram Uplink...`",
            "✅ `[▰▰▰▰▰▰▰▰▰▰] 100% - Link Established!`"
        ]
        def pipeline():
            try:
                for frame in frames:
                    bot.edit_message_text(frame, chat_id, target_msg_id, parse_mode='Markdown')
                    time.sleep(0.6)
                bot.edit_message_text(final_message_text, chat_id, target_msg_id, reply_markup=markup, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"UI Terminal rendering error: {e}")
        Thread(target=pipeline, daemon=True).start()

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 6: PRIMARY DASHBOARD & MENU DISPATCHER
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
    
    welcome_text = (
        f"👑 **SID PREMIUM USERBOT ARCHITECTURE** 👑\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ Welcome, {message.from_user.first_name}.\n\n"
        f"» **Engine Version:** `v5.0-SID-STABLE`\n"
        f"» **Host Status:** `ONLINE & SECURE`\n\n"
        f"Select your deployment module below to establish your runtime:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 7: MULTI-STEP VERIFICATION & REGISTRATION FLOW (OTP & 2FA)
# ──────────────────────────────────────────────────────────────────────────────
@bot.callback_query_handler(func=lambda call: call.data in ["deploy_boy", "deploy_girl"])
def trigger_deployment(call):
    bot.answer_callback_query(call.id)
    gender_choice = "BOY" if "boy" in call.data else "GIRL"
    start_onboarding_sequence(call.message.chat.id, call.from_user.id, gender_choice)

def start_onboarding_sequence(chat_id, user_id, gender):
    onboarding_states[user_id] = {
        'step': 'PHONE_INPUT',
        'gender': gender,
        'api_id': DEFAULT_API_ID,
        'api_hash': DEFAULT_API_HASH,
        'phone': None,
        'client': None,
        'phone_code_hash': None
    }
    msg = bot.send_message(chat_id, f"📱 **SID {gender} MODULE INITIATED**\n\nPlease enter your phone number with your country code (e.g., `+919876543210`):", parse_mode='Markdown')
    bot.register_next_step_handler(msg, process_onboarding_step)

def process_onboarding_step(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_input = message.text.strip() if message.text else ""

    if user_input.lower() == '/cancel':
        onboarding_states.pop(user_id, None)
        return bot.send_message(chat_id, "❌ Registration cancelled.")
        
    if user_id not in onboarding_states: return

    state = onboarding_states[user_id]
    current_step = state['step']

    if current_step == 'PHONE_INPUT':
        state['phone'] = user_input
        progress_msg = bot.send_message(chat_id, "`⚡ Generating ephemeral SID runtime...`", parse_mode='Markdown')
        
        session_id = os.path.join(RUNTIMES_DIR, f"temp_{user_id}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            client = TelegramClient(session_id, state['api_id'], state['api_hash'], loop=loop)
            loop.run_until_complete(client.connect())
            state['client'] = client
            
            send_code_task = client.send_code_request(state['phone'])
            result = loop.run_until_complete(send_code_task)
            state['phone_code_hash'] = result.phone_code_hash
            state['step'] = 'OTP_INPUT'
            
            bot.delete_message(chat_id, progress_msg.message_id)
            msg = bot.send_message(chat_id, f"📥 **OTP Sent to {state['phone']}**\nEnter your verification code below (spaces allowed):", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_onboarding_step)
            
        except Exception as e:
            bot.send_message(chat_id, f"❌ **SID Network Error:** `{e}`")
            onboarding_states.pop(user_id, None)

    elif current_step == 'OTP_INPUT':
        clean_code = user_input.replace(" ", "")
        progress_msg = bot.send_message(chat_id, "`⚙️ Verifying SID token signatures...`", parse_mode='Markdown')
        client = state['client']
        loop = client.loop
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(client.sign_in(state['phone'], code=clean_code, phone_code_hash=state['phone_code_hash']))
            bot.delete_message(chat_id, progress_msg.message_id)
            select_preset_interface(chat_id, user_id)
        except SessionPasswordNeededError:
            state['step'] = 'PASSWORD_2FA_INPUT'
            bot.delete_message(chat_id, progress_msg.message_id)
            msg = bot.send_message(chat_id, "🔒 **2FA Detected**\nEnter your account password:")
            bot.register_next_step_handler(msg, process_onboarding_step)
        except (PhoneCodeInvalidError, PhoneCodeExpiredError):
            bot.delete_message(chat_id, progress_msg.message_id)
            msg = bot.send_message(chat_id, "❌ **Invalid Code.** Try again:")
            bot.register_next_step_handler(msg, process_onboarding_step)
        except Exception as e:
            bot.delete_message(chat_id, progress_msg.message_id)
            bot.send_message(chat_id, f"❌ **Sign-in Fault:** `{e}`")
            onboarding_states.pop(user_id, None)

    elif current_step == 'PASSWORD_2FA_INPUT':
        progress_msg = bot.send_message(chat_id, "`🔐 Verifying 2FA encryption...`", parse_mode='Markdown')
        client = state['client']
        loop = client.loop
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(client.sign_in(password=user_input))
            bot.delete_message(chat_id, progress_msg.message_id)
            select_preset_interface(chat_id, user_id)
        except PasswordHashInvalidError:
            bot.delete_message(chat_id, progress_msg.message_id)
            msg = bot.send_message(chat_id, "❌ **Incorrect Password.** Try again:")
            bot.register_next_step_handler(msg, process_onboarding_step)
        except Exception as e:
            bot.delete_message(chat_id, progress_msg.message_id)
            bot.send_message(chat_id, f"❌ **Fault:** `{e}`")
            onboarding_states.pop(user_id, None)

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 8: AESTHETIC PRESET SELECTION
# ──────────────────────────────────────────────────────────────────────────────
def select_preset_interface(chat_id, user_id):
    state = onboarding_states[user_id]
    gender = state['gender']
    presets = BOY_PRESETS if gender == "BOY" else GIRL_PRESETS
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for index, preset in enumerate(presets):
        markup.add(types.InlineKeyboardButton(f"🎭 {preset}", callback_data=f"finalize_{index}_{user_id}"))
        
    bot.send_message(
        chat_id,
        f"✅ **SID Authentication Successful!**\nChoose your runtime personality profile:",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("finalize_"))
def finalize_and_deploy(call):
    _, index_str, target_uid_str = call.data.split("_")
    user_id = int(target_uid_str)
    
    if call.from_user.id != user_id:
        return bot.answer_callback_query(call.id, "❌ Not your session.")
        
    bot.answer_callback_query(call.id)
    state = onboarding_states.get(user_id)
    if not state:
        return bot.send_message(call.message.chat.id, "❌ Session expired.")
        
    gender = state['gender']
    preset_choice = BOY_PRESETS[int(index_str)] if gender == "BOY" else GIRL_PRESETS[int(index_str)]
    
    client = state['client']
    stable_session_name = os.path.join(RUNTIMES_DIR, f"active_{user_id}")
    client.loop.run_until_complete(client.disconnect())
    
    src_session = os.path.join(RUNTIMES_DIR, f"temp_{user_id}.session")
    dest_session = f"{stable_session_name}.session"
    
    if os.path.exists(src_session):
        if os.path.exists(dest_session): os.remove(dest_session)
        os.rename(src_session, dest_session)
        
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO hosted_sessions VALUES (?, ?, ?, ?, ?, ?)',
                       (user_id, dest_session, gender, preset_choice, state['api_id'], state['api_hash']))
        conn.commit()
        conn.close()
        
    onboarding_states.pop(user_id, None)
    progress_msg = bot.send_message(call.message.chat.id, "`Initializing Setup...`", parse_mode='Markdown')
    success_text = f"🚀 **SID {gender} USERBOT DEPLOYED SUCCESSFULLY**\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n» **Identity:** `{preset_choice}`\n» **Status:** `ACTIVE`\n\nTry sending `.menu`, `.ping`, or `.sid` in any chat!"
    
    SidAnimationLibrary.play_terminal_pulse(call.message.chat.id, progress_msg.message_id, success_text)
    
    # Launch Full Userbot Engine
    threading.Thread(target=deploy_live_userbot_runtime, args=(call.message.chat.id, user_id, gender, preset_choice), daemon=True).start()


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 9: FULL USERBOT ENGINE INJECTION
# ──────────────────────────────────────────────────────────────────────────────
def deploy_live_userbot_runtime(chat_id, user_id, gender, preset_string):
    """Deploys the asynchronous userbot container with ALL functions from d1pr1p.py integrated"""
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT session_key, api_id, api_hash FROM hosted_sessions WHERE user_id = ?', (user_id,))
        record = cursor.fetchone()
        conn.close()
        
    if not record: return
    session_file_path, api_id, api_hash = record
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = TelegramClient(session_file_path.replace(".session", ""), int(api_id), api_hash, loop=loop)
    active_runtimes[user_id] = {'client': client, 'loop': loop, 'thread': threading.current_thread()}
    
    # ── ISOLATED STATE FOR THIS USERBOT ──
    owner_id = user_id
    mylund_users = set()
    active_rebel_loops = {}
    active_akshu_loops = {}
    muted_users = {}
    safe_users = {}
    active_gcmute_loops = {}
    active_reply_modes = {}
    live_forwards = {}
    original_profile = {}
    sys_state = {'auto_react_emoji': None}
    UNAUTH_TEXT = "𝐂ʜʟ 𝐑ɴᴅʏcᴇ 𝐒𝐈𝐃 𝐊ᴇ 𝐋ɴᴅ 𝐏ᴇ 𝐁ᴇᴛʜ 😂🖕🏻🔥"

    # ── ARRAYS FROM USER SCRIPT ──
    RAPIST_MESSAGES = [
        "Gᴜʟᴀᴍɪ ᴋʀ ——➤(🎀)", "Tᴇʀɪ Mᴀ Cʜᴜᴅɪ ——➤(🎀)", "Sᴀʟᴀᴍ Tʜᴏᴋ ——➤(🎀)", " Cʜɪɴᴀᴀʀ ——➤(🎀)",
        "Mᴀᴢᴅᴏᴏʀ ——➤(🎀)", "Hᴀᴡᴀʙᴀᴢᴢ ——➤(🎀)", "𝐃ɪᴘᴇsʜ अब्बू  ʙᴏʟ——➤(🎀)", "Tmkl ——➤(🎀)",
        "Kᴀᴍᴢᴏʀ Kᴜᴛɪʏᴀ ——➤(🎀)", "Bʜᴇᴇᴋ Mᴀɴɢ ——➤(🎀)", "RɴᴅɪMᴏɴ ——➤(🎀)", "Cʜᴜᴅᴀɪ Kɪᴅᴅᴇ ——➤(🎀)",
        "Gʜᴀᴛɪʏᴀ Bᴇᴛᴀ ——➤(🎀)", "Tᴇʀᴀ Bᴀᴀᴘ x𝐃ɪᴘᴇsʜ ——➤(🎀)", "GAɴᴅ Mᴀʀᴀ ᴍᴜʟʟᴇ ——➤(🎀)", 
        "Cʜᴜᴅᴇɢɪ Tᴇʀɪ MA ——➤(🎀)", "BɪᴛCʜ ——➤(🎀)", "HɪJᴅᴜSᴏɴ ——➤(🎀)", "Nᴀʟɪ Sᴀғ Kᴀʀ ᴊAᴋᴇ ——➤(🎀)",
        " GʜɪNᴏɴɪ Rɴ Dz ——➤(🎀)", "Cʜᴏᴛɪ Jᴀᴀᴛ ——➤(🎀)", "TᴇRɪ Mᴀ Kalwɪ ——➤(🎀)", "HɪJᴀB PᴇʜᴇN ——➤(🎀)",
        "Tᴍᴋc Mᴇ KᴏYʟA ——➤(🎀)"
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
        "#𝐃ɪᴘᴇsʜ 𝘉𝘢𝘢𝘱 𝐊𝐎 𝐃𝐁𝐀 𝐍𝐇𝐈 𝐏𝐀R𝐄 ᴄʏᴀ?? 🥶🥱😂", "😹 Tᴇʀɪ 🤪 RᴀNᴅɪ 😫 MᴀA 🤗 Kᴇ 🤢 BᴜR 🤣 Pᴇ 😤 LᴀAᴛ 🙄 MᴀR 😆 Kᴇ 😍 Tᴇʀɪ 😍 BᴇHᴇN 😈 CʜOᴅ 😅 DᴜGᴀ 🤩",
        "GᴀRᴇᴇʙ Ghar Ke Ladke Baap Log Ke Gc Mein Kya Krr Rha 🤢👞", " 🔮 𝐘𝐄 𝐃𝐄𝐊𝐇 𝐉𝐀D𝐔 𝐒𝐄 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐂𝐇𝐎𝐃 𝐃𝐈y𝐚 😂🪄😂🪄", 
        " Teri Maa Ko बाहुबली style mein chodunga 🥶💔🤪😹", "Tumhare Pitashree 𝐃ɪᴘᴇsʜ 💯🔥🗿🌙",
        " Tery behn bole fuck me 𝐃ɪᴘᴇsʜ daddy 😍🌹💋", " तेरी माँ 𝐃ɪᴘᴇsʜ पापा ki दीवानी Since 2k10 😂🖕🏻🔥", " Cover le सस्ती रंडी k काले बच्चे 🤢🤮🖕🏻🥀"
    ]
    
    AKSHU_MESSAGES = RAPIST_MESSAGES
    REBEL_MESSAGES = DIPESH_MESSAGES

    async def operational_lifecycle():
        await client.connect()
        
        try:
            await client(UpdateProfileRequest(
                first_name=preset_string.split()[0],
                about=f"Powered by SID Master Engine 👑 • Profile: {preset_string}"
            ))
        except Exception as e:
            logger.error(f"Profile update fault: {e}")

        def is_authorized(event):
            return event.out or event.sender_id in mylund_users

        async def respond(event, text):
            if event.out:
                await event.edit(text)
            else:
                if not is_authorized(event):
                    try: await client.send_message(event.chat_id, UNAUTH_TEXT, reply_to=event.id)
                    except: pass
                    return False
                try: await event.delete()
                except: pass
                await client.send_message(event.chat_id, text)
            return True

        async def check_unauth_only(event):
            if not is_authorized(event):
                try: await client.send_message(event.chat_id, UNAUTH_TEXT, reply_to=event.id)
                except: pass
                return True
            return False

        # ── SYSTEM ANIMATIONS & CUSTOM ──
        @client.on(events.NewMessage(pattern=r"\.sid", outgoing=True))
        async def sid_alive(event):
            if gender == "BOY":
                text = (f"👑 **SID ENGINE IS DOMINATING** 👑\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"» **Master:** `{preset_string}`\n"
                        f"» **Vibe:** `Aggressive & Unstoppable` 🔥\n"
                        f"» **System:** `Sid Core v5.0`")
            else:
                text = (f"🌸 **SID ENGINE IS THRIVING** 🌸\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"» **Queen:** `{preset_string}`\n"
                        f"» **Vibe:** `Aesthetic & Flawless` ✨\n"
                        f"» **System:** `Sid Core v5.0`")
            await event.edit(text)

        # ── BACKGROUND ENFORCEMENT TASKS ──
        @client.on(events.NewMessage())
        async def mute_enforcement_handler(event):
            chat_id = event.chat_id
            user_id = event.sender_id
            if event.out: return
            if user_id and chat_id in safe_users and user_id in safe_users[chat_id]: return
            is_muted = False
            if chat_id in muted_users:
                if user_id and user_id in muted_users[chat_id]: is_muted = True
                elif chat_id in muted_users[chat_id]: is_muted = True
            if is_muted:
                try: await event.delete()
                except: pass

        @client.on(events.NewMessage())
        async def live_forward_handler(event):
            if event.chat_id in live_forwards and not event.out:
                for target_id in live_forwards[event.chat_id]:
                    try: await client.forward_messages(target_id, event.message)
                    except: pass

        @client.on(events.NewMessage())
        async def auto_react_handler(event):
            if sys_state['auto_react_emoji'] and event.out:
                try:
                    await client(telethon.functions.messages.SendReactionRequest(
                        peer=event.input_chat, msg_id=event.id,
                        reaction=[telethon.tl.types.ReactionEmoji(emoticon=sys_state['auto_react_emoji'])]
                    ))
                except telethon.errors.FloodWaitError as e:
                    await asyncio.sleep(e.seconds)
                except: pass

        @client.on(events.NewMessage())
        async def gcmute_delete_handler(event):
            chat_id = event.chat_id
            if not active_gcmute_loops.get(chat_id, False): return
            if event.out: return
            if event.sender_id and chat_id in safe_users and event.sender_id in safe_users[chat_id]: return
            try: await event.delete()
            except: pass

        @client.on(events.NewMessage())
        async def auto_reply_handler(event):
            if event.out: return
            chat_id = event.chat_id
            user_id = event.sender_id
            if chat_id not in active_reply_modes or user_id not in active_reply_modes[chat_id]: return
            try:
                await client.send_message(chat_id, active_reply_modes[chat_id][user_id], reply_to=event.id)
            except telethon.errors.FloodWaitError as e: await asyncio.sleep(e.seconds)
            except: pass

        # ── COMMANDS: OWNER & AUTHORIZED ──
        @client.on(events.NewMessage(pattern=r"\.mylund", outgoing=True))
        async def mylund_handler(event):
            if ".bhagmc" in event.message.message: return  
            if not event.is_reply:
                return await event.edit("❌ Reply to someone's message to grant them bot access.")
            target_id = (await event.get_reply_message()).sender_id
            if target_id == owner_id: return await event.edit("⚠️ That's you — you already own the bot.")
            mylund_users.add(target_id)
            await event.edit(f"✅ User ID: {target_id} can now use the bot.\nTotal users: {len(mylund_users)}")

        @client.on(events.NewMessage(pattern=r"\.bhagmc", outgoing=True))
        async def bhagmc_handler(event):
            if event.is_reply: target_id = (await event.get_reply_message()).sender_id
            else:
                args = event.message.message.split()
                if len(args) > 1:
                    try: target_id = (await client.get_entity(args[1])).id
                    except Exception as e: return await event.edit(f"❌ Error: {e}")
                else: return await event.edit("❌ Reply to message or .bhagmc @username")
            if target_id in mylund_users:
                mylund_users.discard(target_id)
                await event.edit(f"🚫 User removed. Total authorized: {len(mylund_users)}")
            else: await event.edit("⚠️ User didn't have access.")

        @client.on(events.NewMessage(pattern=r"\.lund$"))
        async def list_authorized_handler(event):
            if not is_authorized(event): return await respond(event, "")
            out_text ="✨ <b>BOT AUTHORITY DETAILS</b> ✨\n──────────────────────────\n"
            out_text += f"👑 <b>Owner:</b> [<code>{owner_id}</code>]\n\n🎀 <b>Authorized List:</b>\n"
            if not mylund_users: out_text += "» <i>No extra users authorized yet.</i>"
            else:
                for i, u_id in enumerate(mylund_users, 1): out_text += f"{i}. User [<code>{u_id}</code>]\n"
            out_text += "\n──────────────────────────"
            await event.edit(out_text, parse_mode="html") if event.out else await client.send_message(event.chat_id, out_text, parse_mode="html")

        @client.on(events.NewMessage(pattern=r"\.refresh"))
        async def refresh_handler(event):
            if not is_authorized(event): return await respond(event, "")
            mylund_users.clear()
            muted_users.clear()
            active_gcmute_loops.clear()
            txt = "🔄 <b>System Refreshed Successfully!</b>\n\n» Authorized users emptied.\n» Muted users cleared.\n» Global mutes reset."
            await event.edit(txt, parse_mode="html") if event.out else await client.send_message(event.chat_id, txt, parse_mode="html")

        @client.on(events.NewMessage(pattern=r"\.safe"))
        async def safe_handler(event):
            if await check_unauth_only(event): return
            if ".unsafe" in event.message.message: return
            if not event.is_reply: return await respond(event, "❌ Reply to message.")
            target_id = (await event.get_reply_message()).sender_id
            if event.chat_id not in safe_users: safe_users[event.chat_id] = set()
            safe_users[event.chat_id].add(target_id)
            await respond(event, f"🛡 User ID {target_id} is safe from deletions.")

        @client.on(events.NewMessage(pattern=r"\.unsafe"))
        async def unsafe_handler(event):
            if await check_unauth_only(event): return
            if event.is_reply: target_id = (await event.get_reply_message()).sender_id
            else:
                try: target_id = (await client.get_entity(event.message.message.split()[1])).id
                except: return await respond(event, "❌ Reply to a message or use: .unsafe @user")
            if event.chat_id in safe_users and target_id in safe_users[event.chat_id]:
                safe_users[event.chat_id].discard(target_id)
                await respond(event, "⚠️ Removed from safe mode.")
            else: await respond(event, "⚠️ Wasn't in safe mode.")

        # ── SPAM & RAID ──
        @client.on(events.NewMessage(pattern=r"\.akshu$"))
        async def akshu_handler(event):
            if not is_authorized(event): return await respond(event, "")
            if not event.is_reply: return await respond(event, "❌ Reply with .akshu")
            if active_akshu_loops.get(event.chat_id): return await respond(event, "⚠️ Loop already active.")
            reply_msg = await event.get_reply_message()
            try: await event.delete()
            except: pass
            active_akshu_loops[event.chat_id] = True
            while active_akshu_loops.get(event.chat_id):
                for msg_text in AKSHU_MESSAGES:
                    if not active_akshu_loops.get(event.chat_id): break
                    try:
                        await client.send_message(event.chat_id, msg_text, reply_to=reply_msg.id)
                        await asyncio.sleep(0.5)  
                    except telethon.errors.FloodWaitError as e: await asyncio.sleep(e.seconds)
                    except: await asyncio.sleep(2)

        @client.on(events.NewMessage(pattern=r"\.akshustop"))
        async def akshustop_handler(event):
            if not is_authorized(event): return await respond(event, "")
            if active_akshu_loops.get(event.chat_id):
                active_akshu_loops[event.chat_id] = False
                await respond(event, "🛑 Akshu loop stopped.")
            else: await respond(event, "❌ No active Akshu loop.")

        @client.on(events.NewMessage(pattern=r"\.rebel$|\.dipesh$|\.rapist$"))
        async def rebel_handler(event):
            if not is_authorized(event): return await respond(event, "")
            if not event.is_reply: return await respond(event, "❌ Reply with command")
            if active_rebel_loops.get(event.chat_id): return await respond(event, "⚠️ Loop already active.")
            reply_msg = await event.get_reply_message()
            try: await event.delete()
            except: pass
            active_rebel_loops[event.chat_id] = True
            count = 0
            while active_rebel_loops.get(event.chat_id):
                for msg_text in REBEL_MESSAGES:
                    if not active_rebel_loops.get(event.chat_id): break
                    try:
                        await client.send_message(event.chat_id, msg_text, reply_to=reply_msg.id)
                        count += 1
                        if count % 3 == 0: await asyncio.sleep(3)
                        else: await asyncio.sleep(1)
                    except telethon.errors.FloodWaitError as e: await asyncio.sleep(e.seconds)
                    except: await asyncio.sleep(5)

        @client.on(events.NewMessage(pattern=r"\.rebelstop|\.dipeshstop|\.rapiststop"))
        async def rebelstop_handler(event):
            if not is_authorized(event): return await respond(event, "")
            if active_rebel_loops.get(event.chat_id):
                active_rebel_loops[event.chat_id] = False
                await respond(event, "🛑 Loop stopped.")
            else: await respond(event, "❌ No active loop.")

        @client.on(events.NewMessage(pattern=r"\.homies"))
        async def homies_handler(event):
            if not is_authorized(event): return await respond(event, "")
            try: await event.delete()
            except: pass
            for msg_text in HOMIES_MESSAGES:
                try:
                    if event.is_reply: await client.send_message(event.chat_id, msg_text, reply_to=event.reply_to_msg_id)
                    else: await client.send_message(event.chat_id, msg_text)
                    await asyncio.sleep(1.5)
                except telethon.errors.FloodWaitError as e: await asyncio.sleep(e.seconds)
                except: pass

        # ── UTILITIES & DOWNLOADERS ──
        @client.on(events.NewMessage(pattern=r"\.ping"))
        async def ping_handler(event):
            if not is_authorized(event): return await respond(event, "")
            start = time.time()
            msg = await event.edit("⚡ `Pinging...`") if event.out else await client.send_message(event.chat_id, "⚡ `Pinging...`")
            ms = round((time.time() - start) * 1000, 2)
            await msg.edit(f"🚀 **SID PONG**\n» `{ms} ms`")

        @client.on(events.NewMessage(pattern=r"\.purge"))
        async def purge_handler(event):
            if not is_authorized(event): return await respond(event, "")
            args = event.message.message.split()
            msgs = []
            if event.is_reply:
                async for msg in client.iter_messages(event.chat_id, min_id=event.reply_to_msg_id - 1):
                    msgs.append(msg.id)
            else:
                limit = int(args[1]) + 1 if len(args) > 1 and args[1].isdigit() else 1
                async for msg in client.iter_messages(event.chat_id, limit=limit):
                    msgs.append(msg.id)
            if msgs:
                for i in range(0, len(msgs), 100):
                    await client.delete_messages(event.chat_id, msgs[i:i+100])
                conf = await client.send_message(event.chat_id, f"🗑️ Purged {len(msgs)-1} messages.")
                await asyncio.sleep(2); await conf.delete()

        @client.on(events.NewMessage(pattern=r"\.react"))
        async def react_command_handler(event):
            if not is_authorized(event): return await respond(event, "")
            emoji = event.message.message.replace(".react", "").strip()
            sys_state['auto_react_emoji'] = emoji if emoji else None
            await respond(event, f"✅ Auto-react set to {emoji}" if emoji else "🛑 Auto-react disabled.")

        @client.on(events.NewMessage(pattern=r"\.forward"))
        async def forward_handler(event):
            if not is_authorized(event): return await respond(event, "")
            args = event.message.message.split()
            if len(args) < 2: return await respond(event, "❌ Usage: .forward [link]")
            try:
                src_id = (await client.get_entity(args[1])).id
                if src_id not in live_forwards: live_forwards[src_id] = []
                if event.chat_id not in live_forwards[src_id]:
                    live_forwards[src_id].append(event.chat_id)
                    await respond(event, "✅ Live sync enabled.")
            except Exception as e: await respond(event, f"❌ Error: {e}")

        @client.on(events.NewMessage(pattern=r"\.song"))
        async def song_handler(event):
            if not is_authorized(event): return await respond(event, "")
            song_name = event.message.message.replace(".song", "").strip()
            if not song_name: return await respond(event, "❌ Provide a song name")
            await respond(event, f"🎵 Downloading: {song_name}...")
            file_base = f"temp_song_{event.id}"
            ydl_opts = {
                'format': 'bestaudio/best', 'outtmpl': f'{file_base}.%(ext)s',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
                'quiet': True, 'default_search': 'ytsearch1'
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"ytsearch1:{song_name}", download=True)
                    fpath = f"{file_base}.mp3"
                    if os.path.exists(fpath):
                        await client.send_file(event.chat_id, fpath, reply_to=event.reply_to_msg_id)
                        os.remove(fpath)
                        try: await event.delete()
                        except: pass
                    else: await respond(event, "❌ Failed to download.")
            except Exception as e: await respond(event, f"❌ Error: {e}")

        @client.on(events.NewMessage(pattern=r"\.copy", outgoing=True))
        async def copy_handler(event):
            if event.is_reply: target = await client.get_entity((await event.get_reply_message()).sender_id)
            else:
                try: target = await client.get_entity(event.message.message.split()[1])
                except: return await event.edit("❌ Provide target.")
            await event.edit("🔄 Cloning profile data...")
            try:
                me = await client.get_me()
                if not original_profile:
                    original_profile['first_name'] = me.first_name or ""
                    original_profile['last_name'] = me.last_name or ""
                    ph = await client.get_profile_photos('me')
                    original_profile['photo'] = await client.download_profile_photo('me') if ph else None
                
                await client(UpdateProfileRequest(first_name=target.first_name or "", last_name=target.last_name or ""))
                tgt_ph = await client.download_profile_photo(target)
                if tgt_ph:
                    if (my_ph := await client.get_profile_photos('me')):
                        await client(DeletePhotosRequest(id=[p for p in my_ph]))
                    await client(UploadProfilePhotoRequest(file=await client.upload_file(tgt_ph)))
                    os.remove(tgt_ph)
                await event.edit("Summon successful 🤍🦋")
            except Exception as e: await event.edit(f"❌ Error: {e}")

        @client.on(events.NewMessage(pattern=r"\.back", outgoing=True))
        async def back_handler(event):
            if not original_profile: return await event.edit("❌ No backup found.")
            await event.edit("🔄 Reverting profile...")
            try:
                await client(UpdateProfileRequest(first_name=original_profile.get('first_name',""), last_name=original_profile.get('last_name',"")))
                if original_profile.get('photo') and os.path.exists(original_profile['photo']):
                    if (my_ph := await client.get_profile_photos('me')):
                        await client(DeletePhotosRequest(id=[p for p in my_ph]))
                    await client(UploadProfilePhotoRequest(file=await client.upload_file(original_profile['photo'])))
                await event.edit("✅ Profile restored!")
            except Exception as e: await event.edit(f"❌ Error: {e}")

        # ── MUTING & ADMIN CONTROLS ──
        @client.on(events.NewMessage(pattern=r"\.mute"))
        async def mute_handler(event):
            if not is_authorized(event) or ".unmute" in event.message.message: return
            if event.is_reply: user_id = (await event.get_reply_message()).sender_id
            else:
                try: user_id = (await client.get_entity(event.message.message.split()[1])).id
                except: return await respond(event, "❌ Provide user")
            if event.chat_id not in muted_users: muted_users[event.chat_id] = set()
            muted_users[event.chat_id].add(user_id)
            await respond(event, "🤫 User muted in this chat.")

        @client.on(events.NewMessage(pattern=r"\.unmute"))
        async def unmute_handler(event):
            if not is_authorized(event): return
            if event.is_reply: user_id = (await event.get_reply_message()).sender_id
            else:
                try: user_id = (await client.get_entity(event.message.message.split()[1])).id
                except: return
            if event.chat_id in muted_users and user_id in muted_users[event.chat_id]:
                muted_users[event.chat_id].discard(user_id)
                await respond(event, "🔊 User unmuted.")

        @client.on(events.NewMessage(pattern=r"\.gcmute"))
        async def gcmute_handler(event):
            if not is_authorized(event) or ".gcunmute" in event.message.message: return
            active_gcmute_loops[event.chat_id] = True
            await respond(event, "🗑️ gcmute mode activated.")

        @client.on(events.NewMessage(pattern=r"\.gcunmute"))
        async def gcunmute_handler(event):
            if not is_authorized(event): return
            active_gcmute_loops[event.chat_id] = False
            await respond(event, "✅ gcmute deactivated.")

        @client.on(events.NewMessage(pattern=r"\.reply"))
        async def reply_mode_handler(event):
            if not is_authorized(event): return
            txt = event.message.message.replace(".reply", "").strip()
            if not event.is_reply or not txt: return await respond(event, "❌ Reply to someone & give text.")
            if event.chat_id not in active_reply_modes: active_reply_modes[event.chat_id] = {}
            active_reply_modes[event.chat_id][(await event.get_reply_message()).sender_id] = txt
            await respond(event, "💬 Auto-reply active.")

        @client.on(events.NewMessage(pattern=r"\.sreply"))
        async def sreply_handler(event):
            if not is_authorized(event): return
            if event.chat_id in active_reply_modes:
                del active_reply_modes[event.chat_id]
                await respond(event, "⏹️ Auto-reply cleared.")

        @client.on(events.NewMessage(pattern=r"\.stop"))
        async def stop_handler(event):
            if not is_authorized(event): return
            active_rebel_loops[event.chat_id] = False
            active_akshu_loops[event.chat_id] = False
            active_gcmute_loops[event.chat_id] = False
            sys_state['auto_react_emoji'] = None
            if event.chat_id in muted_users: del muted_users[event.chat_id]
            if event.chat_id in active_reply_modes: del active_reply_modes[event.chat_id]
            for s in list(live_forwards.keys()):
                if event.chat_id in live_forwards[s]: live_forwards[s].remove(event.chat_id)
            await respond(event, "🛑 All background tasks stopped in this chat.")

        @client.on(events.NewMessage(pattern=r"\.admin"))
        async def admin_handler(event):
            if not is_authorized(event): return
            if event.is_reply: tgt = await client.get_entity((await event.get_reply_message()).sender_id)
            else:
                try: tgt = await client.get_entity(event.message.message.split()[1])
                except: return
            try:
                await client(telethon.functions.channels.EditAdminRequest(
                    channel=event.chat_id, user_id=tgt,
                    admin_rights=ChatAdminRights(change_info=True, post_messages=True, edit_messages=True, delete_messages=True, ban_users=True, invite_users=True, pin_messages=True, add_admins=True, manage_call=True, other=True),
                    rank="Admin"
                ))
                await respond(event, "✅ Promoted to admin.")
            except Exception as e: await respond(event, f"❌ Error: {e}")

        @client.on(events.NewMessage(pattern=r"\.take"))
        async def take_handler(event):
            if not is_authorized(event): return
            if event.is_reply: tgt = await client.get_entity((await event.get_reply_message()).sender_id)
            else:
                try: tgt = await client.get_entity(event.message.message.split()[1])
                except: return
            try:
                await client(telethon.functions.channels.EditAdminRequest(channel=event.chat_id, user_id=tgt, admin_rights=ChatAdminRights(), rank=""))
                await respond(event, "✅ Demoted.")
            except Exception as e: await respond(event, f"❌ Error: {e}")

        @client.on(events.NewMessage(pattern=r"\.kick"))
        async def kick_handler(event):
            if not is_authorized(event): return
            if event.is_reply: tgt = await client.get_entity((await event.get_reply_message()).sender_id)
            else:
                try: tgt = await client.get_entity(event.message.message.split()[1])
                except: return
            try:
                await client.kick_participant(event.chat_id, tgt)
                await respond(event, "👢 Kicked.")
            except Exception as e: await respond(event, f"❌ Error: {e}")
            
        @client.on(events.NewMessage(pattern=r"\.menu"))
        async def menu_handler(event):
            if not is_authorized(event): return
            MENU_TEXT = """
            ===================================
                     🤍 𝐒𝐈𝐃 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 🤍
    ===================================
    💛 𝗥𝗔𝗜𝗗 𝗦𝗬𝗦𝗧𝗘𝗠 💛
     • .dipesh / .rebel / .rapist [ Rᴀɪᴅ ]
     • .dipeshstop / .rebelstop [ Sᴛᴏᴘ Rᴀɪᴅ ]
     • .akshu 🔄 / .akshustop 🛑
     • .reply 🌸 / .sreply ⏹️
     • .stop 🍂 [ Sᴛᴏᴘ Aʟʟ Aᴄᴛɪᴠɪᴛɪᴇs ]
    🩷  𝗠𝗘𝗗𝗜𝗔 🩷
     • .song 🎵
    💙 𝗥𝗡𝗗𝗬 𝗥𝗢𝗡𝗔 💙
     • .purge 🗑
     • .mute 🤫 / .unmute 🔊 / .gcmute 🗑
     • .react 💫 / .forward 🔗
    🎀 𝗕𝗢𝗧𝗦 🎀
     • .admin 👑 / .take 🚫 / .kick 👢
    👻 𝗕𝗔𝗞𝗖𝗛𝗢𝗗𝗜 👻
     • .copy 🌙 / .back 🌿
     • .ping 🚀 / .refresh 🔄
    🖤 𝗔𝗗𝗠𝗜𝗡 𝗔𝗨𝗧𝗛𝗢𝗥𝗜𝗧𝗬 🖤
     • .homies 🎀 / .lund 👑
     • .mylund 🤍 / .bhagmc 🖤
    💚 𝗣𝗥𝗢𝗧𝗘𝗖𝗧 💚
     • .safe 🛡 / .unsafe 🌸
    ===================================
    MᴀDᴇ ʙʏ 𝐒𝐈𝐃 👑
    ===================================""".strip()
            await respond(event, MENU_TEXT)

        await client.run_until_disconnected()

    try:
        loop.run_until_complete(operational_lifecycle())
    except Exception as e:
        logger.error(f"Context dropped: {e}")
    finally:
        active_runtimes.pop(user_id, None)


# ──────────────────────────────────────────────────────────────────────────────
# SECTION 10: TELEMETRY & WORKER MANAGEMENT
# ──────────────────────────────────────────────────────────────────────────────
@bot.callback_query_handler(func=lambda call: call.data == "telemetry")
def display_telemetry(call):
    total_active = len(active_runtimes)
    ram = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent()
    text = (f"📊 **SID TELEMETRY DATA**\n━━━━━━━━━━━━━━━━━━━━\n"
            f"🟢 **Active Containers:** `{total_active}`\n🧠 **Host RAM Usage:** `{ram}%`\n"
            f"⚙️ **Host CPU Load:** `{cpu}%`\n\n» *Architecture designed for dynamic scalability.*")
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "terminate")
def terminate_worker(call):
    user_id = call.from_user.id
    if user_id in active_runtimes:
        client = active_runtimes[user_id]['client']
        loop = active_runtimes[user_id]['loop']
        loop.create_task(client.disconnect())
        bot.answer_callback_query(call.id, "🛑 SID Container Terminated Successfully.", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❌ No active runtimes detected.", show_alert=True)

def safe_shutdown():
    logger.info("Initiating safe shutdown of all SID containers...")
    for user_id, elements in list(active_runtimes.items()):
        elements['loop'].run_until_complete(elements['client'].disconnect())

atexit.register(safe_shutdown)

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 11: SYSTEM LAUNCHPAD
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    logger.info("Initializing SID Master Thread Pools...")
    Thread(target=initialize_keepalive_server, daemon=True).start()
    
    logger.info("SID Host Master Online. Entering infinite polling...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            logger.critical(f"Master Polling Loop Collapsed: {e}. Retrying...")
            time.sleep(5)
