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

    # Create base image with baby pink background
    base = Image.new("RGB", (768, 250), (255, 182, 193))  # baby pink

    thumb = Image.open(f"{video_id}.jpg").resize((200, 200)).convert("RGBA")

    # Paste thumbnail at left side inside a white square box with padding
    box_size = (210, 210)
    box = Image.new("RGBA", box_size, "white")
    box.paste(thumb, (5, 5), thumb)
    base.paste(box, (20, 20), box)

    draw = ImageDraw.Draw(base)

    # Load fonts
    font_title = ImageFont.truetype("arial.ttf", 30)
    font_channel = ImageFont.truetype("arial.ttf", 20)
    font_time = ImageFont.truetype("arial.ttf", 18)
    font_bot = ImageFont.truetype("arial.ttf", 24)

    # Text positions
    text_x = 250
    draw.text((text_x, 30), title[:40], font=font_title, fill="black")
    draw.text((text_x, 80), channel, font=font_channel, fill="black")

    # Draw progress bar (below texts)
    bar_x_start = text_x
    bar_x_end = 700
    bar_y = 130
    bar_height = 15

    # Background bar (light gray)
    draw.rectangle([bar_x_start, bar_y, bar_x_end, bar_y + bar_height], fill="#d3d3d3")

    # Progress - for demo, 40% filled, you can customize as needed
    progress_width = int((bar_x_end - bar_x_start) * 0.4)
    draw.rectangle([bar_x_start, bar_y, bar_x_start + progress_width, bar_y + bar_height], fill="#1DB954")  # Spotify green

    # Duration text on right of bar
    draw.text((bar_x_end + 5, bar_y), duration, font=font_time, fill="black")

    # Draw Spotify-like buttons below progress bar
    button_y = bar_y + bar_height + 15
    button_size = 35
    spacing = 50
    button_x = text_x

    # Play button (triangle)
    play_center = (button_x + button_size // 2, button_y + button_size // 2)
    points = [
        (play_center[0] - 10, play_center[1] - 15),
        (play_center[0] - 10, play_center[1] + 15),
        (play_center[0] + 15, play_center[1])
    ]
    draw.polygon(points, fill="#1DB954")

    # Pause button (two rectangles)
    pause_x = button_x + spacing
    pause_y = button_y + 10
    pause_width = 6
    pause_height = 25
    draw.rectangle([pause_x, pause_y, pause_x + pause_width, pause_y + pause_height], fill="#1DB954")
    draw.rectangle([pause_x + 15, pause_y, pause_x + 15 + pause_width, pause_y + pause_height], fill="#1DB954")

    # Skip button (two triangles pointing right)
    skip_x = pause_x + spacing
    skip_y = button_y + button_size // 2
    skip_points1 = [
        (skip_x, skip_y - 15),
        (skip_x, skip_y + 15),
        (skip_x + 15, skip_y)
    ]
    skip_points2 = [
        (skip_x + 12, skip_y - 15),
        (skip_x + 12, skip_y + 15),
        (skip_x + 27, skip_y)
    ]
    draw.polygon(skip_points1, fill="#1DB954")
    draw.polygon(skip_points2, fill="#1DB954")

    # Draw "Music Bot" text centered at bottom
    w, h = draw.textsize("Music Bot", font=font_bot)
    draw.text(((768 - w) // 2, 210), "Music Bot", font=font_bot, fill="black")

    out_path = f"cache/{video_id}_thumb.png"
    base.save(out_path)
    os.remove(f"{video_id}.jpg")
    return out_path
