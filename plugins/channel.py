from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import CHANNELS, MOVIE_UPDATE_CHANNEL, ADMINS, LOG_CHANNEL
from database.ia_filterdb import save_file, unpack_new_file_id
from utils import get_poster, temp , formate_file_name
import re
from Script import script
from database.users_chats_db import db

processed_movies = set()
media_filter = filters.document | filters.video

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

async def get_imdb(file_name):
    imdb_file_name = await movie_name_format(file_name)
    imdb = await get_poster(imdb_file_name)
    if imdb:
        return imdb.get('rating'), imdb.get('genres'), imdb.get('poster')
    return None
    
async def movie_name_format(file_name):
  filename = re.sub(r'http\S+', '', re.sub(r'@\w+|#\w+', '', file_name).replace('_', ' ').replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace('{', '').replace('}', '').replace('.', ' ').replace('@', '').replace(':', '').replace(';', '').replace("'", '').replace('-', '').replace('!', '')).strip()
  return filename

async def check_qualities(text, qualities: list):
    quality = []
    for q in qualities:
        if q in text:
            quality.append(q)
    quality = ", ".join(quality)
    return quality[:-2] if quality.endswith(", ") else quality

async def send_movie_updates(bot, file_name, caption, file_id):
    try:                        
        year_match = re.search(r"\b(19|20)\d{2}\b", caption)
        year = year_match.group(0) if year_match else None      
        pattern = r"(?i)(?:s|season)0*(\d{1,2})"
        season = re.search(pattern, caption)       
        if not season:
            season = re.search(pattern, file_name) 
        if year:
            file_name = file_name[:file_name.find(year) + 4]      
        if not year:
            if season:
                season = season.group(1) if season else None       
                file_name = file_name[:file_name.find(season) + 1]
        qualities = ["YT WEB-DL", "NF WEB-DL", "AMZN WEB-DL", "BR-Rip", "DVDRip", "DSNP WEB-DL", "HQ HDRip", 
                     "WEBRip", "WEB-DL" "BluRay", "SAINA WEB-DL", "HS WEB-DL", "HDTVRip", "SS WEB-DL", 
                     "SDTVRip", "HQ BR-Rip", "ZEE5 WEB-DL", "JC WEB-DL", "JIO WEB-DL"]
        quality = await check_qualities(caption, qualities) or "Proper HDRip"
        language = ""
        nb_languages = ["Malayalam", "Bengali", "English", "Marathi", "Tamil", "Telugu", "Hindi", "Kannada", "Punjabi", "Gujrati", "Korean", "Japanese", "Bhojpuri", "Chinese", "French", "Spanish", "Norwegian", "Thailand", "German", "Dual Audio", "Multi Audio"]    
        for lang in nb_languages:
            if lang.lower() in caption.lower():
                language += f"{lang}, "
        language = language.strip(", ") or "Unknown language"
        movie_name = await movie_name_format(file_name)    
        if movie_name in processed_movies:
            return 
        processed_movies.add(movie_name)    
        poster_url = await get_imdb(movie_name)    
        search_movie = movie_name.replace(" ", '-')
        movie_update_channel = await db.movies_update_channel_id()    
        btn = [[            
            InlineKeyboardButton('⚠️ Get Sample Files 📂', url=f'https://t.me/{temp.U_NAME}?start=getfile-{search_movie}')
        ],[
            InlineKeyboardButton('🔮 Click Here To Search 🔍', url=f'https://t.me/{temp.U_NAME}?start=getfile-{search_movie}')
        ]]
        reply_markup = InlineKeyboardMarkup(btn)
        if poster_url:
            await bot.send_message(movie_update_channel if movie_update_channel else MOVIE_UPDATE_CHANNEL, 
                                 text=f"<b>🎬 Title : {movie_name}\n🌟 Rating : {rating} / 10\n🎭 Genres : {genres}\n💿 Quality : {quality}\n\n<blockquote>🔊 Audio : {language}</blockquote></b>", reply_markup=reply_markup)
        else:
            no_poster = "https://envs.sh/pTu.jpg"
            await bot.send_message(movie_update_channel if movie_update_channel else MOVIE_UPDATE_CHANNEL, 
                                 text=f"<b>🎬 Title : {movie_name}\n🌟 Rating : {rating} / 10\n🎭 Genres : {genres}\n💿 Quality : {quality}\n\n<blockquote>🔊 Audio : {language}</blockquote></b>", reply_markup=reply_markup)  
    except Exception as e:
        print('Failed to send movie update. Error - ', e)
        await bot.send_message(LOG_CHANNEL, f'Failed to send movie update. Error - {e}')
    
  
