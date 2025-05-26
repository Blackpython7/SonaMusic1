import os
import aiohttp
import aiofiles
from PIL import Image, ImageDraw, ImageFont
from youtubesearchpython import VideosSearch

async def get_video_data(video_id):
    results = VideosSearch(video_id, limit=1)
    data = (await results.next())["result"][0]
    return {
        "title": data.get("title", "Unknown Title"),
        "channel": data.get("channel", {}).get("name", "Unknown Channel"),
        "thumbnail": data["thumbnails"][0]["url"].split("?")[0],
        "duration": data.get("duration", "0:00")
    }

async def generate_pink_card(video_id, bot_name="Meka Bots"):
    data = await get_video_data(video_id)
    title, channel, duration, thumb_url = data["title"], data["channel"], data["duration"], data["thumbnail"]

    base = Image.new("RGB", (768, 768), "#fdb4d9")
    card = Image.new("RGBA", (700, 250), (255, 255, 255, 20))
    card_draw = ImageDraw.Draw(card)

    font_title = ImageFont.truetype("arial.ttf", 40)
    font_channel = ImageFont.truetype("arial.ttf", 30)
    font_bot = ImageFont.truetype("arial.ttf", 28)

    # Download and paste thumbnail
    async with aiohttp.ClientSession() as session:
        async with session.get(thumb_url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(f"{video_id}.jpg", mode="wb")
                await f.write(await resp.read())
                await f.close()

    thumb = Image.open(f"{video_id}.jpg").resize((100, 100)).convert("RGBA")
    card.paste(thumb, (20, 20))

    # Add song title and channel name
    card_draw.text((140, 30), title[:40], font=font_title, fill="white")
    card_draw.text((140, 90), channel, font=font_channel, fill="white")

    # Music progress bar
    card_draw.text((20, 150), "0:24", font=font_channel, fill="white")
    card_draw.text((600, 150), duration, font=font_channel, fill="white")
    card_draw.rectangle((100, 160, 580, 170), fill="white")

    # Play/pause/skip buttons (simplified)
    card_draw.text((300, 190), "◄   ❚❚   ►", font=font_channel, fill="white")

    # Paste card onto base
    base.paste(card, (30, 300), card)

    # Add bot name at bottom
    draw_base = ImageDraw.Draw(base)
    w, _ = draw_base.textsize(bot_name, font=font_bot)
    draw_base.text(((768 - w) // 2, 720), bot_name, font=font_bot, fill="white")

    # Save image
    out_path = f"{video_id}_pink.png"
    base.save(out_path)
    os.remove(f"{video_id}.jpg")
    return out_path

# Example usage
# import asyncio
# asyncio.run(generate_pink_card("Ks-_Mh1QhMc"))  # Replace with your video ID
