from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import CHANNELS, MOVIE_UPDATE_CHANNEL, ADMINS, LOG_CHANNEL
from database.ia_filterdb import save_file, unpack_new_file_id
from utils import get_poster, temp , formate_file_name
import re
from Script import script
from database.users_chats_db import db

MOVIES_UPDATE_TXT = """<b>#New_File_Added

📻 Title: {movie_name}
🔊 Language: {languages} 
🌟 Rating: {rating} / 10
📀 RunTime: {duration}
🎥 Quality: Proper HDRip

<blockquote>🎭 Genres: {genres}</blockquote>
<blockquote>{description}</blockquote></b>"""

processed_movies = set()
media_filter = filters.document | filters.video

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    bot_id = bot.me.id
    media = getattr(message, message.media.value, None)
    if media.mime_type in ['video/mp4', 'video/x-matroska']: 
        media.file_type = message.media.value
        media.caption = message.caption
        success_sts = await save_file(media)
        if success_sts == 'suc' and await db.get_send_movie_update_status(bot_id):
            file_id, file_ref = unpack_new_file_id(media.file_id)
            await send_movie_updates(bot, file_name=media.file_name, caption=media.caption, file_id=file_id)

async def movie_name_format(file_name):
  filename = re.sub(r'http\S+', '', re.sub(r'@\w+|#\w+', '', file_name).replace('_', ' ').replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace('{', '').replace('}', '').replace('.', ' ').replace('@', '').replace(':', '').replace(';', '').replace("'", '').replace('-', '').replace('!', '')).strip()
  return filename 
    
async def get_imdb(file_name, caption):
    imdb_file_name = await movie_name_format(file_name)
    imdb = await get_poster(imdb_file_name)
    if imdb:
        caption = MOVIES_UPDATE_TXT.format(
            title=imdb.get('title'),
            rating=imdb.get('rating'),
            genres=imdb.get('genres'),
            description=imdb.get('plot'),
            languages=imdb.get('languages')
        )
        return imdb.get('title'), imdb.get('poster'), caption
    return None, None, None 

async def send_movie_updates(bot, file_name, file_id):
    imdb_title, poster_url, caption = await get_imdb(file_name)
    #if not post_mode.get('singel_post_mode' , True):
        if imdb_title in processed_movies:
            return
        processed_movies.add(imdb_title)
    if not poster_url or not caption:
        return
    btn = [
        [InlineKeyboardButton('Get File', url=f'https://t.me/{temp.U_NAME}?start=pm_mode_file_{ADMINS[0]}_{file_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(btn)
    movie_update_channel =await db.movies_update_channel_id()
    try:
        await bot.send_photo(movie_update_channel if movie_update_channel else MOVIE_UPDATE_CHANNEL, photo=poster_url, caption=caption, reply_markup=reply_markup)
    except Exception as e:
        print('Error in send_movie_updates', e)
        pass
