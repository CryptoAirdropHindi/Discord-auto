import os
import time
import asyncio
import requests
import random
import sys
from datetime import datetime, timedelta
from discord.ext import tasks, commands
from discord import Message

print(r'''
    clear
    echo -e "${CYAN}"
    echo -e "    ${RED}██╗  ██╗ █████╗ ███████╗ █████╗ ███╗   ██╗${NC}"
    echo -e "    ${GREEN}██║  ██║██╔══██╗██╔════╝██╔══██╗████╗  ██║${NC}"
    echo -e "    ${BLUE}███████║███████║███████╗███████║██╔██╗ ██║${NC}"
    echo -e "    ${YELLOW}██╔══██║██╔══██║╚════██║██╔══██║██║╚██╗██║${NC}"
    echo -e "    ${MAGENTA}██║  ██║██║  ██║███████║██║  ██║██║ ╚████║${NC}"
    echo -e "    ${CYAN}╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝${NC}"
    echo -e "${BLUE}=======================================================${NC}"
    echo -e "${GREEN}            🚀 Naptha Node Management 🚀${NC}"
    echo -e "${BLUE}=======================================================${NC}"
    echo -e "${CYAN}    🌐  Telegram: @CryptoAirdropHindi${NC}"
    echo -e "${CYAN}    📺  YouTube:  @CryptoAirdropHindi6${NC}"
    echo -e "${CYAN}    💻  GitHub:   github.com/CryptoAirdropHindi${NC}")

# === Konfigurasi ===
DISCORD_USER_TOKEN = "TOKEN_DISCORD" #ganti dengan TOKEN discord
CHANNEL_ID = 12345  # Ganti dengan ID channel yang kamu targetkan
INTERVAL_MIN = 5 #random time minimal
INTERVAL_MAX = 9 #random time maksimal
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma:2b"

# === State ===
next_reply_time = datetime.now()
pending_message = None
has_printed_wait = False

# Inisialisasi client sebagai selfbot
client = commands.Bot(command_prefix="!", self_bot=True)

# === Fungsi ambil jawaban dari AI lokal (Ollama) ===
async def get_ai_reply(prompt):
    try:
        crypto_prompt = (
            "You’re a laid-back friend replying casually and briefly. "
            "Keep it simple, chill, and natural — no extra stuff, no emojis, no repeats. "
            "Sometimes say 'yeah', 'true', or 'same', but keep it random and real.\n\n"
            f"Message: {prompt}\n"
            "Reply:"
        )

        response = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": crypto_prompt,
            "stream": False
        })
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception as e:
        print(f"[❌] Error Ollama: {e}")
        return "have a nice day"

# === Event ketika bot siap ===
@client.event
async def on_ready():
    print(f"[✅] Login sebagai {client.user} (akun pribadi aktif)")
    reply_loop.start()
    auto_restart.start()

# === Event ketika pesan baru diterima ===
@client.event
async def on_message(message: Message):
    global pending_message
    if message.channel.id != CHANNEL_ID:
        return
    if message.author.id == client.user.id:
        return

    # print(f"[📥] Pesan dari {message.author.name}: {message.content}")
    pending_message = message

# === Loop interval kirim balasan ===
@tasks.loop(seconds=10)
async def reply_loop():
    global pending_message, next_reply_time, has_printed_wait

    if not pending_message:
        has_printed_wait = False  # reset kalau gak ada pesan
        return

    now = datetime.now()
    if now < next_reply_time:
        if not has_printed_wait:
            remaining = int((next_reply_time - now).total_seconds() // 60)
            print(f"[⏳] Menunggu {remaining} menit sebelum balas...")
            has_printed_wait = True
        return

    # Kalau sudah waktunya balas, reset flag agar bisa print lagi next interval
    has_printed_wait = False

    reply = await get_ai_reply(pending_message.content)
    reply = await get_ai_reply(pending_message.content)

    # === Filtering respons AI yang tidak layak dikirim ===
    banned_phrases = [
        "Sure, here's a random sentence",
        "Here's a sentence",
        "As an AI language model",
        "In conclusion"
    ]

    if any(phrase.lower() in reply.lower() for phrase in banned_phrases) or reply.count("\n") >= 2:
        print("[⚠️] Balasan AI tidak cocok, tidak dikirim.")
        pending_message = None
        next_reply_time = datetime.now() + timedelta(minutes=1)
        return

    # === Kirim jika lolos filter ===
    try:
        if random.choice([True, False]):
            content = f"{pending_message.author.mention} {reply}"
        else:
            content = reply

        await pending_message.channel.send(content)
        print(f"[✅] Balas ke {pending_message.author.name}: {reply}")

        wait_minutes = random.randint(INTERVAL_MIN, INTERVAL_MAX)
        next_reply_time = datetime.now() + timedelta(minutes=wait_minutes)
        pending_message = None
    except Exception as e:
        print(f"[❌] Gagal kirim: {e}")

# === Restart otomatis setiap 2 jam ===
@tasks.loop(hours=2)
async def auto_restart():
    print(f"[♻️] Restart otomatis dimulai pada {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    python = sys.executable
    os.execv(python, [python] + sys.argv)

@auto_restart.before_loop
async def before_auto_restart():
    await client.wait_until_ready()
    print(f"[⏳] Script akan auto restart 2 jam sekali")
    await asyncio.sleep(2 * 60 * 60)  # 3 jam delay sebelum loop pertama

# === Jalankan bot ===
client.run(DISCORD_USER_TOKEN)
