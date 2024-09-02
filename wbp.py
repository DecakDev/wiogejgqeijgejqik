import discord
from discord.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO
import time

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Konstante
CHANNEL_ID = 1267065112456335392
BACKGROUND_URL = "https://i.ibb.co/9hMBXJV/Frame-333.png"
FONT_PATH = "Inter-SemiBold.ttf"
WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"

# Vreme kada je bot pokrenut
start_time = time.time()

@bot.event
async def on_ready():
    # Slanje poruke na webhook kada bot postane online
    uptime_status = "Bot is now online!"
    await send_webhook_message(uptime_status)

@bot.event
async def on_member_join(member):
    try:
        # Preuzimanje pozadinske slike
        response = requests.get(BACKGROUND_URL)
        background = Image.open(BytesIO(response.content))
        
        # Preuzimanje avatara člana, ili podrazumevanog avatara ako član nema avatar
        avatar_url = member.avatar.url if member.avatar else f"https://cdn.discordapp.com/embed/avatars/{int(member.discriminator) % 5}.png"
        
        # Preuzimanje avatara sa URL-a
        response = requests.get(avatar_url)
        avatar = Image.open(BytesIO(response.content)).convert("RGBA")
        
        # Rezanje avatara u oblik kruga
        avatar = avatar.resize((150, 150), Image.LANCZOS)
        mask = Image.new('L', avatar.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, avatar.size[0], avatar.size[1]), fill=255)
        avatar.putalpha(mask)
        
        # Postavljanje avatara na sredinu pozadinske slike
        avatar_position = ((background.width - avatar.width) // 2, 50)
        background.paste(avatar, avatar_position, avatar)
        
        # Učitavanje fontova
        font_welcome = ImageFont.truetype(FONT_PATH, 50)  # Font za "DOBRODOŠLI"
        font_username = ImageFont.truetype(FONT_PATH, 32)  # Manji font za korisničko ime
        
        # Dodavanje teksta "DOBRODOŠLI" ispod avatara
        text_welcome = "DOBRODOŠLI"
        text_welcome_size = draw.textbbox((0, 0), text_welcome, font=font_welcome)
        welcome_position = ((background.width - (text_welcome_size[2] - text_welcome_size[0])) // 2, avatar_position[1] + 160)
        draw.text(welcome_position, text_welcome, font=font_welcome, fill=(255, 255, 255))
        
        # Dodavanje korisničkog imena ispod "DOBRODOŠLI"
        username = f"{member.name}"  # Uklonjen tag (#)
        username_size = draw.textbbox((0, 0), username, font=font_username)
        username_position = ((background.width - (username_size[2] - username_size[0])) // 2, welcome_position[1] + 60)
        draw.text(username_position, username, font=font_username, fill=(0, 255, 255))
        
        # Čuvanje finalne slike
        image_path = "welcome_final.png"
        background.save(image_path)
        
        # Slanje slike u kanal
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(f"Dobrodošao na server, {member.mention}.", file=discord.File(image_path))
    except Exception as e:
        print(f"An error occurred: {e}")

@tasks.loop(minutes=10)  # Ponovljeno svakih 10 minuta
async def send_uptime_status():
    # Izračunavanje koliko dugo je bot online
    uptime_duration = time.time() - start_time
    uptime_status = f"Bot is online for {int(uptime_duration // 3600)} hours, {(uptime_duration % 3600) // 60} minutes."
    await send_webhook_message(uptime_status)

async def send_webhook_message(content):
    # Funkcija za slanje poruke preko webhooka
    data = {
        "content": content
    }
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        response.raise_for_status()  # Proverava da li je zahtev uspešan
    except requests.exceptions.RequestException as e:
        print(f"Failed to send webhook message: {e}")

@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} is ready and online!")
    send_uptime_status.start()  # Pokreće se task koji šalje uptime status

bot.run("YOUR_DISCORD_BOT_TOKEN")
