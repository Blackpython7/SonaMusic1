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

    thumb = Image.open(f"{video_id}.jpg").resize((100, 100)).convert("RGBA")
    base = Image.new("RGB", (768, 768), "#fdb4d9")
    card = Image.new("RGBA", (700, 250), (255, 255, 255, 20))
    draw = ImageDraw.Draw(card)

    font_title = ImageFont.truetype("arial.ttf", 40)
    font_channel = ImageFont.truetype("arial.ttf", 30)
    font_bot = ImageFont.truetype("arial.ttf", 28)

    card.paste(thumb, (20, 20))
    draw.text((140, 30), title[:40], font=font_title, fill="white")
    draw.text((140, 90), channel, font=font_channel, fill="white")
    draw.text((20, 150), "0:24", font=font_channel, fill="white")
    draw.text((600, 150), duration, font=font_channel, fill="white")
    draw.rectangle((100, 160, 580, 170), fill="white")
    draw.text((300, 190), "◄   ❚❚   ►", font=font_channel, fill="white")

    base.paste(card, (30, 300), card)
    draw_base = ImageDraw.Draw(base)
    w, _ = draw_base.textsize("Meka Bots", font=font_bot)
    draw_base.text(((768 - w) // 2, 720), "Meka Bots", font=font_bot, fill="white")

    out_path = f"cache/{video_id}_thumb.png"
    base.save(out_path)
    os.remove(f"{video_id}.jpg")
    return out_path
