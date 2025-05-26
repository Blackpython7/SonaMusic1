import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageOps
from youtubesearchpython import VideosSearch  # <- Correct import
from config import YOUTUBE_IMG_URL


def clear(text):
    words = text.split(" ")
    title = ""
    for word in words:
        if len(title) + len(word) < 60:
            title += " " + word
    return title.strip()


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()


async def get_thumb(videoid):
    try:
        out_path = f"cache/{videoid}.png"
        if os.path.isfile(out_path):
            return out_path

        # Search YouTube
        results = VideosSearch(videoid, limit=1)
        result = (await results.next())["result"][0]

        title = clear(re.sub(r"\W+", " ", result.get("title", "Unknown Title")).title())
        channel = result.get("channel", {}).get("name", "Unknown Channel")
        duration = result.get("duration", "0:00")
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]

        # Download thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/thumb{videoid}.png", "wb") as f:
                        await f.write(await resp.read())

        # Create base image
        width, height = 768, 500
        base = Image.new("RGB", (width, height), (255, 182, 193))  # Baby pink

        # Add square thumbnail
        thumb = Image.open(f"cache/thumb{videoid}.png").resize((120, 120)).convert("RGBA")
        thumb_box = Image.new("RGBA", (130, 130), "white")
        thumb_box.paste(thumb, (5, 5), thumb)
        base.paste(thumb_box, (40, 40), thumb_box)

        # Fonts
        font_title = load_font("EsproMusic/assets/font.ttf", 32)
        font_channel = load_font("EsproMusic/assets/font2.ttf", 24)
        font_small = load_font("EsproMusic/assets/font2.ttf", 20)
        font_bot = load_font("EsproMusic/assets/font2.ttf", 24)

        draw = ImageDraw.Draw(base)

        # Title + Channel
        draw.text((190, 50), title, font=font_title, fill="black")
        draw.text((190, 90), channel, font=font_channel, fill="black")

        # Progress bar
        bar_y = 200
        bar_x1, bar_x2 = 60, width - 60
        bar_height = 12
        draw.rectangle([bar_x1, bar_y, bar_x2, bar_y + bar_height], fill="#d3d3d3")
        progress_width = int((bar_x2 - bar_x1) * 0.35)
        draw.rectangle([bar_x1, bar_y, bar_x1 + progress_width, bar_y + bar_height], fill="#1DB954")
        draw.text((bar_x2 + 5, bar_y - 4), duration, font=font_small, fill="black")

        # Buttons
        button_y = bar_y + 40
        center_x = width // 2
        draw.rectangle([center_x - 20, button_y, center_x - 12, button_y + 30], fill="#1DB954")
        draw.rectangle([center_x + 12, button_y, center_x + 20, button_y + 30], fill="#1DB954")

        # Footer: Music Bot Name
        bot_text = "Meka Bots"
        w, _ = draw.textsize(bot_text, font=font_bot)
        draw.text(((width - w) // 2, height - 40), bot_text, font=font_bot, fill="black")

        base.save(out_path)
        os.remove(f"cache/thumb{videoid}.png")
        return out_path

    except Exception as e:
        print("Thumbnail Error:", e)
        return YOUTUBE_IMG_URL
