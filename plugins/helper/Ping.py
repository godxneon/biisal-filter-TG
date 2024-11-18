import time
from pyrogram import Client, filters
import psutil

start_time = time.time()

async def get_bot_uptime():
    # Calculate the uptime in seconds
    uptime_seconds = int(time.time() - start_time)
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60
    uptime_days = uptime_hours // 24
    uptime_weeks = uptime_days // 7
    ###############################
    uptime_string = f"{uptime_days % 7} D : {uptime_hours % 24} H : {uptime_minutes % 60} M : {uptime_seconds % 60} S"
    return uptime_string

@Client.on_message(filters.command("ping")) 
async def ping(_, message):
    start_t = time.time()
    rm = await message.reply_text("⛈")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    uptime = await get_bot_uptime()
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    await rm.edit(f"🏓 ᴘɪɴɢ: <code>{time_taken_s:.3f} ms</code>\n\n⏰ ᴜᴘᴛɪᴍᴇ: <code>{uptime}</code>\n\n🤖 ᴄᴘᴜ ᴜꜱᴀɢᴇ: <code>{cpu_usage} %</code>\n\n📥 ʀᴀᴍ ᴜꜱᴀɢᴇ: <code>{ram_usage} %</code>")
