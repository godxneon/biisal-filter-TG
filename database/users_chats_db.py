import datetime
import pytz
from motor.motor_asyncio import AsyncIOMotorClient
from info import SETTINGS, IS_PM_SEARCH, IS_SEND_MOVIE_UPDATE, DATABASE_NAME, DATABASE_URI
# from utils import get_seconds
client = AsyncIOMotorClient(DATABASE_URI)
mydb = client[DATABASE_NAME]
fsubs = client['fsubs']
class Database:
    default = SETTINGS.copy()
    def __init__(self):
        self.col = mydb.users
        self.grp = mydb.groups
        self.misc = mydb.misc
        self.users = mydb.uersz
        self.req = mydb.requests
        self.mGrp = mydb.mGrp
        self.pmMode = mydb.pmMode
        self.grp_and_ids = fsubs.grp_and_ids
        self.movies_update_channel = mydb.movies_update_channel
        self.botcol = mydb.botcol
    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            point = 0,
            ban_status=dict(
                is_banned=False,
                ban_reason=""
            )
        )

    async def get_settings(self, id):
        chat = await self.grp.find_one({'id':int(id)})
        if chat:
            return chat.get('settings', self.default)
        else:
            await self.grp.update_one({'id': int(id)}, {'$set': {'settings': self.default}} , upsert=True)
        return self.default

    async def find_join_req(self, id):
        return bool(await self.req.find_one({'id': id}))
        
    async def add_join_req(self, id):
        await self.req.insert_one({'id': id})

    async def del_join_req(self):
        await self.req.drop()

    def new_group(self, id, title):
        return dict(
            id = id,
            title = title,
            chat_status=dict(
                is_disabled=False,
                reason=""
            )
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
        
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def delete_chat(self, id):
        await self.grp.delete_many({'id': int(id)})
        
    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats
    
    async def add_chat(self, chat, title):
        chat = self.new_group(chat, title)
        await self.grp.insert_one(chat)

    async def get_chat(self, chat):
        chat = await self.grp.find_one({'id':int(chat)})
        return False if not chat else chat.get('chat_status')  

    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})   
    
    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count
    
    async def get_all_chats(self):
        return self.grp.find({})

    async def get_db_size(self):
        return (await mydb.command("dbstats"))['dataSize'] 

    async def get_user(self, user_id):
        user_data = await self.users.find_one({"id": user_id})
        return user_data
        
    async def update_user(self, user_data):
        await self.users.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)
        
    async def update_one(self, filter_query, update_data):
        try:
            result = await self.users.update_one(filter_query, update_data)
            return result.matched_count == 1
        except Exception as e:
            print(f"Error updating document: {e}")
            return False

    async def setFsub(self , grpID , fsubID):
        return await self.grp_and_ids.update_one({'grpID': grpID} , {'$set': {'grpID': grpID , "fsubID": fsubID}}, upsert=True)    
        
    async def getFsub(self , grpID):
        link = await self.grp_and_ids.find_one({"grpID": grpID})
        if link is not None:
            return link.get("fsubID")
        else:
            return None

    async def delFsub(self , grpID):
        result =  await self.grp_and_ids.delete_one({"grpID": grpID})
        if result.deleted_count != 0:
            return True
        else:
            return False

    async def get_pm_search_status(self, bot_id):
        bot = await self.botcol.find_one({'id': bot_id})
        if bot and bot.get('bot_pm_search'):
            return bot['bot_pm_search']
        else:
            return IS_PM_SEARCH

    async def update_pm_search_status(self, bot_id, enable):
        bot = await self.botcol.find_one({'id': int(bot_id)})
        if bot:
            await self.botcol.update_one({'id': int(bot_id)}, {'$set': {'bot_pm_search': enable}})
        else:
            await self.botcol.insert_one({'id': int(bot_id), 'bot_pm_search': enable})
            
    async def get_send_movie_update_status(self, bot_id):
        bot = await self.botcol.find_one({'id': bot_id})
        if bot and bot.get('movie_update_feature'):
            return bot['movie_update_feature']
        else:
            return IS_SEND_MOVIE_UPDATE

    async def update_send_movie_update_status(self, bot_id, enable):
        bot = await self.botcol.find_one({'id': int(bot_id)})
        if bot:
            await self.botcol.update_one({'id': int(bot_id)}, {'$set': {'movie_update_feature': enable}})
        else:
            await self.botcol.insert_one({'id': int(bot_id), 'movie_update_feature': enable})      

    async def movies_update_channel_id(self , id=None):
        if id is None:
            myLinks = await self.movies_update_channel.find_one({})
            if myLinks is not None:
                return myLinks.get("id")
            else:
                return None
        return await self.movies_update_channel.update_one({} , {'$set': {'id': id}} , upsert=True)
        
    async def del_movies_channel_id(self):
        try: 
            isDeleted = await self.movies_update_channel.delete_one({})
            if isDeleted.deleted_count > 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"Got err in db set : {e}")
            return False

db = Database()
