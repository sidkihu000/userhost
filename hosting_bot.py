# -*- coding: utf-8 -*-
"""
================================━━━━━━━━================================
                 ✨ TELEGRAM USERBOT MASTER HOSTING ENGINE ✨
================================━━━━━━━━================================
Core Architecture: pyTelegramBotAPI (Master Controller) + Telethon (Dynamic Runtimes)
Features: Step-by-Step OTP/2FA Authentication, Segmented Profiles, Live Telemetry
"""

import os
import sys
import re
import time
import json
import uuid
import shutil
import logging
import sqlite3
import asyncio
import atexit
import psutil
import tempfile
import threading
import subprocess
import importlib.util
from datetime import datetime, timedelta

import telebot
from telebot import types
from flask import Flask
from threading import Thread

from telethon import TelegramClient, events
from telethon.errors import (
    SessionPasswordNeededError, 
    PhoneCodeInvalidError, 
    PasswordHashInvalidError,
    PhoneCodeExpiredError
)
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 1: SYSTEM LOGGING & ENVIRONMENT INITIALIZATION
# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("UserbotHostMaster")

# Absolute system paths configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
RUNTIMES_DIR = os.path.join(BASE_DIR, 'userbot_runtimes')
DATA_STORAGE_DIR = os.path.join(BASE_DIR, 'core_metadata')
DATABASE_PATH = os.path.join(DATA_STORAGE_DIR, 'hosting_matrix.db')

os.makedirs(RUNTIMES_DIR, exist_ok=True)
os.makedirs(DATA_STORAGE_DIR, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 2: WEB RECOVERY LAYER (FLASK COMPLIANCE)
# ──────────────────────────────────────────────────────────────────────────────
web_app = Flask('MatrixHostServer')

@web_app.route('/')
def health_check():
    return "<h3>Matrix Engine Core Status: ONLINE</h3>", 200

def initialize_keepalive_server():
    server_port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=server_port)

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 3: CONSTANTS, PRESETS & RESOURCE PAYLOADS
# ──────────────────────────────────────────────────────────────────────────────
BOT_TOKEN = '7096730412:AAHhv6RLDMW_WXfo2QMUuEdRRRTrAMOTsn0'
PRIMARY_OWNER_ID = 2119464081
SUPPORT_CHANNEL_URL = 'https://t.me/+5uCnxp3U1gMwZjQ1'

DEFAULT_API_ID = 32082988
DEFAULT_API_HASH = "a81844a473550947cfff864a8c7489cd"

# Boy Profile Preset Array
BOY_PRESETS = [
    "DIPESH GAWD 😈", "REBEL BAAP 👑", "AKSHU KENG 🔥", 
    "SID RULE SERVER 😎", "DEADLY MARCO 💀"
]

# Girl Profile Preset Array
GIRL_PRESETS = [
    "NISHANT BADDIE 🎀", "YASH CHHAKA 👌🏻🎀", "KUTIYA SOON 💅🏻", 
    "ANGEL QUEEN ✨", "ROSE PRINCESS 🌸"
]

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 4: STATE MANAGEMENT SYSTEM & TRANSACTIONS
# ──────────────────────────────────────────────────────────────────────────────
GLOBAL_DB_LOCK = threading.Lock()
active_runtimes = {}     # Active live background tasks
onboarding_states = {}   # Interactive connection sequence storage
cached_authorizations = set()

def execute_db_migration():
    """Build structural state tables if missing from runtime node"""
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS system_authorizations
                         (user_id INTEGER PRIMARY KEY, identity_tier TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS hosted_sessions
                         (user_id INTEGER PRIMARY KEY, session_key TEXT, system_preset TEXT, api_id INTEGER, api_hash TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS configuration_records
                         (config_key TEXT PRIMARY KEY, config_value TEXT)''')
        
        cursor.execute('INSERT OR IGNORE INTO system_authorizations VALUES (?, ?)', (PRIMARY_OWNER_ID, 'OWNER'))
        conn.commit()
        conn.close()

def sync_authorizations_cache():
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM system_authorizations')
        for (uid,) in cursor.fetchall():
            cached_authorizations.add(uid)
        conn.close()

execute_db_migration()
sync_authorizations_cache()

# Initialize pyTelegramBotAPI
bot = telebot.TeleBot(BOT_TOKEN)

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 5: INTERACTIVE ANIMATION ENGINE UI
# ──────────────────────────────────────────────────────────────────────────────
class AnimationFrameLibrary:
    @staticmethod
    def construct_progress_bar(percentage, segment_width=10):
        filled_blocks = int(round((percentage / 100.0) * segment_width))
        empty_blocks = segment_width - filled_blocks
        return f"[{'⚡' * filled_blocks}{'   ' * empty_blocks}] {percentage}%"

    @staticmethod
    def play_terminal_pulse(chat_id, target_msg_id, final_message_text, update_markup=None):
        """Asynchronous execution framework to animate multi-stage processing logs"""
        frames = ["🔄 Matrix Initialization...", "🧬 Allocating Secure Memory Core...", "📡 Link Established! Parsing Session..."]
        def pipeline_execution():
            try:
                for frame in frames:
                    bot.edit_message_text(f"`{frame}`", chat_id, target_msg_id, parse_mode='Markdown')
                    time.sleep(0.8)
                bot.edit_message_text(final_message_text, chat_id, target_msg_id, reply_markup=update_markup, parse_mode='Markdown')
            except Exception as pipeline_error:
                logger.error(f"UI Terminal frame rendering error: {pipeline_error}")
        Thread(target=pipeline_execution, daemon=True).start()

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 6: MULTI-STEP VERIFICATION & REGISTRATION FLOW (OTP & 2FA)
# ──────────────────────────────────────────────────────────────────────────────
def start_onboarding_sequence(chat_id, user_id):
    onboarding_states[user_id] = {
        'step': 'PHONE_INPUT',
        'api_id': DEFAULT_API_ID,
        'api_hash': DEFAULT_API_HASH,
        'phone': None,
        'client': None,
        'phone_code_hash': None
    }
    msg = bot.send_message(
        chat_id, 
        "📱 **Starting Authentication Protocol**\n\nPlease enter your phone number with your country code (e.g., `+1234567890`):", 
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, process_onboarding_step)

def process_onboarding_step(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_input = message.text.strip() if message.text else ""

    if user_input.lower() == '/cancel':
        onboarding_states.pop(user_id, None)
        bot.send_message(chat_id, "❌ Registration process cancelled.")
        return

    if user_id not in onboarding_states:
        return

    state = onboarding_states[user_id]
    current_step = state['step']

    if current_step == 'PHONE_INPUT':
        state['phone'] = user_input
        progress_msg = bot.send_message(chat_id, "`⚡ Generating ephemeral security runtime infrastructure...`", parse_mode='Markdown')
        
        # Initialize an isolated loop context for the Telethon instance connection sequence
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
            msg = bot.send_message(chat_id, f"📥 **OTP Sent Successfully to {state['phone']}**\nPlease enter your verification code below:", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_onboarding_step)
            
        except Exception as connection_fault:
            logger.error(f"Authentication channel drop: {connection_fault}")
            bot.send_message(chat_id, f"❌ **Connection Error:** `{connection_fault}`\nUse /host to restart.")
            onboarding_states.pop(user_id, None)

    elif current_step == 'OTP_INPUT':
        progress_msg = bot.send_message(chat_id, "`⚙️ Verifying token signatures...`", parse_mode='Markdown')
        client = state['client']
        loop = client.loop
        
        asyncio.set_event_loop(loop)
        try:
            sign_in_task = client.sign_in(state['phone'], code=user_input, phone_code_hash=state['phone_code_hash'])
            loop.run_until_complete(sign_in_task)
            
            # OTP Verified successfully without a 2FA prompt
            bot.delete_message(chat_id, progress_msg.message_id)
            finalize_onboarding_session(chat_id, user_id)
            
        except SessionPasswordNeededError:
            # 2FA account setup detected
            state['step'] = 'PASSWORD_2FA_INPUT'
            bot.delete_message(chat_id, progress_msg.message_id)
            msg = bot.send_message(chat_id, "🔒 **Two-Factor Authentication (2FA) Detected**\nPlease enter your account password:", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_onboarding_step)
            
        except (PhoneCodeInvalidError, PhoneCodeExpiredError) as code_error:
            bot.delete_message(chat_id, progress_msg.message_id)
            msg = bot.send_message(chat_id, f"❌ **Invalid/Expired Code ({code_error}).** Try again or send /cancel:", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_onboarding_step)
            
        except Exception as general_error:
            bot.delete_message(chat_id, progress_msg.message_id)
            bot.send_message(chat_id, f"❌ **Sign-in Fault:** `{general_error}`\nProcess aborted.")
            onboarding_states.pop(user_id, None)

    elif current_step == 'PASSWORD_2FA_INPUT':
        progress_msg = bot.send_message(chat_id, "`🔐 Verifying 2FA parameters...`", parse_mode='Markdown')
        client = state['client']
        loop = client.loop
        
        asyncio.set_event_loop(loop)
        try:
            sign_in_task = client.sign_in(password=user_input)
            loop.run_until_complete(sign_in_task)
            
            bot.delete_message(chat_id, progress_msg.message_id)
            finalize_onboarding_session(chat_id, user_id)
            
        except PasswordHashInvalidError:
            bot.delete_message(chat_id, progress_msg.message_id)
            msg = bot.send_message(chat_id, "❌ **Incorrect 2FA Password.** Please try again:", parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_onboarding_step)
            
        except Exception as general_error:
            bot.delete_message(chat_id, progress_msg.message_id)
            bot.send_message(chat_id, f"❌ **2FA Verification Fault:** `{general_error}`\nProcess aborted.")
            onboarding_states.pop(user_id, None)

def finalize_onboarding_session(chat_id, user_id):
    state = onboarding_states[user_id]
    client = state['client']
    
    # Persistent session mapping configuration
    stable_session_name = os.path.join(RUNTIMES_DIR, f"active_{user_id}")
    
    # Safe system handoff
    client.loop.run_until_complete(client.disconnect())
    
    src_session = os.path.join(RUNTIMES_DIR, f"temp_{user_id}.session")
    dest_session = f"{stable_session_name}.session"
    
    if os.path.exists(src_session):
        if os.path.exists(dest_session):
            os.remove(dest_session)
        os.rename(src_session, dest_session)
        
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO hosted_sessions VALUES (?, ?, ?, ?, ?)',
                       (user_id, dest_session, 'UNSET', state['api_id'], state['api_hash']))
        conn.commit()
        conn.close()
        
    onboarding_states.pop(user_id, None)
    
    # Prompt the user for the structural profile configuration setup
    display_gender_selection_interface(chat_id, user_id)

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 7: GENDER-BASED PRESET PROFILE MANAGER (BOY / GIRL SECTIONS)
# ──────────────────────────────────────────────────────────────────────────────
def display_gender_selection_interface(chat_id, user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("👑 Boy Profile Variant", callback_data=f"set_gender_boy_{user_id}"),
        types.InlineKeyboardButton("🎀 Girl Profile Variant", callback_data=f"set_gender_girl_{user_id}")
    )
    bot.send_message(
        chat_id,
        "🎭 **Profile Specialization Target Configured Successfully!**\n"
        "Please select your specialized runtime behavior engine module context from the list below:",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_gender_"))
def handle_gender_specialization(call):
    payload = call.data.replace("set_gender_", "")
    gender_type, target_uid_str = payload.split("_")
    target_uid = int(target_uid_str)
    
    if call.from_user.id != target_uid:
        bot.answer_callback_query(call.id, "❌ Access Denied: Session mismatch.", show_alert=True)
        return
        
    bot.answer_callback_query(call.id)
    presets = BOY_PRESETS if gender_type == "boy" else GIRL_PRESETS
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for index, preset_str in enumerate(presets):
        markup.add(types.InlineKeyboardButton(preset_str, callback_data=f"select_preset_{gender_type}_{index}_{target_uid}"))
        
    bot.edit_message_text(
        f"🎭 **Configuring System Behavior Preset Mode**\nSelect your targeted variant configuration script option below:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_preset_"))
def finalize_system_preset(call):
    payload = call.data.replace("select_preset_", "")
    gender_type, index_str, target_uid_str = payload.split("_")
    index = int(index_str)
    target_uid = int(target_uid_str)
    
    if call.from_user.id != target_uid:
        bot.answer_callback_query(call.id, "❌ Authorization Failure.")
        return
        
    bot.answer_callback_query(call.id)
    selected_preset = BOY_PRESETS[index] if gender_type == "boy" else GIRL_PRESETS[index]
    
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE hosted_sessions SET system_preset = ? WHERE user_id = ?', (selected_preset, target_uid))
        conn.commit()
        conn.close()
        
    processing_notice = bot.send_message(call.message.chat.id, "`📡 Mapping parameters to backend runtime container instance...`", parse_mode='Markdown')
    
    # Initialize the runtime container deployment sequence
    threading.Thread(target=deploy_live_userbot_runtime, args=(call.message.chat.id, target_uid, selected_preset), daemon=True).start()

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 8: RUNTIME ENGINE CONTROLLER & SUBPROCESS WORKER
# ──────────────────────────────────────────────────────────────────────────────
def deploy_live_userbot_runtime(chat_id, user_id, preset_string):
    """Deploys an asynchronous, independent client lifecycle layer inside an execution thread"""
    with GLOBAL_DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT session_key, api_id, api_hash FROM hosted_sessions WHERE user_id = ?', (user_id,))
        record = cursor.fetchone()
        conn.close()
        
    if not record:
        bot.send_message(chat_id, "❌ **Runtime Error:** Initialization matrix record missing.")
        return
        
    session_file_path, api_id, api_hash = record
    bot.send_message(chat_id, f"🟢 **Deploying Framework Daemon for {preset_string}...**\nInstantiating asynchronous loop bindings.")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    client = TelegramClient(session_file_path.replace(".session", ""), int(api_id), api_hash, loop=loop)
    active_runtimes[user_id] = {'client': client, 'loop': loop, 'thread': threading.current_thread()}
    
    async def operational_lifecycle():
        await client.connect()
        me = await client.get_me()
        logger.info(f"Dynamically authenticated hosted userbot interface: {me.id}")
        
        # Operational preset updates configuration hook
        try:
            await client(UpdateProfileRequest(
                first_name=preset_string.split()[0],
                about=f"Matrix Hosted Dynamic Bot Engine Layer • Preset Variant: {preset_string}"
            ))
        except Exception as profile_sync_fault:
            logger.error(f"Failed to synchronize profile metadata parameters: {profile_sync_fault}")
            
        # Command interceptor definition within the virtual client runtime context
        @client.on(events.NewMessage(pattern=r"\.ping", outgoing=True))
        async def runtime_ping_handler(event):
            start_time = datetime.now()
            msg = await event.edit("⚡ `System Latency Metric Check...`")
            end_time = datetime.now()
            duration_ms = (end_time - start_time).microseconds / 1000
            await msg.edit(f"🚀 **Host Processing Speed Node Core Online**\n» RTT Metric: `{duration_ms:.2f} ms` \n» Profile: `{preset_string}`")

        await client.run_until_disconnected()

    try:
        loop.run_until_complete(operational_lifecycle())
    except Exception as runtime_fault:
        logger.error(f"Subprocess context collapsed for client {user_id}: {runtime_fault}")
        bot.send_message(chat_id, f"⚠️ **Core Process Layer Notice:** Subprocess context dropped. \nReason: `{runtime_fault}`")
    finally:
        active_runtimes.pop(user_id, None)

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 9: PRIMARY INTERACTIVE DISPATCHER CHANNELS & INTERFACE BUTTONS
# ──────────────────────────────────────────────────────────────────────────────
@bot.message_handler(commands=['start', 'menu'])
def display_dashboard_interface(message):
    user_id = message.from_user.id
    
    # Adaptive master menu buttons configuration
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🚀 Launch Core Deployment Instance"),
        types.KeyboardButton("🎭 Modify Active Custom Profile Presets"),
        types.KeyboardButton("⚡ Real-time Telemetry Metrics"),
        types.KeyboardButton("🛑 Terminate Container Workers")
    )
    
    welcome_text = (
        f"👑 **Telegram Userbot Hosting Architecture Matrix**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ Hello, {message.from_user.first_name}.\n"
        f"Welcome to the master cluster execution framework.\n\n"
        f"» Master Core Version: `v4.2.1-Stable` \n"
        f"» Node Environment Target Status: `ACTIVE` \n\n"
        f"Select a command button to begin processing container actions:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda msg: msg.text == "🚀 Launch Core Deployment Instance")
@bot.message_handler(commands=['host'])
def request_host_deployment_handler(message):
    start_onboarding_sequence(message.chat.id, message.from_user.id)

@bot.message_handler(func=lambda msg: msg.text == "🎭 Modify Active Custom Profile Presets")
def request_preset_modification_handler(message):
    display_gender_selection_interface(message.chat.id, message.from_user.id)

@bot.message_handler(func=lambda msg: msg.text == "⚡ Real-time Telemetry Metrics")
@bot.message_handler(commands=['speed', 'telemetry'])
def display_telemetry_metrics_handler(message):
    start_timer = time.time()
    telemetry_notice = bot.reply_to(message, "`📡 Gathering network engine architecture profiles...`", parse_mode='Markdown')
    execution_lag_ms = round((time.time() - start_timer) * 1000, 2)
    
    total_active_containers = len(active_runtimes)
    system_memory_usage_pct = psutil.virtual_memory().percent
    cpu_utilization_pct = psutil.cpu_percent()
    
    metrics_display_payload = (
        f"📊 **System Telemetry Matrix Data Reports**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏱️ **Master API Dispatch Latency:** `{execution_lag_ms} ms` \n"
        f"🟢 **Hosted Cluster Count:** `{total_active_containers} Instances Running` \n"
        f"🧠 **Host RAM Allocation:** `{system_memory_usage_pct}%` \n"
        f"⚙️ **Global Host CPU Footprint:** `{cpu_utilization_pct}%` \n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Status: `HYPERVISOR COMPLIANT`"
    )
    bot.edit_message_text(metrics_display_payload, message.chat.id, telemetry_notice.message_id, parse_mode='Markdown')

@bot.message_handler(func=lambda msg: msg.text == "🛑 Terminate Container Workers")
@bot.message_handler(commands=['stop'])
def process_runtime_termination(message):
    user_id = message.from_user.id
    if user_id not in active_runtimes:
        bot.reply_to(message, "❌ **Deployment Management Fault:** No container runtimes detected running for your identity.")
        return
        
    container_payload = active_runtimes[user_id]
    client_instance = container_payload['client']
    async_loop = container_payload['loop']
    
    async_loop.create_task(client_instance.disconnect())
    bot.reply_to(message, "🛑 **Container execution terminated.** Asynchronous threads re-pooled successfully.")

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 10: AUTOMATED SHUTDOWN Handoff MATRIX
# ──────────────────────────────────────────────────────────────────────────────
def safe_shutdown_orchestrator():
    logger.warning("Hypervisor signaling interruption context. Safely halting active containers...")
    for user_id, elements in list(active_runtimes.items()):
        try:
            loop = elements['loop']
            client = elements['client']
            loop.run_until_complete(client.disconnect())
            logger.info(f"Successfully closed container connection context: {user_id}")
        except Exception as close_fault:
            logger.error(f"Error encountered during automated worker disposal sequence: {close_fault}")

atexit.register(safe_shutdown_orchestrator)

# ──────────────────────────────────────────────────────────────────────────────
# SECTION 11: ENGINE KERNEL RUNTIME LAUNCHPAD
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    logger.info("Initializing system thread pool frameworks...")
    
    # Spin up background web architecture layers
    web_worker_thread = Thread(target=initialize_keepalive_server, daemon=True)
    web_worker_thread.start()
    
    logger.info("Entering messaging interface pooling architecture...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as infrastructure_fault:
            logger.critical(f"Master Polling Loop Collapsed: {infrastructure_fault}. Re-pooling connections in 5 seconds...")
            time.sleep(5)
