import os
import re
import aiohttp
import aiofiles
from PIL import Image, ImageDraw, ImageFont
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch

FONT_BOLD = "EsproMusic/assets/font_bold.ttf"
FONT_REGULAR = "EsproMusic/assets/font.ttf"
CACHE_DIR = "cache"

def clear_text(text):
    return re.sub(r"\s+", " ", text).strip()

def ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

async def get_video_data(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    results = VideosSearch(url, limit=1)
    result = (await results.next())["result"][0]

    return {
        "title": clear_text(result.get("title", "Unknown Title")),
        "duration": result.get("duration", "0:00"),
        "channel": result.get("channel", {}).get("name", "Unknown Channel"),
        "thumbnail": result["thumbnails"][0]["url"].split("?")[0],
    }

async def download_image(url, path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                async with aiofiles.open(path, mode="wb") as f:
                    await f.write(await resp.read())

async def create_pink_thumb(video_id, bot_name="Meka Bots"):
    ensure_cache_dir()
    cached_file = f"{CACHE_DIR}/{video_id}_pink.png"
    if os.path.isfile(cached_file):
        return cached_file

    try:
        data = await get_video_data(video_id)
        thumb_path = f"{CACHE_DIR}/thumb_{video_id}.jpg"
        await download_image(data["thumbnail"], thumb_path)

        # Create base image
        base = Image.new("RGB", (720, 720), "#f8cddc")
        draw = ImageDraw.Draw(base)

        # Load fonts
        font_bold = ImageFont.truetype(FONT_BOLD, 36)
        font_small = ImageFont.truetype(FONT_REGULAR, 24)

        # Paste video thumbnail
        thumb = Image.open(thumb_path).resize((150, 150))
        base.paste(thumb, (50, 50))

        # Text: Song title and channel name
        draw.text((220, 60), unidecode(data["title"]), font=font_bold, fill="white")
        draw.text((220, 110), unidecode(data["channel"]), font=font_small, fill="white")

        # Progress bar
        draw.rectangle([50, 230, 670, 250], fill="#f5a9c5")  # full bar
        draw.rectangle([50, 230, 200, 250], fill="white")  # current progress
        draw.text((50, 260), "0:24", font=font_small, fill="white")
        draw.text((620, 260), data["duration"], font=font_small, fill="white")

        # Media controls
        controls = ["⏮", "⏸", "⏭"]
        x = 270
        for icon in controls:
            draw.text((x, 320), icon, font=font_bold, fill="white")
            x += 80

        # Bot name
        draw.text((250, 670), bot_name, font=font_small, fill="white")

        # Save and clean
        base.save(cached_file)
        os.remove(thumb_path)
        return cached_file

    except Exception as e:
        print(f"Error: {e}")
        return "fallback.png"  # or default image path
