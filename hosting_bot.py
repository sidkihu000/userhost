# ════════════════════════════════════════════════════════════════
#   HOSTER BOT CODE (MERGED WITH SID MASTER & FLOW BOT ENGINE)
# ════════════════════════════════════════════════════════════════

import asyncio
import logging
import os
import time
import shutil
import random
import json
import threading
from io import BytesIO
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.constants import ParseMode
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import (
    SessionPasswordNeededError, PhoneCodeExpiredError,
    PhoneCodeInvalidError, FloodWaitError
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

START_TIME = time.time()

# ─── BOT CONFIGURATION ────────────────────────────────────────────────────────
BOT_TOKEN = "8883135152:AAGexieuRsioA9aXGau3dT823hw7Mw0M-qc"
OWNER_ID = 8115054010
TELEGRAM_API_ID = 38843772
TELEGRAM_API_HASH = "875fbb273801c8025d05e98173fca536"
SUPPORT_USERNAME = "@YourSupport"
MAX_ACCOUNTS_PER_USER = 3
MAX_USERBOTS = 50

# ─── CONVERSATION STATES ──────────────────────────────────────────────────────
ASK_PHONE, ASK_CODE, ASK_2FA = range(3)
pending_logins: dict = {}

# ════════════════════════════════════════════════════════════════════════════════
#   SID MASTER: RAID ARRAYS & ANIMATION TEXTS
# ════════════════════════════════════════════════════════════════════════════════

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
    "Teri ma bhooki randy", "Chal na gawar", "Hakla kyun rha tu😂", "𝒯𝑒𝑟𝑖 𝑀𝑎 𝐺𝑎𝑑ℎ𝑒 𝐾𝑎 𝐿𝑜𝑑𝑎 𝐿𝑒𝑡𝑖 𝒉𝑒𝒉𝑒😂",
    "Tᴇʀᴀ ʙᴀᴀᴘ SᴛᴀᴛɪᴏN Mᴀɪ ʟᴀɴɢᴅᴀ Cʜᴀʟᴛᴀ 😂", "𝘛𝘦𝘳𝘪 𝘉𝘦𝘩𝘦𝘯 𝘒...𝘒𝘩𝘶𝘭𝘦𝘦 𝘈𝘢𝘮 𝘗𝘦𝘭𝘶 𝘒𝘶𝘵ɪʏᴀ 𝘣𝘢𝘯𝘢𝘬𝘦 REBEL Bʜɪ TᴇRᴇ JᴀIsA KʀᴛA TʜA Usʜᴇ ʜɪᴊᴅᴀ ʙᴀɴᴀ ᴅɪʏᴀ😂",
    "Cʜᴜᴘ Bɪʜᴀʀɪ ʙᴀᴜɴᴇ😂", "𝑻𝒆𝒓𝒊 𝑴𝒂 𝑺𝒂𝒕𝒓𝒂𝒏𝒈𝒊 𝑹𝒂𝒏𝒅🩷🤍🩶🖤💜👌🏻", "Cʜᴜᴅᴋᴇ Pɢʟ Bᴀɴ Gʏᴀ ᴄʏᴀ 😂",
    "HɪᴊDᴏ Kᴇ RᴀJᴀ TᴜJʜᴇ MᴇRᴇ LᴀNᴅ Kɪ sᴀʟᴀᴍɪ 😂", "Zᴏᴏ Kᴇ GᴏRɪLᴀ Sᴇ Tᴇʀɪ Mᴀ CʜᴜDᴡAU Oʀ ʙᴀᴄᴄʜᴇ Kᴀ NᴀMᴇ ᴅᴜ LADCHT DAS",
    "GᴀO Kᴇ SᴀRᴘᴀNᴄH Nᴇ Tᴇʀɪ Mᴀ ᴄʜᴏᴅɪ😂", "Chup rndyk kone mein baith 😂😂😂",
    "Teri Maa Ke भोसड़े में Theater Kholke सैयारा चाला दूंगा 🔈🔈🔥🔥🔥🔥😂😂😂🔈🔈🔈",
    "_✍🏻 𝐘ᴇ 𝐃ᴇ𝐊ʜ ˢᶜʳⁱᵖᵗ ˡⁱᵏʰ ʳᵃʰᵃ ʰᵘ 𝐓ᴇʀɪ 𝐌ᴀA 𝐊ᴇ 𝐁ʜ𝐎sᴅᴇ 𝐌ᴇIɴ 😂😂😂", "SᴜAʀ Tᴇʀɪ MᴀA Kɪ CʜUᴛ 😌😌💤💤",
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

HACK_ANIMATION = [
    "💻 `Initializing SID Exploit Script...`",
    "💻 `Connecting to Target's Local IP...`",
    "💻 `Bypassing Security Firewalls... [▓▓░░░░]`",
    "💻 `Extracting Database... [▓▓▓▓▓░]`",
    "💻 `Decrypting Mainframe... [▓▓▓▓▓▓]`",
    "👑 **HACK COMPLETE!**\n» System Compromised. Target Destroyed. 😈"
]
LOAD_BAR_FRAMES = ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]
EXPLODE_ANIMATION = ["💣 `3...`", "💣 `2...`", "💣 `1...`", "💥 **BOOOOOOOOM** 💥"]
HEART_ANIMATION = ["🤍", "🩷", "💖", "💗", "💓", "💞", "💕"]

SID_MASTER_MENU = """
===================================
       👑 **SID MASTER MENU** 👑
===================================
🔥 **RAID COMMANDS**
• `.attack` / `.sattack` (Stop)
• `.roast` / `.sroast`
• `.rebel` / `.srebel`
• `.sid` / `.ssid`
• `.homies` / `.shomies`

🚀 **POWER SPAM COMMANDS**
• `.spam <count> <text>`
• `.mixspam <count>`

✨ **ANIMATIONS & EFFECTS**
• `.hack` (Terminal Hack)
• `.load` (Progress Bar)
• `.magic` (Text Reveal)
• `.heart` (Love Burst)
• `.matrix` (Binary Code)
• `.explode` (Bomb Effect)

🛠 **UTILITIES & MODERATION**
• `.ping` / `.alive` / `.sid`
• `.menu` / `.help`
• `.mute` / `.unmute` (Reply or @username)
• `.purge <count>` (Reply to start)

🌊 **FLOW BOT COMMANDS**
• `.swipe <text>`
• `.stopswipe`
• `.flowdelay <seconds>`
• `.flowcount <n>`

===================================
 Powered by SID Core v6.0-DYNAMIC
==================================="""

SID_FLOW_BOT_MENU = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      💖  SID BEBO FLOW BOT  💖
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🌊 High‑speed flow engine.
  Use `.swipe` to start a swipe flood.

【 🌊 𝗙𝗟𝗢𝗪 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 】
  ✦ .swipe <text>           → swipe with custom text
  ✦ .swipe                  → swipe using default texts
  ✦ .stopswipe              → stop swipe flood

【 🚀 𝗙𝗟𝗢𝗪 𝗦𝗣𝗘𝗘𝗗 】
  ✦ .flowdelay <seconds>    → set delay between messages
  ✦ .flowcount <n>          → set number of messages per swipe

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       💖  SID BEBO — 𝗙𝗹𝗼𝘄 𝘄𝗶𝘁𝗵 𝗣𝗼𝘄𝗲𝗿
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ════════════════════════════════════════════════════════════════════════════════
#   USERBOT ENGINE REGISTRATION
# ════════════════════════════════════════════════════════════════════════════════
def register_userbot_engine(client: TelegramClient, user_id: int):
    U_STATE = {
        'start_time': time.time(),
        'active_raids': {},
        'flow_delay': 0.2,
        'flow_count': 30,
        'swipe_task': None,
        'muted_users': set()
    }

    def is_authorized(event):
        return event.out or event.sender_id == user_id

    async def _safe_edit(event, text):
        if event.out:
            try:
                return await event.edit(text, parse_mode='md')
            except Exception:
                try:
                    return await event.edit(text)
                except Exception:
                    return await event.reply(text)
        else:
            return await event.reply(text)

    async def get_target(event, arg=""):
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            return reply_msg.sender_id
        if arg:
            try:
                entity = await client.get_entity(arg)
                return entity.id
            except Exception:
                pass
        return None

    # ── Status & Utilities ──
    @client.on(events.NewMessage(pattern=r"^[/.](?:alive|sid)$"))
    async def ub_alive(event):
        if not is_authorized(event): return
        up = int(time.time() - U_STATE['start_time'])
        h, r = divmod(up, 3600); m, s = divmod(r, 60)
        txt = (
            f"👑 **SID PREMIUM USERBOT ENGINE** 👑\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"» **Status:** `ONLINE & DOMINATING` 🔥\n"
            f"» **Version:** `v6.0-SID-DYNAMIC`\n"
            f"» **Uptime:** `{h}h {m}m {s}s`\n"
            f"» **Owner ID:** `{user_id}`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ *Send .menu to view full command list!*"
        )
        await _safe_edit(event, txt)

    @client.on(events.NewMessage(pattern=r"^[/.](?:ping)$"))
    async def ub_ping(event):
        if not is_authorized(event): return
        start_t = time.time()
        await _safe_edit(event, "⚡ `Pinging...`")
        latency = round((time.time() - start_t) * 1000, 2)
        await _safe_edit(event, f"😈 **SID SPEED:** `{latency} ms` ⚡")

    @client.on(events.NewMessage(pattern=r"^[/.](?:menu|sid_menu|help|commands)$"))
    async def ub_menu(event):
        if not is_authorized(event): return
        await _safe_edit(event, SID_MASTER_MENU)

    @client.on(events.NewMessage(pattern=r"^[/.](?:flowmenu)$"))
    async def ub_flowmenu(event):
        if not is_authorized(event): return
        await _safe_edit(event, SID_FLOW_BOT_MENU)

    # ── Mute & Purge Commands ──
    @client.on(events.NewMessage(pattern=r"^[/.](?:mute)(?:\s+(.*))?$"))
    async def ub_mute(event):
        if not is_authorized(event): return
        arg = event.pattern_match.group(1) or ""
        tgt = await get_target(event, arg.strip())
        if not tgt:
            return await _safe_edit(event, "❌ Reply to a user or provide @username to mute.")
        U_STATE['muted_users'].add(tgt)
        await _safe_edit(event, f"🤫 **User Muted!** ID: `{tgt}`\n🗑️ *Their incoming messages will be auto-deleted.*")

    @client.on(events.NewMessage(pattern=r"^[/.](?:unmute)(?:\s+(.*))?$"))
    async def ub_unmute(event):
        if not is_authorized(event): return
        arg = event.pattern_match.group(1) or ""
        tgt = await get_target(event, arg.strip())
        if not tgt:
            return await _safe_edit(event, "❌ Reply to a user or provide @username to unmute.")
        if tgt in U_STATE['muted_users']:
            U_STATE['muted_users'].remove(tgt)
            await _safe_edit(event, f"🔊 **User Unmuted!** ID: `{tgt}`")
        else:
            await _safe_edit(event, f"⚠️ User `{tgt}` is not muted.")

    @client.on(events.NewMessage(pattern=r"^[/.](?:purge)(?:\s+(\d+))?$"))
    async def ub_purge(event):
        if not is_authorized(event): return
        limit = event.pattern_match.group(1)
        chat = await event.get_input_chat()
        
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            msgs = []
            async for m in client.iter_messages(chat, min_id=reply_msg.id - 1):
                msgs.append(m.id)
            if msgs:
                for i in range(0, len(msgs), 100):
                    await client.delete_messages(chat, msgs[i:i+100])
                msg = await client.send_message(chat, f"🗑️ **Purged {len(msgs)} messages!**")
                await asyncio.sleep(2)
                await msg.delete()
        elif limit:
            limit = int(limit)
            msgs = []
            async for m in client.iter_messages(chat, limit=limit + 1):
                msgs.append(m.id)
            if msgs:
                for i in range(0, len(msgs), 100):
                    await client.delete_messages(chat, msgs[i:i+100])
                msg = await client.send_message(chat, f"🗑️ **Purged {len(msgs)-1} messages!**")
                await asyncio.sleep(2)
                await msg.delete()
        else:
            await _safe_edit(event, "❌ Reply to a message to purge from there, or use `.purge <count>`")

    @client.on(events.NewMessage())
    async def ub_mute_handler(event):
        # NOTE: This runs for EVERY incoming/outgoing message.
        # If the sender is in muted_users, we delete it instantly.
        # This will work on any ID including OWNER_ID if muted.
        if event.sender_id in U_STATE['muted_users']:
            try:
                await event.delete()
            except Exception:
                pass

    # ── Raid Commands ──
    def register_raid(cmd, text_array):
        @client.on(events.NewMessage(pattern=rf"^[/.]{cmd}(?:\s+(.*))?$"))
        async def start_raid(event):
            if not is_authorized(event): return
            arg = event.pattern_match.group(1) or ""
            tgt = await get_target(event, arg.strip())
            if not tgt:
                return await _safe_edit(event, "❌ Reply to a user or mention @username.")
            if cmd not in U_STATE['active_raids']:
                U_STATE['active_raids'][cmd] = set()
            U_STATE['active_raids'][cmd].add(tgt)
            await _safe_edit(event, f"🔥 **{cmd.upper()} RAID ON** → `{tgt}`")

        @client.on(events.NewMessage(pattern=rf"^[/.](?:s{cmd}|stop{cmd})$"))
        async def stop_raid(event):
            if not is_authorized(event): return
            if cmd in U_STATE['active_raids']:
                U_STATE['active_raids'][cmd].clear()
            await _safe_edit(event, f"🛑 **{cmd.upper()} RAID OFF**")

    register_raid("attack", ATTACK_LIST)
    register_raid("roast", ROAST_LIST)
    register_raid("diss", DISS_LIST)
    register_raid("war", WAR_LIST)
    register_raid("savage", SAVAGE_LIST)
    register_raid("rebel", DIPESH_MESSAGES)
    register_raid("sid", RAPIST_MESSAGES)
    register_raid("homies", HOMIES_MESSAGES)

    @client.on(events.NewMessage(incoming=True))
    async def raid_trigger(event):
        sender = event.sender_id
        if not sender: return
        array_map = {
            "attack": ATTACK_LIST, "roast": ROAST_LIST, "diss": DISS_LIST,
            "war": WAR_LIST, "savage": SAVAGE_LIST, "rebel": DIPESH_MESSAGES,
            "sid": RAPIST_MESSAGES, "homies": HOMIES_MESSAGES
        }
        for cmd, targets in U_STATE['active_raids'].items():
            if sender in targets:
                try:
                    await event.reply(random.choice(array_map[cmd]))
                    await asyncio.sleep(0.3)
                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds)
                except Exception:
                    pass

    # ── Spam Commands ──
    @client.on(events.NewMessage(pattern=r"^[/.](?:spam)\s+(\d+)\s+(.+)"))
    async def ub_spam(event):
        if not is_authorized(event): return
        count = int(event.pattern_match.group(1))
        text = event.pattern_match.group(2)
        if event.out:
            try: await event.delete()
            except Exception: pass
        for _ in range(count):
            try:
                await client.send_message(event.chat_id, text)
                await asyncio.sleep(0.15)
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            except Exception:
                break

    @client.on(events.NewMessage(pattern=r"^[/.](?:mixspam)\s+(\d+)"))
    async def ub_mixspam(event):
        if not is_authorized(event): return
        count = int(event.pattern_match.group(1))
        all_pool = RAPIST_MESSAGES + DIPESH_MESSAGES + HOMIES_MESSAGES + ATTACK_LIST
        if event.out:
            try: await event.delete()
            except Exception: pass
        for _ in range(count):
            try:
                await client.send_message(event.chat_id, random.choice(all_pool))
                await asyncio.sleep(0.2)
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            except Exception:
                break

    # ── Animations ──
    @client.on(events.NewMessage(pattern=r"^[/.](?:hack)$"))
    async def ub_hack(event):
        if not is_authorized(event): return
        for frame in HACK_ANIMATION:
            await _safe_edit(event, frame)
            await asyncio.sleep(0.8)

    @client.on(events.NewMessage(pattern=r"^[/.](?:load)$"))
    async def ub_load(event):
        if not is_authorized(event): return
        for i in range(1, 101, 20):
            frame = LOAD_BAR_FRAMES[(i // 20) % len(LOAD_BAR_FRAMES)]
            await _safe_edit(event, f"⏳ **Loading Matrix:** `{frame} {i}%`")
            await asyncio.sleep(0.4)
        await _safe_edit(event, "✅ **SID MATRIX FULLY LOADED!**")

    @client.on(events.NewMessage(pattern=r"^[/.](?:magic)$"))
    async def ub_magic(event):
        if not is_authorized(event): return
        phrase = "SID IS INCREDIBLE"
        for i in range(len(phrase)):
            await _safe_edit(event, f"🪄 `{phrase[:i+1]}`")
            await asyncio.sleep(0.2)
        await _safe_edit(event, f"✨ **{phrase}** ✨")

    @client.on(events.NewMessage(pattern=r"^[/.](?:heart)$"))
    async def ub_heart(event):
        if not is_authorized(event): return
        for h in HEART_ANIMATION:
            await _safe_edit(event, f"Generating love... {h}")
            await asyncio.sleep(0.4)
        await _safe_edit(event, "💖 **SID SENDS LOVE!** 💖")

    @client.on(events.NewMessage(pattern=r"^[/.](?:explode)$"))
    async def ub_explode(event):
        if not is_authorized(event): return
        for frame in EXPLODE_ANIMATION:
            await _safe_edit(event, frame)
            await asyncio.sleep(0.8)

    # ── Flow Bot (Swipe) Methods ──
    @client.on(events.NewMessage(pattern=r"^[/.](?:swipe)(?:\s+(.*))?$"))
    async def ub_swipe(event):
        if not is_authorized(event): return
        custom_txt = event.pattern_match.group(1)
        txt = custom_txt.strip() if custom_txt else random.choice(RAPIST_MESSAGES + DIPESH_MESSAGES + HOMIES_MESSAGES)
        
        if U_STATE['swipe_task'] and not U_STATE['swipe_task'].done():
            U_STATE['swipe_task'].cancel()
            
        async def _swipe_runner():
            for _ in range(U_STATE['flow_count']):
                try:
                    await client.send_message(event.chat_id, txt)
                    await asyncio.sleep(U_STATE['flow_delay'])
                except Exception:
                    break
                    
        U_STATE['swipe_task'] = asyncio.create_task(_swipe_runner())
        await _safe_edit(event, f"🌊 **Swipe Started!** {U_STATE['flow_count']} msgs ({U_STATE['flow_delay']}s delay). Use `.stopswipe` to stop.")

    @client.on(events.NewMessage(pattern=r"^[/.](?:stopswipe)$"))
    async def ub_stopswipe(event):
        if not is_authorized(event): return
        if U_STATE['swipe_task'] and not U_STATE['swipe_task'].done():
            U_STATE['swipe_task'].cancel()
            await _safe_edit(event, "🛑 **Swipe Stopped!**")
        else:
            await _safe_edit(event, "ℹ️ No active swipe.")

    @client.on(events.NewMessage(pattern=r"^[/.](?:flowdelay)\s+([0-9.]+)"))
    async def ub_flowdelay(event):
        if not is_authorized(event): return
        d = float(event.pattern_match.group(1))
        if d < 0.05: d = 0.05
        U_STATE['flow_delay'] = d
        await _safe_edit(event, f"⏱️ **Flow Delay set to:** `{d}s`")

    @client.on(events.NewMessage(pattern=r"^[/.](?:flowcount)\s+(\d+)"))
    async def ub_flowcount(event):
        if not is_authorized(event): return
        c = int(event.pattern_match.group(1))
        if c < 1: c = 1
        U_STATE['flow_count'] = c
        await _safe_edit(event, f"🔢 **Flow Count set to:** `{c}`")

# ════════════════════════════════════════════════════════════════════════════════
#   DATABASE MANAGER
# ════════════════════════════════════════════════════════════════════════════════
class DBManager:
    def __init__(self, filename="hosting_db.json"):
        self.filename = filename
        self.data = {
            "users": {}, 
            "accounts": {}, 
            "blocked": [],
            "sudo": [],
            "bot_settings": {"is_on": True},
            "welcome_video": None
        }
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    self.data = json.load(f)
            except Exception:
                pass

    def save(self):
        try:
            with open(self.filename, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def is_sudo(self, uid, owner_id):
        return uid == owner_id or uid in self.data.get("sudo", [])

    def is_blocked(self, uid):
        return uid in self.data.get("blocked", [])

    def user_exists(self, uid):
        return str(uid) in self.data.get("users", {})

    def save_user_meta(self, uid, meta):
        uid = str(uid)
        if uid not in self.data["users"]:
            self.data["users"][uid] = {}
        self.data["users"][uid].update(meta)
        self.save()

    def get_accounts(self, uid):
        uid = str(uid)
        accs = self.data["accounts"].get(uid, {})
        return list(accs.values())

    def get_account(self, uid, slot):
        uid = str(uid)
        return self.data["accounts"].get(uid, {}).get(str(slot))

    def add_account(self, uid, acc_dict):
        uid = str(uid)
        if uid not in self.data["accounts"]:
            self.data["accounts"][uid] = {}
        self.data["accounts"][uid][str(acc_dict["slot"])] = acc_dict
        self.save()

    def remove_account(self, uid, slot):
        uid = str(uid)
        if uid in self.data["accounts"] and str(slot) in self.data["accounts"][uid]:
            del self.data["accounts"][uid][str(slot)]
            self.save()

    def get_welcome_video(self):
        return self.data.get("welcome_video")

    def set_welcome_video(self, data):
        self.data["welcome_video"] = data
        self.save()

    def remove_welcome_video(self):
        self.data["welcome_video"] = None
        self.save()

    def get_random_anime_image(self):
        return None

    def hosted_count(self):
        return sum(len(accs) for accs in self.data["accounts"].values())

    def get_all_users(self):
        return list(self.data["users"].keys())

    def user_count(self):
        return len(self.data["users"])

    def get_blocked(self):
        return self.data.get("blocked", [])

    def block_user(self, uid):
        if uid not in self.data["blocked"]:
            self.data["blocked"].append(uid)
            self.save()

    def unblock_user(self, uid):
        if uid in self.data["blocked"]:
            self.data["blocked"].remove(uid)
            self.save()

    def get_sudo_users(self):
        return self.data.get("sudo", [])

    def add_sudo(self, uid):
        if uid not in self.data["sudo"]:
            self.data["sudo"].append(uid)
            self.save()

    def remove_sudo(self, uid):
        if uid in self.data["sudo"]:
            self.data["sudo"].remove(uid)
            self.save()

    def is_bot_on(self):
        return self.data.get("bot_settings", {}).get("is_on", True)

    def set_bot_settings(self, settings):
        if "bot_settings" not in self.data:
            self.data["bot_settings"] = {}
        self.data["bot_settings"].update(settings)
        self.save()

db = DBManager()

# ════════════════════════════════════════════════════════════════════════════════
#   RUNNER MANAGER
# ════════════════════════════════════════════════════════════════════════════════
active_runtimes = {}

def _run_telethon_client(uid, slot, api_id, api_hash, session_string):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        client = TelegramClient(StringSession(session_string), int(api_id), api_hash, loop=loop)
        register_userbot_engine(client, uid)
        
        loop.run_until_complete(client.connect())
        if not loop.run_until_complete(client.is_user_authorized()):
            logger.warning(f"Userbot {uid}:{slot} is not authorized.")
            return
            
        active_runtimes[(str(uid), str(slot))] = {
            "client": client,
            "loop": loop,
            "start_time": time.time()
        }
        logger.info(f"Userbot successfully started for user {uid} (slot {slot})")
        loop.run_until_complete(client.run_until_disconnected())
    except Exception as e:
        logger.error(f"Userbot thread error: {e}")
    finally:
        active_runtimes.pop((str(uid), str(slot)), None)

class RunnerManager:
    def is_running(self, uid, slot):
        return (str(uid), str(slot)) in active_runtimes

    def get_uptime(self, uid, slot):
        key = (str(uid), str(slot))
        if key in active_runtimes:
            e = int(time.time() - active_runtimes[key]["start_time"])
            h, r = divmod(e, 3600); m, s = divmod(r, 60)
            return f"{h}h {m}m {s}s"
        return "N/A"

    def running_count(self):
        return len(active_runtimes)

    def start_userbot(self, uid, slot, api_id, api_hash, session_string, uid_str):
        key = (str(uid), str(slot))
        if key in active_runtimes:
            return True
        try:
            t = threading.Thread(
                target=_run_telethon_client, 
                args=(uid, slot, api_id, api_hash, session_string), 
                daemon=True
            )
            t.start()
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Failed to start thread: {e}")
            return False

    def stop_userbot(self, uid, slot):
        key = (str(uid), str(slot))
        if key in active_runtimes:
            try:
                loop = active_runtimes[key]["loop"]
                client = active_runtimes[key]["client"]
                asyncio.run_coroutine_threadsafe(client.disconnect(), loop)
            except Exception:
                pass
        return True

    def restart_userbot(self, uid, slot, api_id, api_hash, session_string, uid_str):
        self.stop_userbot(uid, slot)
        time.sleep(1)
        return self.start_userbot(uid, slot, api_id, api_hash, session_string, uid_str)

    def stop_all_for_user(self, uid):
        slots_to_stop = [s for (u, s) in active_runtimes.keys() if u == str(uid)]
        for slot in slots_to_stop:
            self.stop_userbot(uid, slot)

runner = RunnerManager()

# ════════════════════════════════════════════════════════════════════════════════
#   FONT STYLES
# ════════════════════════════════════════════════════════════════════════════════

def bold_serif(t: str) -> str:
    result = ""
    for c in t:
        if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D400)
        elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D41A)
        elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7CE)
        else: result += c
    return result

def italic_serif(t: str) -> str:
    special = {'h': '𝒽', 'e': '𝑒', 'i': '𝑖', 'j': '𝑗'}
    result = ""
    for c in t:
        if c in special: result += special[c]
        elif 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D434)
        elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D44E)
        else: result += c
    return result

def script(t: str) -> str:
    result = ""
    for c in t:
        if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D4D0)
        elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D4EA)
        else: result += c
    return result

def double_struck(t: str) -> str:
    special_map = {'C': 'ℂ', 'H': 'ℍ', 'N': 'ℕ', 'P': 'ℙ', 'Q': 'ℚ', 'R': 'ℝ', 'Z': 'ℤ'}
    result = ""
    for c in t:
        if c in special_map: result += special_map[c]
        elif 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D538)
        elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D552)
        elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7D8)
        else: result += c
    return result

def sans_bold(t: str) -> str:
    result = ""
    for c in t:
        if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D5D4)
        elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D5EE)
        elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7EC)
        else: result += c
    return result

def mono(t: str) -> str:
    result = ""
    for c in t:
        if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D670)
        elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D68A)
        elif '0' <= c <= '9': result += chr(ord(c) - ord('0') + 0x1D7F6)
        else: result += c
    return result

def fraktur(t: str) -> str:
    special = {'C': 'ℭ', 'H': 'ℌ', 'I': 'ℑ', 'R': 'ℜ', 'Z': 'ℨ'}
    result = ""
    for c in t:
        if c in special: result += special[c]
        elif 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D504)
        elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D51E)
        else: result += c
    return result

def bold_italic_serif(t: str) -> str:
    result = ""
    for c in t:
        if 'A' <= c <= 'Z': result += chr(ord(c) - ord('A') + 0x1D468)
        elif 'a' <= c <= 'z': result += chr(ord(c) - ord('a') + 0x1D482)
        else: result += c
    return result

DIV  = "━━━━━━━━━━━━━━━━━━━━━━━━━━"
DIV2 = "·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·͜·"
DIV3 = "⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯"
TOP  = "╔══════════════════════════╗"
BOT  = "╚══════════════════════════╝"
MID  = "╠══════════════════════════╣"

# ════════════════════════════════════════════════════════════════════════════════
#   HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def is_owner(uid): return uid == OWNER_ID
def is_premium(uid): return is_owner(uid) or db.is_sudo(uid, OWNER_ID)

def uptime_str():
    e = int(time.time() - START_TIME)
    h, r = divmod(e, 3600); m, s = divmod(r, 60)
    return f"{h}h {m}m {s}s"

def _phone_label(acct: dict) -> str:
    phone = acct.get("phone", "")
    return phone if phone else f"Account #{acct.get('slot', 0) + 1}"

async def owner_only(update: Update) -> bool:
    if not is_owner(update.effective_user.id):
        await update.message.reply_text(
            f"{TOP}\n║  🔒  {bold_serif('Access Denied')}  🔒  ║\n{BOT}\n\n"
            f"{script('This command is restricted to')}\n👑 {sans_bold('Owners Only')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return False
    return True

async def premium_only(update: Update) -> bool:
    if not is_premium(update.effective_user.id):
        await update.message.reply_text(
            f"🌟 {bold_serif('Premium Required')}\n\n"
            f"{script('This feature is for')}\n"
            f"👑 {sans_bold('Owners')} & {sans_bold('Premium Users')} {script('only')}\n\n"
            f"📩 {mono('Contact:')} {SUPPORT_USERNAME}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return False
    return True

async def check_blocked(update: Update) -> bool:
    if db.is_blocked(update.effective_user.id):
        await update.message.reply_text(
            f"🚫 {bold_serif('You have been Blocked')}\n\n"
            f"{script('Contact support to appeal.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return False
    return True

async def cleanup_pending(uid: int):
    data = pending_logins.pop(uid, None)
    if data and data.get("client"):
        try: await data["client"].disconnect()
        except: pass


# ════════════════════════════════════════════════════════════════════════════════
#   /start
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    uid  = update.effective_user.id
    name = update.effective_user.first_name or "User"

    if not db.user_exists(uid):
        db.save_user_meta(uid, {"first_name": name, "joined_at": int(time.time())})

    accounts = db.get_accounts(uid)
    hosted   = [a for a in accounts if a.get("hosted")]
    running  = [a for a in hosted if runner.is_running(uid, a["slot"])]

    if hosted:
        status_line = (
            f"\n📱 {fraktur('Accounts')} : {mono(str(len(hosted)))} hosted  "
            f"| {mono(str(len(running)))} running"
        )
    else:
        status_line = f"\n⚪ {fraktur('Userbot')}: {italic_serif('Not hosted yet')}"

    welcome_video = db.get_welcome_video()
    if welcome_video and welcome_video.get("file_id"):
        try:
            if welcome_video.get("is_video_note"):
                await context.bot.send_video_note(
                    chat_id=update.effective_chat.id,
                    video_note=welcome_video["file_id"],
                )
            else:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=welcome_video["file_id"],
                )
        except Exception as e:
            logger.warning(f"Failed to send welcome video: {e}")

    keyboard = [
        [
            InlineKeyboardButton("🚀  𝗛𝗼𝘀𝘁 𝗠𝘆 𝗨𝘀𝗲𝗿𝗯𝗼𝘁", callback_data="host"),
        ],
        [
            InlineKeyboardButton("📋  𝗠𝗮𝘀𝘁𝗲𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀", callback_data="commands"),
            InlineKeyboardButton("🌊  𝗙𝗹𝗼𝘄 𝗠𝗲𝗻𝘂",       callback_data="flow_menu"),
        ],
        [
            InlineKeyboardButton("📊  𝗦𝘁𝗮𝘁𝘂𝘀",   callback_data="status"),
            InlineKeyboardButton("🗑️  𝗟𝗼𝗴𝗼𝘂𝘁",   callback_data="menu_logout"),
        ],
        [
            InlineKeyboardButton("📞  𝗦𝘂𝗽𝗽𝗼𝗿𝘁",          callback_data="support"),
            InlineKeyboardButton("❓  𝗛𝗲𝗹𝗽 & 𝗚𝘂𝗶𝗱𝗲", callback_data="help"),
        ],
    ]
    if is_owner(uid):
        keyboard.append([
            InlineKeyboardButton("📢  𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁", callback_data="broadcast_menu"),
            InlineKeyboardButton("⚙️  𝗦𝗲𝘁𝘁𝗶𝗻𝗴𝘀",   callback_data="settings_menu"),
        ])

    text = (
        f"👑 **SID PREMIUM USERBOT ARCHITECTURE** 👑\n"
        f"{DIV}\n"
        f"✨ Welcome back, {bold_serif(name)}!\n\n"
        f"» **Engine:** `v6.0-SID-DYNAMIC`\n"
        f"» **Status:** `ONLINE & SECURE`\n\n"
        f"🪪 {fraktur('Your ID')} : `{uid}`\n"
        f"{status_line}\n\n"
        f"{italic_serif('Select an option below')} 👇"
    )

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# ════════════════════════════════════════════════════════════════════════════════
#   /setwelcomevideo (Owner)
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_setwelcomevideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    reply = update.message.reply_to_message
    if not reply:
        await update.message.reply_text(
            f"📽️ {bold_serif('Set Welcome Video')}\n\n"
            f"{script('Reply to a video or video note with')}\n"
            f"{mono('/setwelcomevideo')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    file_id = None
    is_video_note = False

    if reply.video:
        file_id = reply.video.file_id
    elif reply.video_note:
        file_id = reply.video_note.file_id
        is_video_note = True
    else:
        await update.message.reply_text(
            f"❌ {bold_serif('Reply must be a video or video note.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    db.set_welcome_video({"file_id": file_id, "is_video_note": is_video_note})
    await update.message.reply_text(
        f"✅ {bold_serif('Welcome video set successfully!')}\n\n"
        f"📹 {script('New users will see this video on /start')}",
        parse_mode=ParseMode.MARKDOWN,
    )

# ════════════════════════════════════════════════════════════════════════════════
#   /removewelcomevideo (Owner)
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_removewelcomevideo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    if db.get_welcome_video() is None:
        await update.message.reply_text(
            f"⚠️ {italic_serif('No welcome video is currently set.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    db.remove_welcome_video()
    await update.message.reply_text(
        f"🗑️ {bold_serif('Welcome video removed.')}\n\n"
        f"{script('The /start message will now show only text.')}",
        parse_mode=ParseMode.MARKDOWN,
    )

# ════════════════════════════════════════════════════════════════════════════════
#   /help
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    text = (
        f"❓ {double_struck('Help')} & {double_struck('Commands')}\n"
        f"{DIV}\n\n"
        f"{'━'*3} {sans_bold('User Commands')} {'━'*3}\n\n"
        f"🔹 {mono('/start')}       {script('Grand Welcome Screen')}\n"
        f"🔹 {mono('/help')}        {script('This Help Menu')}\n"
        f"🔹 {mono('/commands')}    {script('Master Features Menu')}\n"
        f"🔹 {mono('/flowmenu')}    {script('Flow Bot Features Menu')}\n"
        f"🔹 {mono('/host')}        {script('Add & Deploy Account')}\n"
        f"🔹 {mono('/myaccounts')}  {script('Manage All Accounts')}\n"
        f"🔹 {mono('/status')}      {script('Check All Userbots')}\n"
        f"🔹 {mono('/restart')}     {script('Restart Userbot')}\n"
        f"🔹 {mono('/logout')}      {script('Logout an Account')}\n"
        f"🔹 {mono('/support')}     {script('Contact Admin')}\n\n"
        f"{DIV}\n"
        f"{'━'*3} 👑 {sans_bold('Owner Commands')} {'━'*3}\n\n"
        f"🔺 {mono('/restartall')}    {fraktur('Restart All Userbots')}\n"
        f"🔺 {mono('/refresh')}       {fraktur('Refresh Bot State')}\n"
        f"🔺 {mono('/sudolist')}      {fraktur('Manage Sudo Users')}\n"
        f"🔺 {mono('/setdp')}         {fraktur('Set Display Photo')}\n"
        f"🔺 {mono('/block')}         {fraktur('Block a User')}\n"
        f"🔺 {mono('/unblock')}       {fraktur('Unblock a User')}\n"
        f"🔺 {mono('/blockeduser')}   {fraktur('View Blocked List')}\n"
        f"🔺 {mono('/stats')}         {fraktur('Bot Statistics')}\n"
        f"🔺 {mono('/secretfunction')} {fraktur('Secret Commands')}\n"
        f"🔺 {mono('/setwelcomevideo')} {fraktur('Set Welcome Video')}\n"
        f"🔺 {mono('/removewelcomevideo')} {fraktur('Remove Welcome Video')}\n"
        f"🔺 {mono('/setbot')}        {fraktur('ON/OFF Bot')}\n"
        f"{DIV}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# ════════════════════════════════════════════════════════════════════════════════
#   MENUS
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    await update.message.reply_text(SID_MASTER_MENU, parse_mode=ParseMode.MARKDOWN)

async def cmd_flowmenu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    await update.message.reply_text(SID_FLOW_BOT_MENU, parse_mode=ParseMode.MARKDOWN)

# ════════════════════════════════════════════════════════════════════════════════
#   /host — Phone + OTP Login Flow
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_host_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        reply = update.callback_query.message.reply_text
    else:
        reply = update.message.reply_text

    if not await check_blocked(update): return ConversationHandler.END
    uid = update.effective_user.id

    accounts = db.get_accounts(uid)
    hosted   = [a for a in accounts if a.get("hosted")]
    if len(hosted) >= MAX_ACCOUNTS_PER_USER:
        await reply(
            f"📱 {bold_serif('Account Limit Reached')}\n\n"
            f"{script('You already have')} {mono(str(len(hosted)))} {script('accounts hosted.')}\n"
            f"📌 {italic_serif('Maximum:')} {mono(str(MAX_ACCOUNTS_PER_USER))} {italic_serif('per user')}\n\n"
            f"🗑️ {script('Logout an account first:')} /logout",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

    total = db.hosted_count()
    if total >= MAX_USERBOTS and not is_premium(uid):
        await reply(
            f"😔 {sans_bold('Slots Full')} ({total}/{MAX_USERBOTS})\n\n"
            f"{script('Contact')} {SUPPORT_USERNAME} {script('to get a slot.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

    await cleanup_pending(uid)

    extra = f"\n\n📱 {italic_serif('Account')} {mono(str(len(hosted)+1))} {italic_serif('of')} {mono(str(MAX_ACCOUNTS_PER_USER))}" if hosted else ""

    await reply(
        f"{TOP}\n"
        f"║  🚀  {bold_serif('Deploy Your Userbot')}  🚀  ║\n"
        f"{BOT}\n\n"
        f"📱 {sans_bold('Step 1 of 3')}\n"
        f"{DIV3}\n"
        f"{script('Enter your Telegram Phone Number')}\n\n"
        f"🌍 {fraktur('Format')}: {mono('+91XXXXXXXXXX')}\n"
        f"_(country code ke saath)_{extra}\n\n"
        f"🔴 {italic_serif('Send /cancel to abort')}",
        parse_mode=ParseMode.MARKDOWN,
    )
    return ASK_PHONE

async def host_got_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    phone = update.message.text.strip()
    digits = phone.replace("+", "").replace(" ", "").replace("-", "")
    if not digits.isdigit() or len(digits) < 7:
        await update.message.reply_text(
            f"❌ {bold_serif('Invalid Number')}\n\n"
            f"{script('Please enter in format')}: {mono('+91XXXXXXXXXX')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ASK_PHONE

    msg = await update.message.reply_text(
        f"⏳ {sans_bold('Sending OTP to Telegram')}... 📨"
    )
    try:
        client = TelegramClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH)
        await client.connect()
        result = await client.send_code_request(phone)
        pending_logins[uid] = {
            "client": client,
            "phone":  phone,
            "phone_code_hash": result.phone_code_hash,
        }
        await msg.edit_text(
            f"{TOP}\n"
            f"║  📨  {bold_serif('OTP Sent Successfully')}  📨  ║\n"
            f"{BOT}\n\n"
            f"📱 {fraktur('Number')}: {mono(phone)}\n\n"
            f"📩 {sans_bold('Step 2 of 3')}\n"
            f"{DIV3}\n"
            f"{script('Enter the Login Code from your Telegram app')}\n\n"
            f"💡 {italic_serif('Tip: Send with spaces to avoid auto-forward')}\n"
            f"    {mono('Example')}: {bold_serif('1 2 3 4 5')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ASK_CODE
    except FloodWaitError as e:
        await cleanup_pending(uid)
        await msg.edit_text(
            f"⏳ {sans_bold('Flood Wait!')} {mono(str(e.seconds) + 's')} baad try karo."
        )
        return ConversationHandler.END
    except Exception as e:
        await cleanup_pending(uid)
        await msg.edit_text(
            f"❌ {bold_serif('Error')}\n{mono(str(e)[:120])}\n\n{script('Try again:')} /host",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

async def host_got_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    code = update.message.text.strip().replace(" ", "")

    pending = pending_logins.get(uid)
    if not pending:
        await update.message.reply_text(
            f"❌ {sans_bold('Session expired. Try /host again.')}"
        )
        return ConversationHandler.END

    client: TelegramClient = pending["client"]
    phone: str = pending["phone"]
    hash_: str = pending["phone_code_hash"]

    msg = await update.message.reply_text(f"🔐 {sans_bold('Verifying OTP')}...")
    try:
        await client.sign_in(phone, code, phone_code_hash=hash_)
        session_string = client.session.save()
        await client.disconnect()
        pending_logins.pop(uid, None)
        await _deploy_userbot(update, context, uid, session_string, phone, msg)
        return ConversationHandler.END

    except SessionPasswordNeededError:
        await msg.edit_text(
            f"{TOP}\n║  🔒  {bold_serif('2FA Detected')}  🔒  ║\n{BOT}\n\n"
            f"🛡️ {sans_bold('Step 3 of 3')}\n{DIV3}\n"
            f"{script('Your account has Two-Step Verification')}\n\n"
            f"🔑 {fraktur('Enter your 2FA Password')}:",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ASK_2FA

    except PhoneCodeInvalidError:
        await msg.edit_text(
            f"❌ {bold_serif('Wrong Code!')} Dobara enter karo:\n\n"
            f"💡 {mono('Spaces ke saath')}: {bold_serif('1 2 3 4 5')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ASK_CODE

    except PhoneCodeExpiredError:
        await cleanup_pending(uid)
        await msg.edit_text(
            f"⏳ {sans_bold('Code Expired!')} Dobara /host karo.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

    except Exception as e:
        await cleanup_pending(uid)
        await msg.edit_text(
            f"❌ {bold_serif('Error')}\n{mono(str(e)[:120])}\n\nDobara /host karo.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

async def host_got_2fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid      = update.effective_user.id
    password = update.message.text.strip()
    pending  = pending_logins.get(uid)
    if not pending:
        await update.message.reply_text("❌ Session expire ho gayi. /host karo.")
        return ConversationHandler.END

    client: TelegramClient = pending["client"]
    phone: str = pending.get("phone", "")
    msg = await update.message.reply_text(f"🔐 {sans_bold('Verifying 2FA Password')}...")
    try:
        await client.sign_in(password=password)
        session_string = client.session.save()
        await client.disconnect()
        pending_logins.pop(uid, None)
        await _deploy_userbot(update, context, uid, session_string, phone, msg)
        return ConversationHandler.END
    except Exception as e:
        await cleanup_pending(uid)
        await msg.edit_text(
            f"❌ {bold_serif('Wrong 2FA Password')}\n"
            f"{mono(str(e)[:120])}\n\nDobara /host karo.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

async def _deploy_userbot(update, context, uid, session_string, phone, msg):
    name     = update.effective_user.first_name or "User"
    accounts = db.get_accounts(uid)
    existing = {a.get("slot") for a in accounts}
    slot = 0
    while slot in existing:
        slot += 1
    acc_num = slot + 1

    # ─── Terminal Animation ───
    frames = [
        "🟢 `[▱▱▱▱▱▱▱▱▱] Booting Sid Kernel...`",
        "🟡 `[▰▰▰▱▱▱▱▱▱] Injecting Modules...`",
        "🟠 `[▰▰▰▰▰▰▱▱▱] Bypassing Security...`",
        "🔴 `[▰▰▰▰▰▰▰▰▱] Establishing Uplink...`",
        f"✅ `[▰▰▰▰▰▰▰▰▰] Link Established for Slot #{acc_num}!`"
    ]
    for frame in frames:
        try:
            await msg.edit_text(frame, parse_mode=ParseMode.MARKDOWN)
            await asyncio.sleep(0.5)
        except Exception:
            pass

    ok = runner.start_userbot(
        uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH, session_string, str(uid),
    )
    
    if ok:
        db.save_user_meta(uid, {"first_name": name})
        db.add_account(uid, {
            "slot":           slot,
            "session_string": session_string,
            "hosted":         True,
            "hosted_at":      int(time.time()),
            "phone":          phone,
        })
        
        deploy_caption = (
            f"{TOP}\n"
            f"║  🎉  {bold_serif('Deploy Successful')}  🎉  ║\n"
            f"{BOT}\n\n"
            f"✅ {sans_bold('Account')} : {mono('#' + str(acc_num))}\n"
            f"📱 {sans_bold('Phone')}   : {mono(phone if phone else 'N/A')}\n"
            f"⚡ {sans_bold('Version')} : {mono('v6.0-SID-DYNAMIC')}\n"
            f"📦 {sans_bold('Commands')}: {mono('500+')}\n\n"
            f"{DIV}\n"
            f"🔹 {italic_serif('Kisi bhi chat mein')} {mono('.alive')} {italic_serif('bhejo')}\n"
            f"🔹 {italic_serif('Commands dekhne ke liye')} {mono('.menu')} {italic_serif('bhejo')}\n"
            f"🔹 /myaccounts {italic_serif('se sab accounts dekho')}\n"
            f"🔹 /host {italic_serif('se aur account add karo')}"
        )
        
        try:
            await msg.edit_text(
                deploy_caption,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception:
            await update.effective_chat.send_message(
                deploy_caption,
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        try:
            await msg.edit_text(
                f"❌ {bold_serif('Deploy Failed')}\n\n"
                f"{script('Possible reasons:')}\n"
                f"• {fraktur('Account banned by Telegram')}\n"
                f"• {fraktur('Server error')}\n\n"
                f"📩 {sans_bold('Support')}: {SUPPORT_USERNAME}",
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception:
            await update.effective_chat.send_message(
                "❌ Deploy Failed. Please try /host again.",
                parse_mode=ParseMode.MARKDOWN,
            )

async def host_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cleanup_pending(update.effective_user.id)
    await update.message.reply_text(
        f"🚫 {bold_serif('Login Cancelled')}\n\n"
        f"{script('Use /host to try again anytime.')}"
    )
    return ConversationHandler.END

# ════════════════════════════════════════════════════════════════════════════════
#   /broadcast (Owner)
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return

    reply = update.message.reply_to_message
    text_arg = " ".join(context.args).strip()

    if not reply and not text_arg:
        await update.message.reply_text(
            f"{TOP}\n"
            f"║  📢  {bold_serif('Broadcast Center')}  📢  ║\n"
            f"{BOT}\n\n"
            f"📝 {script('Reply to any message with')} {mono('/broadcast')}\n"
            f"or {script('use')} {mono('/broadcast your message here')}\n\n"
            f"✨ {italic_serif('Media, photos, videos and files are supported when replying.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    users = []
    for uid_str in db.get_all_users():
        try:
            target_uid = int(uid_str)
        except Exception:
            continue
        if target_uid == OWNER_ID or db.is_blocked(target_uid):
            continue
        users.append(target_uid)

    total = len(users)
    if total == 0:
        await update.message.reply_text(
            f"⚠️ {bold_serif('No eligible users found.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    progress = await update.message.reply_text(
        f"📢 {bold_serif('Broadcast Starting')}...\n"
        f"⏳ {script('Preparing')} • {mono(f'0/{total}')}",
        parse_mode=ParseMode.MARKDOWN,
    )

    sent = 0
    failed = 0
    for index, target_uid in enumerate(users, 1):
        try:
            if reply:
                await context.bot.copy_message(
                    chat_id=target_uid,
                    from_chat_id=update.effective_chat.id,
                    message_id=reply.message_id,
                )
            else:
                await context.bot.send_message(
                    chat_id=target_uid,
                    text=text_arg,
                )
            sent += 1
        except Exception as e:
            failed += 1
            logger.warning(f"Broadcast failed for {target_uid}: {str(e)[:100]}")

        if index == 1 or index % 10 == 0 or index == total:
            frames = ["📢", "📣", "🚀", "✨", "📡"]
            frame = frames[(index // 10) % len(frames)]
            try:
                await progress.edit_text(
                    f"{frame} {bold_serif('Broadcasting')}...\n"
                    f"⏳ {script('Progress')} • {mono(f'{index}/{total}')}\n"
                    f"✅ {mono(str(sent))}  ❌ {mono(str(failed))}",
                    parse_mode=ParseMode.MARKDOWN,
                )
            except Exception:
                pass

    await progress.edit_text(
        f"{TOP}\n"
        f"║  ✅  {bold_serif('Broadcast Complete')}  ✅  ║\n"
        f"{BOT}\n\n"
        f"📨 {sans_bold('Sent')}    : {mono(str(sent))}\n"
        f"❌ {sans_bold('Failed')}  : {mono(str(failed))}\n"
        f"👥 {sans_bold('Total')}   : {mono(str(total))}\n\n"
        f"{DIV}\n"
        f"✨ {italic_serif('Broadcast finished successfully.')}",
        parse_mode=ParseMode.MARKDOWN,
    )

# ════════════════════════════════════════════════════════════════════════════════
#   /myaccounts
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_myaccounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    uid      = update.effective_user.id
    accounts = db.get_accounts(uid)
    hosted   = [a for a in accounts if a.get("hosted")]

    if not hosted:
        keyboard = [[InlineKeyboardButton("🚀 Host My First Userbot", callback_data="host")]]
        await update.message.reply_text(
            f"📱 {bold_serif('No Accounts Hosted Yet')}\n\n"
            f"{script('Get started with /host')}\n"
            f"{italic_serif('Host up to')} {mono(str(MAX_ACCOUNTS_PER_USER))} {italic_serif('accounts!')}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    lines = []
    keyboard = []
    for acct in hosted:
        slot   = acct.get("slot", 0)
        alive  = runner.is_running(uid, slot)
        uptime = runner.get_uptime(uid, slot) if alive else None
        icon   = "🟢" if alive else "🔴"
        phone  = _phone_label(acct)
        up_str = f"  ⏱️ {uptime}" if uptime else ""
        lines.append(
            f"{icon} {bold_serif('Acc #' + str(slot+1))} — {mono(phone)}{up_str}"
        )
        row = []
        if alive:
            row.append(InlineKeyboardButton(f"🔄 Restart #{slot+1}", callback_data=f"restart_acc_{slot}"))
        else:
            row.append(InlineKeyboardButton(f"▶️ Start #{slot+1}",   callback_data=f"start_acc_{slot}"))
        row.append(InlineKeyboardButton(f"🗑️ Logout #{slot+1}", callback_data=f"logout_acc_{slot}"))
        keyboard.append(row)

    if len(hosted) < MAX_ACCOUNTS_PER_USER:
        keyboard.append([InlineKeyboardButton("➕ Add Another Account", callback_data="add_acc")])

    header = (
        f"{TOP}\n"
        f"║  📱  {double_struck('My Accounts')} ({len(hosted)}/{MAX_ACCOUNTS_PER_USER})  📱  ║\n"
        f"{BOT}\n\n"
    )
    body = "\n".join(lines)
    footer = f"\n\n{DIV}\n🔹 /host {italic_serif('— add account')}"

    await update.message.reply_text(
        header + body + footer,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# ════════════════════════════════════════════════════════════════════════════════
#   /status
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    uid      = update.effective_user.id
    accounts = db.get_accounts(uid)
    hosted   = [a for a in accounts if a.get("hosted")]

    if not hosted:
        await update.message.reply_text(
            f"❌ {bold_serif('No Userbot Found')}\n\n"
            f"{script('Deploy one using')} /host",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    import datetime
    lines = []
    for acct in hosted:
        slot     = acct.get("slot", 0)
        alive    = runner.is_running(uid, slot)
        uptime   = runner.get_uptime(uid, slot) if alive else "—"
        hosted_at = acct.get("hosted_at", 0)
        since = datetime.datetime.fromtimestamp(hosted_at).strftime("%d %b %Y  %H:%M") if hosted_at else "—"
        icon = "🟢" if alive else "🔴"
        phone = _phone_label(acct)
        lines.append(
            f"{icon} {sans_bold('Account #' + str(slot+1))} — {mono(phone)}\n"
            f"   ⏱️ {italic_serif('Uptime')} : {mono(uptime)}\n"
            f"   📅 {italic_serif('Hosted')} : {mono(since)}"
        )

    footer = ""
    if any(not runner.is_running(uid, a["slot"]) for a in hosted):
        footer = f"\n\n🔄 {italic_serif('Use /restart to revive stopped accounts.')}"

    await update.message.reply_text(
        f"{TOP}\n║  📊  {double_struck('Userbot Status')}  📊  ║\n{BOT}\n\n"
        + "\n\n".join(lines) +
        f"\n\n{DIV}"
        f"\n⚡ {sans_bold('Version')} : {mono('v6.0-SID-DYNAMIC')}"
        f"{footer}",
        parse_mode=ParseMode.MARKDOWN,
    )

# ════════════════════════════════════════════════════════════════════════════════
#   /restart
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    uid      = update.effective_user.id
    accounts = db.get_accounts(uid)
    hosted   = [a for a in accounts if a.get("hosted")]

    if not hosted:
        await update.message.reply_text(
            f"❌ {bold_serif('No Userbot Found.')} {script('Use /host first.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if len(hosted) == 1:
        acct = hosted[0]
        slot = acct["slot"]
        await _do_restart(update, uid, slot, acct)
        return

    keyboard = []
    for acct in hosted:
        slot  = acct["slot"]
        phone = _phone_label(acct)
        alive = runner.is_running(uid, slot)
        icon  = "🟢" if alive else "🔴"
        keyboard.append([
            InlineKeyboardButton(
                f"{icon} Restart #{slot+1} — {phone}",
                callback_data=f"restart_acc_{slot}",
            )
        ])
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")])

    await update.message.reply_text(
        f"🔄 {bold_serif('Which account to restart?')}\n\n"
        f"{script('Select below')} 👇",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def _do_restart(update_or_query, uid, slot, acct):
    is_cb = hasattr(update_or_query, "callback_query") and update_or_query.callback_query
    if is_cb:
        msg_obj = update_or_query.callback_query.message
        send = msg_obj.reply_text
    else:
        send = update_or_query.message.reply_text

    msg = await send(f"🔄 {sans_bold('Restarting Account')} #{slot+1}...")
    ok = runner.restart_userbot(
        uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
        acct.get("session_string", ""), str(uid),
    )
    if ok:
        await msg.edit_text(
            f"✅ {double_struck('Account #' + str(slot+1) + ' Restarted')}!\n\n"
            f"🟢 {sans_bold('Status')}: {script('Running')}\n"
            f"⚡ {italic_serif('Test with')} {mono('.alive')}",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await msg.edit_text(
            f"❌ {bold_serif('Restart Failed')}\n\n"
            f"📩 {script('Contact')} {SUPPORT_USERNAME}",
            parse_mode=ParseMode.MARKDOWN,
        )

# ════════════════════════════════════════════════════════════════════════════════
#   /logout
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    uid      = update.effective_user.id
    accounts = db.get_accounts(uid)
    hosted   = [a for a in accounts if a.get("hosted")]

    if not hosted:
        await update.message.reply_text(
            f"❌ {italic_serif('Koi active userbot nahi hai.')}"
        )
        return

    if len(hosted) == 1:
        acct = hosted[0]
        slot = acct["slot"]
        phone = _phone_label(acct)
        keyboard = [[
            InlineKeyboardButton("✅ Haan, Logout Karo", callback_data=f"confirm_logout_{slot}"),
            InlineKeyboardButton("❌ Cancel",            callback_data="cancel_action"),
        ]]
        await update.message.reply_text(
            f"⚠️ {bold_serif('Logout Confirmation')}\n\n"
            f"📱 {sans_bold('Account')} : {mono(phone)}\n\n"
            f"{script('Logout karne se session delete ho jayega.')}\n"
            f"{italic_serif('Dobara host karne ke liye /host karo.')}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    keyboard = []
    for acct in hosted:
        slot  = acct["slot"]
        phone = _phone_label(acct)
        alive = runner.is_running(uid, slot)
        icon  = "🟢" if alive else "🔴"
        keyboard.append([
            InlineKeyboardButton(
                f"{icon} Logout #{slot+1} — {phone}",
                callback_data=f"logout_acc_{slot}",
            )
        ])
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")])

    await update.message.reply_text(
        f"🗑️ {bold_serif('Kaunsa Account Logout Karna Hai?')}\n\n"
        f"{script('Select below')} 👇",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def _do_logout(uid, slot):
    runner.stop_userbot(uid, slot)
    db.remove_account(uid, slot)
    session_dir = f"data/sessions/{uid}/{slot}"
    shutil.rmtree(session_dir, ignore_errors=True)

# ════════════════════════════════════════════════════════════════════════════════
#   /support & Admin Controls
# ════════════════════════════════════════════════════════════════════════════════

async def cmd_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    await update.message.reply_text(
        f"{TOP}\n║  📞  {double_struck('Support Center')}  📞  ║\n{BOT}\n\n"
        f"👤 {sans_bold('Admin')}    : {SUPPORT_USERNAME}\n"
        f"⚡ {sans_bold('Response')} : {script('Fast')}\n\n"
        f"{DIV}\n"
        f"🔧 {bold_serif('Try these first:')}\n\n"
        f"🔹 /myaccounts — {italic_serif('Sab accounts dekho')}\n"
        f"🔹 /restart    — {italic_serif('Userbot restart karo')}\n"
        f"🔹 /status     — {italic_serif('Status check karo')}\n"
        f"🔹 /logout → /host — {italic_serif('Re-deploy karo')}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_supportraid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    if not await premium_only(update): return
    args   = context.args
    target = " ".join(args) if args else None
    if not target:
        await update.message.reply_text(
            f"⚔️ {bold_serif('Pro Support Raid')}\n\n"
            f"📌 {sans_bold('Usage')}: {mono('/supportraid @username')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    await update.message.reply_text(
        f"{TOP}\n║  ⚔️  {bold_serif('Support Raid Launched')}  ⚔️  ║\n{BOT}\n\n"
        f"🎯 {sans_bold('Target')} : {mono(target)}\n"
        f"🌪️ {script('All premium userbots activated!')}\n"
        f"⚡ {fraktur('Raid Mode')}: {double_struck('MAX POWER')}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_restartall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    msg   = await update.message.reply_text(f"🔄 {sans_bold('Restarting All Userbots')}...")
    count = 0
    for uid_str in db.get_all_users():
        uid = int(uid_str)
        if db.is_blocked(uid): continue
        for acct in db.get_accounts(uid):
            if not acct.get("hosted") or not acct.get("session_string"): continue
            slot = acct["slot"]
            ok = runner.restart_userbot(
                uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                acct["session_string"], uid_str,
            )
            if ok: count += 1
    await msg.edit_text(
        f"✅ {double_struck('Restart Complete')}\n\n"
        f"🟢 {sans_bold('Restarted')}: {mono(str(count))} {script('userbots')}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    await update.message.reply_text(
        f"🔁 {bold_serif('Bot State Refreshed')}\n\n"
        f"🟢 {sans_bold('Running')} : {mono(str(runner.running_count()))}\n"
        f"📦 {sans_bold('Total')}   : {mono(str(db.hosted_count()))}\n"
        f"🕒 {sans_bold('Uptime')}  : {mono(uptime_str())}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    args  = context.args
    sudos = db.get_sudo_users()

    if args and args[0] == "add" and len(args) > 1:
        try:
            db.add_sudo(int(args[1]))
            await update.message.reply_text(
                f"✅ {mono(args[1])} {script('added to Sudo Users.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
        except: await update.message.reply_text("❌ Invalid ID.")
        return

    if args and args[0] == "del" and len(args) > 1:
        try:
            db.remove_sudo(int(args[1]))
            await update.message.reply_text(
                f"✅ {mono(args[1])} {script('removed from Sudo Users.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
        except: await update.message.reply_text("❌ Invalid ID.")
        return

    if not sudos:
        await update.message.reply_text(
            f"📋 {bold_serif('No Sudo Users yet.')}\n\nAdd: {mono('/sudolist add <uid>')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    lines = "\n".join(f"  👑 {mono(str(u))}" for u in sudos)
    await update.message.reply_text(
        f"{TOP}\n║  👑  {double_struck('Sudo Users')} ({len(sudos)})  👑  ║\n{BOT}\n\n"
        f"{lines}\n\n{DIV}\n"
        f"➕ {mono('/sudolist add <uid>')}\n"
        f"➖ {mono('/sudolist del <uid>')}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_setdp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text(f"📸 {script('Kisi photo ko reply karo.')}")
        return
    photo = update.message.reply_to_message.photo[-1]
    file  = await context.bot.get_file(photo.file_id)
    data  = await file.download_as_bytearray()
    from io import BytesIO
    try:
        await context.bot.set_my_profile_photo(BytesIO(bytes(data)))
        await update.message.reply_text(f"✅ {bold_serif('Display Photo Updated')}!")
    except Exception as e:
        await update.message.reply_text(
            f"❌ {sans_bold('Failed')}: {mono(str(e)[:80])}",
            parse_mode=ParseMode.MARKDOWN,
        )

async def cmd_block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    if not context.args:
        await update.message.reply_text(
            f"📌 {sans_bold('Usage')}: {mono('/block <user_id>')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    try:
        target = int(context.args[0])
        if target == OWNER_ID:
            await update.message.reply_text(f"❌ {italic_serif('Owner ko block nahi kar sakte.')}")
            return
        db.block_user(target)
        runner.stop_all_for_user(target)
        await update.message.reply_text(
            f"🚫 {bold_serif('User Blocked')}\n\n"
            f"🆔 {mono(str(target))}\n"
            f"🔴 {script('All userbots stopped.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
    except ValueError:
        await update.message.reply_text("❌ Invalid ID.")

async def cmd_unblock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    if not context.args:
        await update.message.reply_text(
            f"📌 {sans_bold('Usage')}: {mono('/unblock <user_id>')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    try:
        db.unblock_user(int(context.args[0]))
        await update.message.reply_text(
            f"✅ {bold_serif('User Unblocked')}\n🆔 {mono(context.args[0])}",
            parse_mode=ParseMode.MARKDOWN,
        )
    except ValueError:
        await update.message.reply_text("❌ Invalid ID.")

async def cmd_blockeduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    blocked = db.get_blocked()
    if not blocked:
        await update.message.reply_text(f"✅ {script('No blocked users.')}")
        return
    lines = "\n".join(f"  🚫 {mono(str(u))}" for u in blocked)
    await update.message.reply_text(
        f"{TOP}\n║  🚫  {double_struck('Blocked Users')} ({len(blocked)})  🚫  ║\n{BOT}\n\n"
        f"{lines}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    total   = db.user_count()
    hosted  = db.hosted_count()
    running = runner.running_count()
    blocked = len(db.get_blocked())
    sudos   = len(db.get_sudo_users())

    await update.message.reply_text(
        f"{TOP}\n║  📊  {double_struck('Bot Statistics')}  📊  ║\n{BOT}\n\n"
        f"👥 {sans_bold('Total Users')}    : {double_struck(str(total))}\n"
        f"🚀 {sans_bold('Hosted Accounts')}: {double_struck(str(hosted))}\n"
        f"🟢 {sans_bold('Running')}        : {double_struck(str(running))}\n"
        f"🔴 {sans_bold('Stopped')}        : {double_struck(str(hosted - running))}\n"
        f"🚫 {sans_bold('Blocked')}        : {double_struck(str(blocked))}\n"
        f"👑 {sans_bold('Sudo Users')}     : {double_struck(str(sudos))}\n"
        f"📦 {sans_bold('Max Slots')}      : {double_struck(str(MAX_USERBOTS))}\n"
        f"{DIV}\n"
        f"🕒 {sans_bold('Bot Uptime')} : {mono(uptime_str())}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_secretfunction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    await update.message.reply_text(
        f"{TOP}\n║  🔐  {bold_serif('Secret Commands')}  🔐  ║\n{BOT}\n\n"
        f"🔺 {mono('/sudolist add <uid>')}  — {fraktur('Add Premium User')}\n"
        f"🔺 {mono('/sudolist del <uid>')}  — {fraktur('Remove Premium User')}\n"
        f"🔺 {mono('/block <uid>')}         — {fraktur('Ban & Kill All Userbots')}\n"
        f"🔺 {mono('/unblock <uid>')}       — {fraktur('Unban User')}\n"
        f"🔺 {mono('/restartall')}          — {fraktur('Restart All Userbots')}\n"
        f"🔺 {mono('/refresh')}             — {fraktur('Refresh Bot State')}\n"
        f"🔺 {mono('/stats')}               — {fraktur('Full Statistics')}\n"
        f"🔺 {mono('/setdp')}               — {fraktur('Set Display Photo')}\n"
        f"🔺 {mono('/blockeduser')}         — {fraktur('View Blocked List')}\n"
        f"🔺 {mono('/secretfunction')}      — {fraktur('This Menu')}\n"
        f"🔺 {mono('/setwelcomevideo')}     — {fraktur('Set Welcome Video')}\n"
        f"🔺 {mono('/removewelcomevideo')}  — {fraktur('Remove Welcome Video')}\n"
        f"🔺 {mono('/setbot')}              — {fraktur('ON/OFF Bot')}",
        parse_mode=ParseMode.MARKDOWN,
    )

async def cmd_setbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await owner_only(update): return
    args = context.args
    if not args or args[0].lower() not in ["on", "off"]:
        current = "ON" if db.is_bot_on() else "OFF"
        await update.message.reply_text(
            f"⚙️ {bold_serif('Bot Status')}\n\n"
            f"📊 {sans_bold('Current')} : {mono(current)}\n\n"
            f"📌 {sans_bold('Usage')}: {mono('/setbot on/off')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    new_state = args[0].lower() == "on"
    db.set_bot_settings({"is_on": new_state})
    status = "ON 🟢" if new_state else "OFF 🔴"
    await update.message.reply_text(
        f"✅ {bold_serif('Bot Status Updated')}\n\n"
        f"📊 {sans_bold('Status')} : {mono(status)}",
        parse_mode=ParseMode.MARKDOWN,
    )

# ════════════════════════════════════════════════════════════════════════════════
#   CALLBACK QUERY HANDLER
# ════════════════════════════════════════════════════════════════════════════════

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not db.is_bot_on():
        await update.callback_query.answer("⚠️ Bot is currently OFF", show_alert=True)
        return

    query = update.callback_query
    await query.answer()
    uid  = update.effective_user.id
    data = query.data

    if data == "cancel_action":
        await query.message.edit_text(f"🚫 {italic_serif('Cancelled.')}")
        return

    if data == "broadcast_menu":
        if not is_owner(uid):
            await query.answer("🔒 Owner only", show_alert=True)
            return
        await query.message.reply_text(
            f"{TOP}\n"
            f"║  📢  {bold_serif('Broadcast Center')}  📢  ║\n"
            f"{BOT}\n\n"
            f"📝 {script('Reply to any message with')} {mono('/broadcast')}\n"
            f"or use {mono('/broadcast your message')}\n\n"
            f"✨ {italic_serif('Button animation + live progress is enabled.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data == "settings_menu":
        if not is_owner(uid):
            await query.answer("🔒 Owner only", show_alert=True)
            return
        current_status = "ON 🟢" if db.is_bot_on() else "OFF 🔴"
        keyboard = [
            [InlineKeyboardButton(f"🟢 Bot is {current_status}", callback_data="toggle_bot")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")],
        ]
        await query.message.reply_text(
            f"{TOP}\n"
            f"║  ⚙️  {bold_serif('Bot Settings')}  ⚙️  ║\n"
            f"{BOT}\n\n"
            f"📊 {sans_bold('Bot Status')} : {mono(current_status)}\n"
            f"🆔 {sans_bold('Owner ID')}  : `{OWNER_ID}`\n"
            f"🔑 {sans_bold('API ID')}    : `{TELEGRAM_API_ID}`\n"
            f"🔐 {sans_bold('API Hash')}  : `{TELEGRAM_API_HASH[:8]}...`\n\n"
            f"{DIV}\n"
            f"💡 {italic_serif('Toggle bot status below')}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if data == "toggle_bot":
        if not is_owner(uid):
            await query.answer("🔒 Owner only", show_alert=True)
            return
        current = db.is_bot_on()
        db.set_bot_settings({"is_on": not current})
        new_status = "ON 🟢" if not current else "OFF 🔴"
        await query.message.edit_text(
            f"✅ {bold_serif('Bot Status Updated')}\n\n"
            f"📊 {sans_bold('Status')} : {mono(new_status)}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data == "back_to_start":
        await cmd_start(update, context)
        return

    if data == "commands":
        await query.message.reply_text(SID_MASTER_MENU, parse_mode=ParseMode.MARKDOWN)
        return

    if data == "flow_menu":
        await query.message.reply_text(SID_FLOW_BOT_MENU, parse_mode=ParseMode.MARKDOWN)
        return

    if data == "status":
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]
        if not hosted:
            await query.message.reply_text(
                f"❌ {bold_serif('No Userbot Hosted')}\n\n"
                f"{script('Use /host to deploy your first account.')}",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        import datetime
        lines = []
        for acct in hosted:
            slot     = acct.get("slot", 0)
            alive    = runner.is_running(uid, slot)
            uptime   = runner.get_uptime(uid, slot) if alive else "—"
            hosted_at = acct.get("hosted_at", 0)
            since = datetime.datetime.fromtimestamp(hosted_at).strftime("%d %b %Y") if hosted_at else "—"
            icon  = "🟢" if alive else "🔴"
            phone = _phone_label(acct)
            lines.append(
                f"{icon} {sans_bold('Acc #' + str(slot+1))} — {mono(phone)}\n"
                f"   ⏱️ {uptime}   📅 {since}"
            )
        footer = ""
        if any(not runner.is_running(uid, a["slot"]) for a in hosted):
            footer = f"\n\n🔄 {italic_serif('/restart se revive karo.')}"
        await query.message.reply_text(
            f"{TOP}\n║  📊  {double_struck('Userbot Status')}  📊  ║\n{BOT}\n\n"
            + "\n\n".join(lines) +
            f"\n\n{DIV}"
            f"\n⚡ {sans_bold('Version')} : {mono('v6.0-SID-DYNAMIC')}"
            f"{footer}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data == "menu_logout":
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]
        if not hosted:
            await query.message.reply_text(
                f"❌ {italic_serif('Koi active userbot nahi hai.')}"
            )
            return
        if len(hosted) == 1:
            acct  = hosted[0]
            slot  = acct["slot"]
            phone = _phone_label(acct)
            kb = [[
                InlineKeyboardButton("✅ Haan, Logout Karo", callback_data=f"confirm_logout_{slot}"),
                InlineKeyboardButton("❌ Cancel",            callback_data="cancel_action"),
            ]]
            await query.message.reply_text(
                f"⚠️ {bold_serif('Logout Confirmation')}\n\n"
                f"📱 {sans_bold('Account')} : {mono(phone)}\n\n"
                f"{script('Session delete ho jayega.')}\n"
                f"{italic_serif('Dobara /host se add kar sakte ho.')}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(kb),
            )
        else:
            kb = []
            for acct in hosted:
                slot  = acct["slot"]
                phone = _phone_label(acct)
                alive = runner.is_running(uid, slot)
                icon  = "🟢" if alive else "🔴"
                kb.append([InlineKeyboardButton(
                    f"{icon} Logout #{slot+1} — {phone}",
                    callback_data=f"logout_acc_{slot}",
                )])
            kb.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")])
            await query.message.reply_text(
                f"🗑️ {bold_serif('Kaunsa Account Logout Karna Hai?')}\n\n"
                f"{script('Select below')} 👇",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(kb),
            )
        return

    if data == "support":
        await query.message.reply_text(
            f"{TOP}\n║  📞  {double_struck('Support Center')}  📞  ║\n{BOT}\n\n"
            f"👤 {sans_bold('Bot Owner')}  : {SUPPORT_USERNAME}\n"
            f"⚡ {sans_bold('Response')}   : {script('Fast')}\n\n"
            f"{DIV}\n"
            f"🔧 {bold_serif('Pehle Yeh Try Karo:')}\n\n"
            f"🔹 /myaccounts — {italic_serif('sab accounts dekho')}\n"
            f"🔹 /restart    — {italic_serif('userbot restart karo')}\n"
            f"🔹 /status     — {italic_serif('status check karo')}\n"
            f"🔹 /logout     — {italic_serif('aur dobara /host karo')}\n\n"
            f"{DIV}\n"
            f"🤖 {bold_serif('Bot Owner')}: {SUPPORT_USERNAME}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data == "help":
        await query.message.reply_text(
            f"╔══════════════════════════════╗\n"
            f"║  📖  {bold_serif('BOT USAGE GUIDE')}  📖  ║\n"
            f"╚══════════════════════════════╝\n\n"
            f"{'━'*30}\n"
            f"🚀 {sans_bold('STEP 1')} — {bold_serif('Bot Start Karo')}\n"
            f"{'━'*30}\n"
            f"➡️ {script('Is bot pe')} /start {script('bhejo')}\n"
            f"✅ {italic_serif('Welcome screen aayega')}\n\n"
            f"{'━'*30}\n"
            f"📱 {sans_bold('STEP 2')} — {bold_serif('Account Host Karo')}\n"
            f"{'━'*30}\n"
            f"➡️ {mono('Host My Userbot')} {script('button tap karo')}\n"
            f"➡️ {script('Apna phone number enter karo')}\n"
            f"    {mono('Format: +91XXXXXXXXXX')}\n"
            f"➡️ {script('Telegram se OTP aayega')}\n"
            f"    💡 {italic_serif('OTP spaces ke saath bhejo:')}\n"
            f"    {mono('1 2 3 4 5')} ← {italic_serif('aisa karo')}\n"
            f"➡️ {script('2FA hai toh password bhi daalo')}\n"
            f"✅ {italic_serif('Userbot deploy ho jayega!')}\n\n"
            f"{'━'*30}\n"
            f"⚡ {sans_bold('STEP 3')} — {bold_serif('Commands Chalao')}\n"
            f"{'━'*30}\n"
            f"➡️ {script('Kisi bhi chat mein jao')}\n"
            f"➡️ {script('Dot')} {mono('.')} {script('se command likho:')}\n\n"
            f"    {mono('.alive')}  → {script('Bot alive check karo')}\n"
            f"    {mono('.ping')}   → {script('Speed check')}\n"
            f"    {mono('.menu')}   → {script('Commands list')}\n"
            f"    {mono('.attack')} → {script('Attack karo')}\n"
            f"    {mono('.roast')}  → {script('Roast karo')}\n"
            f"    {mono('.swipe')}  → {script('Swipe flood shuru')}\n\n"
            f"{'━'*30}\n"
            f"🔄 {sans_bold('STEP 4')} — {bold_serif('Manage Karo')}\n"
            f"{'━'*30}\n"
            f"    /myaccounts — {script('Sab accounts')}\n"
            f"    /status     — {script('Status dekho')}\n"
            f"    /restart    — {script('Restart karo')}\n"
            f"    /logout     — {script('Logout karo')}\n"
            f"    /host       — {script('Naya account add karo')}\n\n"
            f"{'━'*30}\n"
            f"⚠️ {sans_bold('IMPORTANT')}\n"
            f"{'━'*30}\n"
            f"🔸 {italic_serif('Sirf tumhara OWN account command chalayega')}\n"
            f"🔸 {italic_serif('Kisi dusre ka message ignore hoga')}\n"
            f"🔸 {italic_serif('Max')} {mono('3')} {italic_serif('accounts ek saath host ho sakte hain')}\n\n"
            f"{'━'*30}\n"
            f"🌟 {bold_serif('Bot Owner')}: {SUPPORT_USERNAME}\n"
            f"⚡ {bold_serif('Powered by SIDxBOT')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data.startswith("restart_acc_"):
        try:
            slot = int(data.split("_")[-1])
        except ValueError:
            return
        acct = db.get_account(uid, slot)
        if not acct:
            await query.message.reply_text(f"❌ {italic_serif('Account not found.')}")
            return
        msg = await query.message.reply_text(
            f"🔄 {sans_bold('Restarting Account')} #{slot+1}..."
        )
        ok = runner.restart_userbot(
            uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
            acct.get("session_string", ""), str(uid),
        )
        if ok:
            await msg.edit_text(
                f"✅ {double_struck('Account #' + str(slot+1) + ' Restarted')}!\n\n"
                f"🟢 {sans_bold('Status')}: {script('Running')}\n"
                f"⚡ {italic_serif('Test with')} {mono('.alive')}",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await msg.edit_text(f"❌ {bold_serif('Restart Failed')}\n📩 {SUPPORT_USERNAME}")
        return

    if data.startswith("start_acc_"):
        try:
            slot = int(data.split("_")[-1])
        except ValueError:
            return
        acct = db.get_account(uid, slot)
        if not acct:
            await query.message.reply_text(f"❌ {italic_serif('Account not found.')}")
            return
        msg = await query.message.reply_text(
            f"▶️ {sans_bold('Starting Account')} #{slot+1}..."
        )
        ok = runner.start_userbot(
            uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
            acct.get("session_string", ""), str(uid),
        )
        if ok:
            await msg.edit_text(
                f"✅ {double_struck('Account #' + str(slot+1) + ' Started')}!\n\n"
                f"🟢 {sans_bold('Status')}: {script('Running')}\n"
                f"⚡ {italic_serif('Test with')} {mono('.alive')}",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await msg.edit_text(f"❌ {bold_serif('Start Failed')}\n📩 {SUPPORT_USERNAME}")
        return

    if data.startswith("logout_acc_"):
        try:
            slot = int(data.split("_")[-1])
        except ValueError:
            return
        acct  = db.get_account(uid, slot)
        if not acct:
            await query.message.reply_text(f"❌ {italic_serif('Account not found.')}")
            return
        phone = _phone_label(acct)
        keyboard = [[
            InlineKeyboardButton("✅ Haan, Logout Karo", callback_data=f"confirm_logout_{slot}"),
            InlineKeyboardButton("❌ Cancel",            callback_data="cancel_action"),
        ]]
        await query.message.reply_text(
            f"⚠️ {bold_serif('Logout Confirmation')}\n\n"
            f"📱 {sans_bold('Account')} #{slot+1} : {mono(phone)}\n\n"
            f"{script('Session delete ho jayega.')}\n"
            f"{italic_serif('Dobara /host se add kar sakte ho.')}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if data.startswith("confirm_logout_"):
        try:
            slot = int(data.split("_")[-1])
        except ValueError:
            return
        acct  = db.get_account(uid, slot)
        phone = _phone_label(acct) if acct else f"#{slot+1}"
        await _do_logout(uid, slot)
        await query.message.edit_text(
            f"{TOP}\n║  👋  {bold_serif('Logged Out')}  👋  ║\n{BOT}\n\n"
            f"📱 {sans_bold('Account')} : {mono(phone)}\n"
            f"🗑️ {sans_bold('Session')} : {script('Cleared')}\n\n"
            f"🚀 {fraktur('Re-deploy anytime:')} /host\n"
            f"📱 {fraktur('See accounts:')} /myaccounts",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if data == "add_acc":
        accounts = db.get_accounts(uid)
        hosted   = [a for a in accounts if a.get("hosted")]
        if len(hosted) >= MAX_ACCOUNTS_PER_USER:
            await query.message.reply_text(
                f"📱 {bold_serif('Account Limit Reached')}\n\n"
                f"{script('Maximum')} {mono(str(MAX_ACCOUNTS_PER_USER))} {script('accounts.')}\n"
                f"🗑️ {script('Logout one first:')} /logout",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        await query.message.reply_text(
            f"🚀 {bold_serif('Add New Account')}\n\n"
            f"{script('Send')} /host {script('to start the login flow.')}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

# ════════════════════════════════════════════════════════════════════════════════
#   AUTO HEALTH CHECK
# ════════════════════════════════════════════════════════════════════════════════

async def auto_health_check(context: ContextTypes.DEFAULT_TYPE):
    if not db.is_bot_on():
        return
    for uid_str in db.get_all_users():
        uid = int(uid_str)
        if db.is_blocked(uid): continue
        for acct in db.get_accounts(uid):
            if not acct.get("hosted") or not acct.get("session_string"): continue
            slot = acct["slot"]
            if not runner.is_running(uid, slot):
                runner.start_userbot(
                    uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                    acct["session_string"], uid_str,
                )

# ════════════════════════════════════════════════════════════════════════════════
#   STARTUP & MAIN
# ════════════════════════════════════════════════════════════════════════════════

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start",           "Grand Welcome"),
        BotCommand("help",            "All Commands"),
        BotCommand("commands",        "Master Features Menu"),
        BotCommand("flowmenu",        "Flow Bot Features Menu"),
        BotCommand("host",            "Add & Deploy Account"),
        BotCommand("myaccounts",      "Manage All Accounts"),
        BotCommand("status",          "Check Userbot Status"),
        BotCommand("restart",         "Restart Userbot"),
        BotCommand("logout",          "Logout an Account"),
        BotCommand("support",         "Get Support"),
        BotCommand("supportraid",     "Pro Raid (Premium)"),
        BotCommand("restartall",      "Restart All (Owner)"),
        BotCommand("refresh",         "Refresh State (Owner)"),
        BotCommand("sudolist",        "Sudo Users (Owner)"),
        BotCommand("setdp",           "Set Display Photo (Owner)"),
        BotCommand("block",           "Block User (Owner)"),
        BotCommand("unblock",         "Unblock User (Owner)"),
        BotCommand("blockeduser",     "Blocked List (Owner)"),
        BotCommand("stats",           "Bot Statistics (Owner)"),
        BotCommand("secretfunction",  "Secret Commands (Owner)"),
        BotCommand("setwelcomevideo", "Set Welcome Video (Owner)"),
        BotCommand("removewelcomevideo", "Remove Welcome Video (Owner)"),
        BotCommand("broadcast",         "Broadcast Message (Owner)"),
        BotCommand("setbot",          "ON/OFF Bot (Owner)"),
    ])
    if db.is_bot_on():
        count = 0
        for uid_str in db.get_all_users():
            uid = int(uid_str)
            if db.is_blocked(uid): continue
            for acct in db.get_accounts(uid):
                if not acct.get("hosted") or not acct.get("session_string"): continue
                ok = runner.start_userbot(
                    uid, acct["slot"], str(TELEGRAM_API_ID), TELEGRAM_API_HASH,
                    acct["session_string"], uid_str,
                )
                if ok: count += 1
        logger.info(f"[STARTUP] Auto-started {count} userbots.")
    else:
        logger.info("[STARTUP] Bot is OFF — skipping auto-start.")

def main():
    if not BOT_TOKEN:  raise ValueError("BOT_TOKEN not set!")
    if not OWNER_ID:   raise ValueError("OWNER_ID not set!")

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    host_conv = ConversationHandler(
        entry_points=[
            CommandHandler("host", cmd_host_start),
            CallbackQueryHandler(cmd_host_start, pattern="^host$"),
        ],
        states={
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_phone)],
            ASK_CODE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_code)],
            ASK_2FA:   [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_2fa)],
        },
        fallbacks=[CommandHandler("cancel", host_cancel)],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start",           cmd_start))
    app.add_handler(CommandHandler("help",            cmd_help))
    app.add_handler(CommandHandler("commands",        cmd_commands))
    app.add_handler(CommandHandler("flowmenu",        cmd_flowmenu))
    app.add_handler(host_conv)
    app.add_handler(CommandHandler("myaccounts",      cmd_myaccounts))
    app.add_handler(CommandHandler("status",          cmd_status))
    app.add_handler(CommandHandler("restart",         cmd_restart))
    app.add_handler(CommandHandler("logout",          cmd_logout))
    app.add_handler(CommandHandler("support",         cmd_support))
    app.add_handler(CommandHandler("supportraid",     cmd_supportraid))
    app.add_handler(CommandHandler("restartall",      cmd_restartall))
    app.add_handler(CommandHandler("refresh",         cmd_refresh))
    app.add_handler(CommandHandler("sudolist",        cmd_sudolist))
    app.add_handler(CommandHandler("setdp",           cmd_setdp))
    app.add_handler(CommandHandler("block",           cmd_block))
    app.add_handler(CommandHandler("unblock",         cmd_unblock))
    app.add_handler(CommandHandler("blockeduser",     cmd_blockeduser))
    app.add_handler(CommandHandler("stats",           cmd_stats))
    app.add_handler(CommandHandler("secretfunction",  cmd_secretfunction))
    app.add_handler(CommandHandler("setwelcomevideo", cmd_setwelcomevideo))
    app.add_handler(CommandHandler("removewelcomevideo", cmd_removewelcomevideo))
    app.add_handler(CommandHandler("broadcast",         cmd_broadcast))
    app.add_handler(CommandHandler("setbot",            cmd_setbot))
    app.add_handler(CallbackQueryHandler(callback_handler))

    if app.job_queue:
        app.job_queue.run_repeating(auto_health_check, interval=300, first=60)

    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("🤖  SID Premium Hoster Bot STARTED!")
    logger.info(f"👑  Owner ID: {OWNER_ID}")
    logger.info(f"📊  Bot Status: {'ON' if db.is_bot_on() else 'OFF'}")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
