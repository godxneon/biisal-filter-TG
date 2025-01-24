import os
import asyncio
import random
import pytz
import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, User, InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest
from info import CHAT_ID, TEXT, APPROVED, APICS, LOG_CHANNEL

@Client.on_chat_join_request((filters.group | filters.channel) & filters.chat(CHAT_ID) if CHAT_ID else (filters.group | filters.channel))
async def autoapprove(client, message: ChatJoinRequest):
    chat=message.chat 
    user=message.from_user 
    print(f"{user.first_name} Joined (Approved)") 
    await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)       
    buttons = [[
                InlineKeyboardButton('🎭 GROUP', url='https://t.me/KLMovieGroup'),       
                InlineKeyboardButton('CHANNEL 🎫', url='https://t.me/team_KL')
             ],[
                InlineKeyboardButton('♻️ Movie Request Group ♻️', url='https://t.me/KeralaRockers_Group')
              ]]      
    await client.send_photo(
        photo=random.choice(APICS),
        chat_id=message.from_user.id, 
        caption=TEXT.format(mention=user.mention, title=chat.title),
        reply_markup=InlineKeyboardMarkup(buttons)
        )   
#    await asyncio.sleep(35)
#    await k.delete()
    
