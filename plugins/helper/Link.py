from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.command("link") & filters.user(ADMINS))
async def generate_link(client, message):
    command_text = message.text.split(maxsplit=1)
    if len(command_text) < 2:
        await message.reply("Please Provide The Name For The Movie! Example:<code>/link game of thrones</code>")
        return
    movie_name = command_text[1].replace(" ", "-")
    link = f"https://telegram.me/Oru_adaar_Robot?start=getfile-{movie_name}"
    
    await message.reply(
        text=f"Here Is Your Link: {link}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="💥 Share To Link 🔗", url=f"https://telegram.me/share/url?url={link}")]]
        )
    )
