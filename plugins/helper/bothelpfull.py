import random
from pyrogram import Client, filters , enums
from pyrogram.types import InlineKeyboardMarkup , InlineKeyboardButton
from info import ADMINS 
import re
from database.users_chats_db import db

@Client.on_message(filters.command("set_muc") & filters.user(ADMINS))
async def set_muc_id(client, message):
    try:
        id = message.command[1]
        if id:
            is_suc = await db.movies_update_channel_id(int(id))
            if is_suc:
                await message.reply("Successfully set movies update  channel id : " + id)
            else:
                await message.reply("Failed to set movies update channel id : " + id)
        else:
            await message.reply("Invalid channel id : " + id)
    except Exception as e:
        print('Err in set_muc_id', e)
        await message.reply("Failed to set movies channel id!")

@Client.on_message(filters.command("del_muc") & filters.user(ADMINS))
async def del_muc_id(client, message):
    try:
        is_suc = await db.del_movies_channel_id()
        if is_suc:
            await message.reply("Successfully deleted movies channel id")
        else:
            await message.reply("Failed to delete movies channel id")
    except Exception as e:
        print('Err in del_muc_id', e)
        await message.reply("Failed to delete movies channel id!")

@Client.on_message(filters.regex("http") & filters.regex("www") | filters.regex("https") | filters.regex("t.me") & filters.incoming)
async def nolink(bot, message):
    user_id = message.from_user.id
    if user_id in ADMINS: return 
    await message.delete()
	
#@Client.on_message(filters.forwarded & filters.incoming)
#async def forward(bot, message):
    #user_id = message.from_user.id
    #if user_id in ADMINS: return 
    #await message.delete()
