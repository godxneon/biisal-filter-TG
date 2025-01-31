from utils import temp
from utils import get_poster
from info import POST_CHANNELS
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

#protect_content=True
#show_caption_above_media=True

@Client.on_message(filters.command('postfile'))
async def getfile(client, message):
    try:
        query = message.text.split(" ", 1) 
        if len(query) < 2:
            return await message.reply_text("<b>Usage :</b> /postfile {movie_name}\n\nExample : /postfile Money Heist")
        file_name = query[1].strip() 
        movie_details = await get_poster(file_name)
        
        if not movie_details:
            return await message.reply_text(f"No Results Found For {file_name} On IMDB.")

        poster = movie_details.get('poster', None)
        movie_title = movie_details.get('title', 'N/A')
        rating = movie_details.get('rating', 'N/A')
        genres = movie_details.get('genres', 'N/A')
        plot = movie_details.get('plot', 'N/A')
        year = movie_details.get('year', 'N/A')
        languages = movie_details.get('languages', 'N/A')
        
        custom_link = f"https://t.me/{temp.U_NAME}?start=getfile-{file_name.replace(' ', '-').lower()}"
        hackerjr_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("💥 𝖢𝗅𝗂𝖼𝗄 𝖧𝖾𝗋𝖾 𝖳𝗈 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽 💥", url=custom_link)
            ],[
            InlineKeyboardButton("⚡️ 𝖬𝖺𝗂𝗇 𝖢𝗁𝖺𝗇𝗇𝖾𝗅",  url=f"https://t.me/+d1RAYYmgtTI5YWJl"),
            InlineKeyboardButton("𝖬𝖺𝗂𝗇 𝖦𝗋𝗈𝗎𝗉 🔮",  url=f"https://t.me/KLMovieGroup")
        ]])
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("😊 Yes", callback_data=f"post_yes_{file_name}"),
             InlineKeyboardButton("🥺 No", callback_data=f"post_no_{file_name}")]
        ])
        
        if poster:
            await message.reply_photo(
                poster,
                caption=(
                    f"<b>🔖 Title: {movie_title}</b>\n"
                    f"<b>📆 Year: {year}</b>\n"
                    f"<b>🌐 Language: {languages}</b>\n"
                    f"<b>⭐️ Rating: {rating}/10</b>\n"
                    f"<b>🎬 Genres: {genres}</b>\n"
                    f"<b><blockquote expandable>📕 Story Line: {plot}</blockquote></b>\n"
                    "<b>🔥 Uploaded : @KLxFiles</b>"
                ),
                reply_markup=hackerjr_markup,
                has_spoiler=True,
                #show_caption_above_media=True,
                parse_mode=enums.ParseMode.HTML,
            )
            await message.reply_text("Do You Want To Post This Content On POST_CAHNNELS ?",
                reply_markup=reply_markup)
        else:
            await message.reply_text(
                (
                    f"<b>🔖 Title: {movie_title}</b>\n"
                    f"<b>📆 Year: {year}</b>\n"
                    f"<b>🌐 Language: {languages}</b>\n"
                    f"<b>⭐️ Rating: {rating}/10</b>\n"
                    f"<b>🎬 Genres: {genres}</b>\n"
                    f"<b><blockquote expandable>📕 Story Line: {plot}</blockquote></b>\n"
                    "<b>🔥 Uploaded : @KLxFiles</b>"
                ),
                reply_markup=hackerjr_markup,
                has_spoiler=True,
                #show_caption_above_media=True,
                parse_mode=enums.ParseMode.HTML,
            )
            await message.reply_text("Do You Want To Post This Content On POST_CAHNNEL ?",
                reply_markup=reply_markup)
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

@Client.on_callback_query(filters.regex(r'^post_(yes|no)_'))
async def post_to_channels(client, callback_query):
    action, file_name = callback_query.data.split('_')[1], callback_query.data.split('_')[2]
    
    if action == "yes":
        movie_details = await get_poster(file_name)
        
        if not movie_details:
            return await callback_query.message.reply_text(f"No Results Found For {file_name} On IMDB.")
        
        poster = movie_details.get('poster', None)
        movie_title = movie_details.get('title', 'N/A')
        rating = movie_details.get('rating', 'N/A')
        genres = movie_details.get('genres', 'N/A')
        plot = movie_details.get('plot', 'N/A')
        year = movie_details.get('year', 'N/A')
        languages = movie_details.get('languages', 'N/A')

        custom_link = f"https://t.me/{temp.U_NAME}?start=getfile-{file_name.replace(' ', '-').lower()}"
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("💥 𝖢𝗅𝗂𝖼𝗄 𝖧𝖾𝗋𝖾 𝖳𝗈 𝖣𝗈𝗐𝗇𝗅𝗈𝖺𝖽 💥", url=custom_link)
            ],[
            InlineKeyboardButton("⚡️ 𝖬𝖺𝗂𝗇 𝖢𝗁𝖺𝗇𝗇𝖾𝗅",  url=f"https://t.me/+d1RAYYmgtTI5YWJl"),
            InlineKeyboardButton("𝖬𝖺𝗂𝗇 𝖦𝗋𝗈𝗎𝗉 🔮",  url=f"https://t.me/KLMovieGroup")
        ]])
        for channel_id in POST_CHANNELS:
            try:
                if poster:
                    await client.send_photo( 
                        chat_id=channel_id,
                        photo=poster,
                        caption=(
                            f"<b>🔖 Title: {movie_title}</b>\n"
                            f"<b>📆 Year: {year}</b>\n"
                            f"<b>🌐 Language: {languages}</b>\n"
                            f"<b>⭐️ Rating: {rating}/10</b>\n"
                            f"<b>🎬 Genres: {genres}</b>\n"
                            f"<b><blockquote expandable>📕 Story Line: {plot}</blockquote></b>\n"
                            "<b>🔥 Uploaded: @KLxFiles</b>"
                        ),
                        reply_markup=reply_markup,
                        has_spoiler=True,
                        protect_content=True,
                        parse_mode=enums.ParseMode.HTML
                    )
                else:
                    await client.send_message(
                        chat_id=channel_id,
                        text=(
                            f"<b>🔖 Title: {movie_title}</b>\n"
                            f"<b>📆 Year: {year}</b>\n"
                            f"<b>🌐 Language: {languages}</b>\n"
                            f"<b>⭐️ Rating: {rating}/10</b>\n"
                            f"<b>🎬 Genres: {genres}</b>\n"
                            f"<b><blockquote expandable>📕 Story Line: {plot}</blockquote></b>\n"
                            "<b>🔥 Uploaded : @KLxFiles</b>"
                        ),
                        reply_markup=reply_markup,
                        has_spoiler=True,
                        protect_content=True,
                        parse_mode=enums.ParseMode.HTML
                    )
            except Exception as e:
                await callback_query.message.reply_text(f"Error Posting To Channel {channel_id}: {str(e)}")
        
        await callback_query.message.edit_text("Movie Details Successfully Posted To Channels.")
    
    elif action == "no":
        await callback_query.message.edit_text("Movie Details Will Not Be Posted To Channels.")

  
