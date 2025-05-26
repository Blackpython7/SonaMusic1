import os
import re
import random
import aiofiles
import aiohttp

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch

from EsproMusic import app
from config import YOUTUBE_IMG_URL


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))


def clear(text):
    words = text.split(" ")
    title = ""
    for word in words:
        if len(title) + len(word) < 60:
            title += " " + word
    return title.strip()


async def get_thumb(videoid):
    path = f"cache/{videoid}.png"
    if os.path.isfile(path):
        return path

    try:
        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        result = (await results.next())["result"][0]

        title = re.sub("\W+", " ", result.get("title", "Unsupported Title")).title()
        duration = result.get("duration", "Unknown Mins")
        thumbnail_url = result["thumbnails"][0]["url"].split("?")[0]
        views = result.get("viewCount", {}).get("short", "Unknown Views")
        channel = result.get("channel", {}).get("name", "Unknown Channel")

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/thumb{videoid}.png", "wb") as f:
                        await f.write(await resp.read())

        youtube_img = Image.open(f"cache/thumb{videoid}.png").convert("RGB")
        os.remove(f"cache/thumb{videoid}.png")

        # Resize and add border
        resized = changeImageSize(1280, 720, youtube_img)
        enhanced = ImageEnhance.Brightness(resized).enhance(1.1)
        contrasted = ImageEnhance.Contrast(enhanced).enhance(1.1)
        bordered = ImageOps.expand(contrasted, border=20, fill="pink")

        # Add text
        draw = ImageDraw.Draw(bordered)
        title_font = ImageFont.truetype("EsproMusic/assets/font.ttf", 50)
        small_font = ImageFont.truetype("EsproMusic/assets/font2.ttf", 40)

        draw.text((40, 600), clear(title), font=title_font, fill="white")
        draw.text((40, 660), f"{channel} • {views}", font=small_font, fill="white")
        draw.text((1080, 20), unidecode(app.name), font=small_font, fill="white")
        draw.text((1100, 660), f"{duration}", font=small_font, fill="white")

        bordered.save(path)
        return path

    except Exception as e:
        print(f"Thumbnail error: {e}")
        return YOUTUBE_IMG_URL
