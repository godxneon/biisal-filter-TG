import sys
import os, requests
import logging
import random
import asyncio
import string
import pytz
from os import environ, execle, system
from datetime import timedelta
from datetime import datetime as dt
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup , ForceReply
from database.ia_filterdb import Media, get_file_details, get_bad_files, unpack_new_file_id
from database.users_chats_db import db
from database.config_db import mdb
from plugins.pm_filter import auto_filter
from utils import formate_file_name, get_settings, save_group_settings, is_req_subscribed, get_size, is_check_admin, get_status, temp, get_readable_time
import re
import base64
from info import *
import traceback
logger = logging.getLogger(__name__)

import pymongo

inclient = pymongo.MongoClient(DATABASE_URI)
indb = inclient[DATABASE_NAME]

infile = indb['file_reply_text']

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client:Client, message): 
    pm_mode = False
    try:
         data = message.command[1]
         if data.startswith('pm_mode_'):
             pm_mode = True
    except:
        pass
    
    if len(message.command) == 2 and message.command[1].startswith('getfile'):
        searches = message.command[1].split("-", 1)[1] 
        search = searches.replace('-',' ')
        message.text = search 
        await auto_filter(client, message) 
        return
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        status = get_status()
        buttons = [[                   
           InlineKeyboardButton('• How To Use Me •', url=f't.me/{temp.U_NAME}?start=help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        aks=await message.reply_text(text=f"<b>🙋 Yes {status},\nHow Can I Help You??</b>", reply_markup=reply_markup)
        await asyncio.sleep(15)
        await aks.delete()
        await message.delete()
        if (str(message.chat.id)).startswith("-100") and not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            group_link = await message.chat.export_invite_link()
            user = message.from_user.mention if message.from_user else "Dear" 
            await client.send_message(LOG_CHANNEL, script.NEW_GROUP_TXT.format(temp.B_LINK, message.chat.title, message.chat.id, message.chat.username, group_link, total, user))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.NEW_USER_TXT.format(temp.B_LINK, message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('⇆ Add Me To Your Groups ⇆', url=f'http://t.me/{temp.U_NAME}?startgroup=start')
        ],[
            InlineKeyboardButton('🗽 Features', callback_data='features'),
            InlineKeyboardButton('🧑‍💻 Owner', callback_data='owner_info')
        ],[
            InlineKeyboardButton('🎭 sᴜᴘᴘᴏʀᴛ', callback_data='comunity_link'),
            InlineKeyboardButton('🏷 About', callback_data='about')
        ],[
            InlineKeyboardButton('🤷‍♂ How To Request Movies 🤷‍♂', callback_data='earn')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(photo=START_IMG, caption=script.START_TXT.format(get_status(), message.from_user.mention, message.from_user.id),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    if AUTH_CHANNEL and not await is_req_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL), creates_join_request=True)
        except ChatAdminRequired:
            logger.error("Make Sure Bot Is Admin In Forcesub Channel")
            return
        btn = [[
            InlineKeyboardButton("🔮 ᴊᴏɪɴ ɴᴏᴡ 🔮", url=invite_link.invite_link)
        ]]

        if message.command[1] != "subscribe":
            
            try:
                chksub_data = message.command[1].replace('pm_mode_', '') if pm_mode else message.command[1]
                kk, grp_id, file_id = chksub_data.split('_', 2)
                pre = 'checksubp' if kk == 'filep' else 'checksub'
                btn.append(
                    [InlineKeyboardButton("♻️ ᴛʀʏ ᴀɢᴀɪɴ ♻️", callback_data=f"checksub#{file_id}#{int(grp_id)}")]
                )
            except (IndexError, ValueError):
                print('IndexError: ', IndexError)
                btn.append(
                    [InlineKeyboardButton("♻️ ᴛʀʏ ᴀɢᴀɪɴ ♻️", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")]
                )
        await client.send_message(
            chat_id=message.from_user.id,
            text="<b>📢 First Join Our BackUp Channel Then You Will Get Movie Otherwise You Will Not Get it.\n\n✨ Click Join Now Button 👇</b>",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.HTML
        )
        return

    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
            InlineKeyboardButton('⇆ Add Me To Your Groups ⇆', url=f'http://t.me/{temp.U_NAME}?startgroup=start')
        ],[
            InlineKeyboardButton('🗽 Features', callback_data='features'),
            InlineKeyboardButton('🧑‍💻 Owner', callback_data='owner_info')
        ],[            
            InlineKeyboardButton('🎭 sᴜᴘᴘᴏʀᴛ', callback_data='comunity_link'),
            InlineKeyboardButton('🏷 About', callback_data='about')
        ],[
            InlineKeyboardButton('🤷‍♂ How To Request Movies 🤷‍♂', callback_data='earn')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        return await message.reply_photo(photo=START_IMG, caption=script.START_TXT.format(get_status(), message.from_user.mention, message.from_user.id),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    if data.startswith('pm_mode_'):
        pm_mode = True
        data = data.replace('pm_mode_', '')
    try:
        pre, grp_id, file_id = data.split('_', 2)
    except:
        pre, grp_id, file_id = "", 0, data
            
    if data and data.startswith("allfiles"):
        _, key = data.split("_", 1)
        files = temp.FILES_ID.get(key)
        if not files:
            await message.reply_text("<b>⚠️ ᴀʟʟ ꜰɪʟᴇs ɴᴏᴛ ꜰᴏᴜɴᴅ ⚠️</b>")
            return
        files_to_delete = []
        for file in files:
            user_id = message.from_user.id 
            grp_id = temp.CHAT.get(user_id)
            settings = await get_settings(grp_id, pm_mode=pm_mode)
            CAPTION = settings['caption']
            f_caption = FILE_CAPTION.format(
                file_name=formate_file_name(file.file_name),
                file_size=get_size(file.file_size),
                file_caption=file.caption
            )
            btn = [[                
                InlineKeyboardButton('🍿 𝗝𝗢𝗜𝗡 𝗡𝗘𝗪 𝗢𝗧𝗧 𝗠𝗢𝗩𝗜𝗘𝗦 🍿', url="https://t.me/+F3aZLBpIyMpmY2Y1")  
            ]]
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file.file_id,
                caption=f_caption,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            files_to_delete.append(msg)

        k = await msg.reply("<b>ㅤㅤ❗️❗️<u>IMPORTANT❗️️❗️</u>\n\nThis File Will Be Deleted From Here Within <u>10 Minute</u>. Please Forward This File To Your Saved Messages And Start Download There.</b>",quote=True)
        await asyncio.sleep(100)
        await k.delete()
        await message.delete()
        for file in files_to_delete:
            try:
                await file.delete()
            except:
                pass
        return 
    if not data:
        return

    files_ = await get_file_details(file_id)           
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        return await message.reply('<b>⚠️ ᴀʟʟ ꜰɪʟᴇs ɴᴏᴛ ꜰᴏᴜɴᴅ ⚠️</b>')
    files = files_[0]
    settings = await get_settings(grp_id , pm_mode=pm_mode)
    CAPTION = settings['caption']
    f_caption = FILE_CAPTION.format(
        file_name = formate_file_name(files.file_name),
        file_size = get_size(files.file_size),
        file_caption=files.caption
    )
    btn = [[
        InlineKeyboardButton('🍿 𝗝𝗢𝗜𝗡 𝗡𝗘𝗪 𝗢𝗧𝗧 𝗠𝗢𝗩𝗜𝗘𝗦 🍿', url="https://t.me/+F3aZLBpIyMpmY2Y1")  
    ]]
    msg = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        reply_markup=InlineKeyboardMarkup(btn)
    )
    k = await msg.reply("<b>ㅤㅤ❗️❗️<u>IMPORTANT❗️️❗️</u>\n\nThis File Will Be Deleted From Here Within <u>10 Minute</u>. Please Forward This File To Your Saved Messages And Start Download There.</b>",quote=True)
    await asyncio.sleep(100)
    await msg.delete()
    await k.delete()
    await message.delete()
    return 

@Client.on_message(filters.command('delete'))
async def delete(bot, message):
    if message.from_user.id not in ADMINS:
        await message.reply('ᴏɴʟʏ ᴛʜᴇ ʙᴏᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ... 😑')
        return
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("ᴘʀᴏᴄᴇssɪɴɢ...⏳", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return
    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('<b>ᴛʜɪs ɪs ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ ꜰɪʟᴇ ꜰᴏʀᴍᴀᴛ</b>')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)
    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('<b>ꜰɪʟᴇ ɪs sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ꜰʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ 💥</b>')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('<b>ꜰɪʟᴇ ɪs sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ꜰʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ 💥</b>')
        else:
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('<b>ꜰɪʟᴇ ɪs sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ꜰʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ 💥</b>')
            else:
                await msg.edit('<b>ꜰɪʟᴇ ɴᴏᴛ ꜰᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ</b>')

@Client.on_message(filters.command('deleteall'))
async def delete_all_index(bot, message):
    files = await Media.count_documents()
    if int(files) == 0:
        return await message.reply_text('Not have files to delete')
    btn = [[
            InlineKeyboardButton(text="ʏᴇs", callback_data="all_files_delete")
        ],[
            InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data="close_data")
        ]]
    if message.from_user.id not in ADMINS:
        await message.reply('ᴏɴʟʏ ᴛʜᴇ ʙᴏᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ... 😑')
        return
    await message.reply_text('<b>ᴛʜɪs ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ɪɴᴅᴇxᴇᴅ ꜰɪʟᴇs.\nᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ??</b>', reply_markup=InlineKeyboardMarkup(btn))

@Client.on_message(filters.command('settings'))
async def settings(client, message):
    if message.from_user.id not in ADMINS:
        d = await message.reply('ᴏɴʟʏ ᴛʜᴇ ʙᴏᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ..😑')
        await asyncio.sleep(15) 
        await d.delete()
        await message.delete()
        return
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return await message.reply("<b>💔 ʏᴏᴜ ᴀʀᴇ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ...</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("<b>ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ɢʀᴏᴜᴘ.</b>")
    grp_id = message.chat.id
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('<b>ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪꜱ ɢʀᴏᴜᴘ</b>')
    settings = await get_settings(grp_id)
    title = message.chat.title
    if settings is not None:
            buttons = [[
                InlineKeyboardButton('ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}'),
                InlineKeyboardButton('ᴏɴ ✓' if settings["auto_filter"] else 'ᴏғғ ✗', callback_data=f'setgs#auto_filter#{settings["auto_filter"]}#{grp_id}')
            ],[
                InlineKeyboardButton('ɪᴍᴅʙ', callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}'),
                InlineKeyboardButton('ᴏɴ ✓' if settings["imdb"] else 'ᴏғғ ✗', callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}')
            ],[
                InlineKeyboardButton('sᴘᴇʟʟ ᴄʜᴇᴄᴋ', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}'),
                InlineKeyboardButton('ᴏɴ ✓' if settings["spell_check"] else 'ᴏғғ ✗', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}')
            ],[
                InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}'),
                InlineKeyboardButton(f'{get_readable_time(DELETE_TIME)}' if settings["auto_delete"] else 'ᴏғғ ✗', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}')
            ],[
                InlineKeyboardButton('ʀᴇsᴜʟᴛ ᴍᴏᴅᴇ', callback_data=f'setgs#link#{settings["link"]}#{str(grp_id)}'),
                InlineKeyboardButton('⛓ ʟɪɴᴋ' if settings["link"] else '🧲 ʙᴜᴛᴛᴏɴ', callback_data=f'setgs#link#{settings["link"]}#{str(grp_id)}')
            ],[
                InlineKeyboardButton('❌ ᴄʟᴏsᴇ ❌', callback_data='close_data')
            ]]
            await message.reply_text(
                text=f"ᴄʜᴀɴɢᴇ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ꜰᴏʀ <b>'{title}'</b> ᴀs ʏᴏᴜʀ ᴡɪsʜ ✨",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
    else:
        await message.reply_text('<b>ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ 🙅</b>')        

@Client.on_message(filters.command("send"))
async def send_msg(bot, message):
    if message.from_user.id not in ADMINS:
        await message.reply('<b>ᴏɴʟʏ ᴛʜᴇ ʙᴏᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ...</b>')
        return
    if message.reply_to_message:
        target_ids = message.text.split(" ")[1:]
        if not target_ids:
            await message.reply_text("<b>ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴏɴᴇ ᴏʀ ᴍᴏʀᴇ ᴜꜱᴇʀ ɪᴅꜱ ᴀꜱ ᴀ ꜱᴘᴀᴄᴇ...</b>")
            return
        out = "\n\n"
        success_count = 0
        try:
            users = await db.get_all_users()
            for target_id in target_ids:
                try:
                    user = await bot.get_users(target_id)
                    out += f"{user.id}\n"
                    await message.reply_to_message.copy(int(user.id))
                    success_count += 1
                except Exception as e:
                    out += f"‼️ ᴇʀʀᴏʀ ɪɴ ᴛʜɪꜱ ɪᴅ - <code>{target_id}</code> <code>{str(e)}</code>\n"
            await message.reply_text(f"<b>✅️ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴍᴇꜱꜱᴀɢᴇ ꜱᴇɴᴛ ɪɴ `{success_count}` ɪᴅ\n<code>{out}</code></b>")
        except Exception as e:
            await message.reply_text(f"<b>‼️ ᴇʀʀᴏʀ - <code>{e}</code></b>")
    else:
        await message.reply_text("<b>ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴀꜱ ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇꜱꜱᴀɢᴇ, ꜰᴏʀ ᴇɢ - <code>/send userid1 userid2</code></b>")

@Client.on_message(filters.command("search"))
async def search_files(bot, message):
    if message.from_user.id not in ADMINS:
        await message.reply('Only the bot owner can use this command... 😑')
        return
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, this command won't work in groups. It only works in my PM!</b>")  
    try:
        keyword = message.text.split(" ", 1)[1]
    except IndexError:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, give me a keyword along with the command to delete files.</b>")
    files, total = await get_bad_files(keyword)
    if int(total) == 0:
        await message.reply_text('<i>I could not find any files with this keyword 😐</i>')
        return 
    file_names = "\n\n".join(f"{index + 1}. {item['file_name']}" for index, item in enumerate(files))
    file_data = f"🚫 Your search - '{keyword}':\n\n{file_names}"    
    with open("file_names.txt", "w" , encoding='utf-8') as file:
        file.write(file_data)
    await message.reply_document(
        document="file_names.txt",
        caption=f"<b>♻️ ʙʏ ʏᴏᴜʀ ꜱᴇᴀʀᴄʜ, ɪ ꜰᴏᴜɴᴅ - <code>{total}</code> ꜰɪʟᴇs</b>",
        parse_mode=enums.ParseMode.HTML
    )
    os.remove("file_names.txt")

@Client.on_message(filters.command("deletefiles"))
async def deletemultiplefiles(bot, message):
    if message.from_user.id not in ADMINS:
        await message.reply('ᴏɴʟʏ ᴛʜᴇ ʙᴏᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ... 😑')
        return
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>ʜᴇʏ {message.from_user.mention}, ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏɴ'ᴛ ᴡᴏʀᴋ ɪɴ ɢʀᴏᴜᴘs. ɪᴛ ᴏɴʟʏ ᴡᴏʀᴋs ᴏɴ ᴍʏ ᴘᴍ !!</b>")
    else:
        pass
    try:
        keyword = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(f"<b>ʜᴇʏ {message.from_user.mention}, ɢɪᴠᴇ ᴍᴇ ᴀ ᴋᴇʏᴡᴏʀᴅ ᴀʟᴏɴɢ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ꜰɪʟᴇs.</b>")
    files, total = await get_bad_files(keyword)
    if int(total) == 0:
        await message.reply_text('<i>ɪ ᴄᴏᴜʟᴅ ɴᴏᴛ ꜰɪɴᴅ ᴀɴʏ ꜰɪʟᴇs ᴡɪᴛʜ ᴛʜɪs ᴋᴇʏᴡᴏʀᴅ 😐</i>')
        return 
    btn = [[
       InlineKeyboardButton("ʏᴇs, ᴄᴏɴᴛɪɴᴜᴇ ✅", callback_data=f"killfilesak#{keyword}")
       ],[
       InlineKeyboardButton("ɴᴏ, ᴀʙᴏʀᴛ ᴏᴘᴇʀᴀᴛɪᴏɴ 😢", callback_data="close_data")
    ]]
    await message.reply_text(
        text=f"<b>ᴛᴏᴛᴀʟ ꜰɪʟᴇs ꜰᴏᴜɴᴅ - <code>{total}</code>\n\nᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ?\n\nɴᴏᴛᴇ:- ᴛʜɪs ᴄᴏᴜʟᴅ ʙᴇ ᴀ ᴅᴇsᴛʀᴜᴄᴛɪᴠᴇ ᴀᴄᴛɪᴏɴ!!</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("del_file"))
async def delete_files(bot, message):
    if message.from_user.id not in ADMINS:
        await message.reply('Only the bot owner can use this command... 😑')
        return
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, this command won't work in groups. It only works on my PM!</b>")    
    try:
        keywords = message.text.split(" ", 1)[1].split(",")
    except IndexError:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, give me keywords separated by commas along with the command to delete files.</b>")   
    deleted_files_count = 0
    not_found_files = []
    for keyword in keywords:
        result = await Media.collection.delete_many({'file_name': keyword.strip()})
        if result.deleted_count:
            deleted_files_count += 1
        else:
            not_found_files.append(keyword.strip())
    if deleted_files_count > 0:
        await message.reply_text(f'<b>{deleted_files_count} file successfully deleted from the database 💥</b>')
    if not_found_files:
        await message.reply_text(f'<b>Files not found in the database - <code>{", ".join(not_found_files)}</code></b>')

@Client.on_message(filters.command('restart') & filters.user(ADMINS))
async def restart_bot(client, message):
    msg = await message.reply_text(
        text="<b>Bot Restarting ...</b>"
    )        
    await msg.edit("<b>Restart Successfully Completed ✅</b>")
    system("git pull -f && pip3 install --no-cache-dir -r requirements.txt")
    execle(sys.executable, sys.executable, "bot.py", environ)
   
@Client.on_message(filters.private & filters.command("pm_search_on"))
async def set_pm_search_on(client, message):
    user_id = message.from_user.id
    bot_id = client.me.id
    if user_id not in ADMINS:
        await message.delete()
        return
    
    await db.update_pm_search_status(bot_id, enable=True)
    await message.reply_text("<b><i>✅️ ᴘᴍ ꜱᴇᴀʀᴄʜ ᴇɴᴀʙʟᴇᴅ, ꜰʀᴏᴍ ɴᴏᴡ ᴜꜱᴇʀꜱ ᴀʙʟᴇ ᴛᴏ ꜱᴇᴀʀᴄʜ ᴍᴏᴠɪᴇ ɪɴ ʙᴏᴛ ᴘᴍ.</i></b>")

@Client.on_message(filters.private & filters.command("pm_search_off"))
async def set_pm_search_off(client, message):
    user_id = message.from_user.id
    bot_id = client.me.id
    if user_id not in ADMINS:
        await message.delete()
        return
    
    await db.update_pm_search_status(bot_id, enable=False)
    await message.reply_text("<b><i>❌️ ᴘᴍ ꜱᴇᴀʀᴄʜ ᴅɪꜱᴀʙʟᴇᴅ, ꜰʀᴏᴍ ɴᴏᴡ ɴᴏ ᴏɴᴇ ᴄᴀɴ ᴀʙʟᴇ ᴛᴏ ꜱᴇᴀʀᴄʜ ᴍᴏᴠɪᴇ ɪɴ ʙᴏᴛ ᴘᴍ.</i></b>")

@Client.on_message(filters.private & filters.command("movie_update_on"))
async def set_send_movie_on(client, message):
    user_id = message.from_user.id
    bot_id = client.me.id
    if user_id not in ADMINS:
        await message.delete()
        return    
    await db.update_send_movie_update_status(bot_id, enable=True)
    await message.reply_text("<b><i>✅️ ꜱᴇɴᴅ ᴍᴏᴠɪᴇ ᴜᴘᴅᴀᴛᴇ ᴇɴᴀʙʟᴇᴅ.</i></b>")

@Client.on_message(filters.private & filters.command("movie_update_off"))
async def set_send_movie_update_off(client, message):
    user_id = message.from_user.id
    bot_id = client.me.id
    if user_id not in ADMINS:
        await message.delete()
        return    
    await db.update_send_movie_update_status(bot_id, enable=False)
    await message.reply_text("<b><i>❌️ ꜱᴇɴᴅ ᴍᴏᴠɪᴇ ᴜᴘᴅᴀᴛᴇ ᴅɪꜱᴀʙʟᴇᴅ.</i></b>")
    
@Client.on_message(filters.command("list") & filters.incoming)
async def latest(client, message):
    text_data = infile.find_one({"_id": "file_text"})
    if not text_data:
        return
    text = text_data.get(f"text")
    if text == "off":
        await message.reply("The List Of New Releases Are Empty.😔")
        return
    else:
        mc = await message.reply_text(f"{text}")
        await asyncio.sleep(70)
        await mc.delete()
        await message.delete()

@Client.on_message(filters.command('file_text') & filters.user(ADMINS))
async def set_file_text_command(client, message):
    text_data = infile.find_one({"_id": "file_text"})    
    if len(message.command) == 1:        
        if not text_data:
            await message.reply("You don't have any text")
            return
        text = text_data.get("text")
        if text == "off":
            await message.reply("You don't have any text")
            return
        else:
            await message.reply(f"current text is\n\n {text}")
            return 
    else:
        text = message.text.split(" ", 1)[1]
        if text == "off":
            if not text_data:                    
                await message.reply(f"Text have Deleted.")
            else:
                infile.update_one(
                    {"_id": "file_text"},
                    {"$set": {"text": "off"}},
                    upsert=True
                )
                await message.reply("Text have Deleted.")
        else:
            infile.update_one(
                    {"_id": "file_text"},
                    {"$set": {"text": text}},
                    upsert=True
            )
            await message.reply("Saved buddy 😁.")
