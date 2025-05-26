import os
import aiohttp
import aiofiles
from PIL import Image, ImageDraw, ImageFont
from youtubesearchpython import VideosSearch

async def get_thumb(video_id):
    results = VideosSearch(video_id, limit=1)
    data = (await results.next())["result"][0]
    title = data.get("title", "Unknown Title")
    channel = data.get("channel", {}).get("name", "Unknown Channel")
    thumb_url = data["thumbnails"][0]["url"].split("?")[0]
    duration = data.get("duration", "0:00")

    # Download thumbnail
    async with aiohttp.ClientSession() as session:
        async with session.get(thumb_url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(f"{video_id}.jpg", mode="wb")
                await f.write(await resp.read())
                await f.close()

    # Canvas
    width, height = 768, 500
    bg_color = (255, 182, 193)  # Baby pink
    base = Image.new("RGB", (width, height), bg_color)

    # Thumbnail image
    thumb = Image.open(f"{video_id}.jpg").resize((120, 120)).convert("RGBA")
    thumb_box = Image.new("RGBA", (130, 130), "white")
    thumb_box.paste(thumb, (5, 5), thumb)
    base.paste(thumb_box, (40, 40), thumb_box)

    # Fonts
    font_title = ImageFont.truetype("arial.ttf", 32)
    font_channel = ImageFont.truetype("arial.ttf", 24)
    font_small = ImageFont.truetype("arial.ttf", 20)
    font_bot = ImageFont.truetype("arial.ttf", 26)

    draw = ImageDraw.Draw(base)

    # Texts beside thumbnail
    text_x = 190
    draw.text((text_x, 50), title[:40], font=font_title, fill="black")
    draw.text((text_x, 95), channel, font=font_channel, fill="black")

    # Progress bar
    bar_y = 200
    bar_x1, bar_x2 = 60, width - 60
    bar_height = 12
    draw.rectangle([bar_x1, bar_y, bar_x2, bar_y + bar_height], fill="#d3d3d3")
    progress_width = int((bar_x2 - bar_x1) * 0.4)  # Static 40% for demo
    draw.rectangle([bar_x1, bar_y, bar_x1 + progress_width, bar_y + bar_height], fill="#1DB954")
    draw.text((bar_x2 + 5, bar_y - 4), duration, font=font_small, fill="black")

    # Spotify-style buttons (centered)
    button_y = bar_y + 40
    center_x = width // 2

    # Pause button (two bars)
    bar_w, bar_h = 8, 30
    draw.rectangle([center_x - 20, button_y, center_x - 20 + bar_w, button_y + bar_h], fill="#1DB954")
    draw.rectangle([center_x + 12, button_y, center_x + 12 + bar_w, button_y + bar_h], fill="#1DB954")

    # Music Bot name at bottom
    bot_text = "Music Bot"
    w, _ = draw.textsize(bot_text, font=font_bot)
    draw.text(((width - w) // 2, height - 50), bot_text, font=font_bot, fill="black")

    out_path = f"cache/{video_id}_thumb.png"
    base.save(out_path)
    os.remove(f"{video_id}.jpg")
    return out_path
