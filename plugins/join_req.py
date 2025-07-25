from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest, Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.users_chats_db import db
from info import ADMINS, SYD_URI, SYD_NAME, AUTH_CHANNEL
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import ChatAdminRequired, RPCError
import asyncio
from pyrogram.errors import UserNotParticipant
from utils import temp

@Client.on_message(filters.command("delforce"))
async def delforce_handler(client, message: Message):
    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply_text(
            "⚠️ ᴘʟᴇᴀꜱᴇ ᴜꜱᴇ ᴛʜɪꜱ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ...",
        )

    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in (enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR):
        return await message.reply_text("⛔ ʏᴏᴜ ᴍᴜꜱᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

    chat_id = message.chat.id
    existing = await force_db.col.find_one({"group_id": chat_id})
    if not existing:
        return await message.reply_text("⚠️ ɴᴏ ꜰᴏʀᴄᴇ ꜱᴜʙ ɪꜱ ꜱᴇᴛ ꜰᴏʀ ᴛʜɪꜱ ɢʀᴏᴜᴘ. ᴜꜱᴇ /setforce ᴛᴏ ꜱᴇᴛ.")

    await force_db.col.delete_one({"group_id": chat_id})
    await message.reply_text("ꜰᴏʀᴄᴇ ꜱᴜʙ ꜱᴇᴛᴛɪɴɢ ꜰᴏʀ ᴛʜɪꜱ ɢʀᴏᴜᴘ ʜᴀꜱ ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ. ✅")

@Client.on_message(filters.command("seeforce"))
async def see_force_channel(client, message):
    if message.chat.type == enums.ChatType.PRIVATE:
        await message.reply("⚠️ ᴘʟᴇᴀꜱᴇ ᴜꜱᴇ ᴛʜɪꜱ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ...")
        return

    group_id = message.chat.id
    user_id = message.from_user.id
    if (await client.get_chat_member(message.chat.id, message.from_user.id)).status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]: return await message.reply("ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴀʟʟᴏᴡᴇᴅ.")

    channel_id = await force_db.get_channel_id(group_id)

    if not channel_id:
        await client.send_message(user_id, "❌ ɴᴏ ꜰᴏʀᴄᴇ ꜱᴜʙ ᴄʜᴀɴɴᴇʟ ꜱᴇᴛ ꜰᴏʀ ᴛʜɪꜱ ɢʀᴏᴜᴘ.")
        
        await message.reply("⚠️ ᴩʟᴇᴀꜱᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴩʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ")
        return

    try:
        chat = await client.get_chat(channel_id)
        invite = await client.create_chat_invite_link(
            channel_id,
           # creates_join_request=True,
            name=f"FS_{group_id}"
        )
    except ChatAdminRequired:
        await client.send_message(user_id, "❌ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴅᴍɪɴ ʀɪɢʜᴛꜱ ɪɴ ᴛʜᴇ ꜰᴏʀᴄᴇ ꜱᴜʙ ᴄʜᴀɴɴᴇʟ.")
        await message.reply("⚠️ ᴇʀʀᴏʀ: ᴩʟᴇᴀꜱᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴩʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ")
        return
    except Exception as e:
        await client.send_message(user_id, f"⚠️ ᴇʀʀᴏʀ: `{e}` \n ꜰᴏʀᴡᴀʀᴅ ɪᴛ ᴛᴏ @Syd_xyz ꜰᴏʀ ʜᴇʟᴩ.")
        await message.reply("⚠️ ᴇʀʀᴏʀ: ᴩʟᴇᴀꜱᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴩʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ")
        return

    text = (
        f"✅ **ꜰᴏʀᴄᴇ ꜱᴜʙ ᴄʜᴀɴɴᴇʟ ᴅᴇᴛᴀɪʟꜱ:**\n\n"
        f"**ɴᴀᴍᴇ**: {chat.title}\n"
        f"**ɪᴅ**: `{channel_id}`\n"
        f"**ɪɴᴠɪᴛᴇ**: [ᴄʟɪᴄᴋ ᴛᴏ ᴊᴏɪɴ]({invite.invite_link})"
    )

    try:
        await client.send_message(user_id, text, disable_web_page_preview=True)
        await message.reply("📩 ᴅᴇᴛᴀɪʟꜱ ꜱᴇɴᴛ ɪɴ ᴘᴇʀꜱᴏɴᴀʟ ᴄʜᴀᴛ.")
    except Exception:
        await message.reply("❌ ᴄᴏᴜʟᴅɴ'ᴛ ꜱᴇɴᴅ ᴍᴇꜱꜱᴀɢᴇ ɪɴ ᴘᴇʀꜱᴏɴᴀʟ ᴄʜᴀᴛ. ᴘʟᴇᴀꜱᴇ ꜱᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ꜰɪʀꜱᴛ.")

class Database:
    def __init__(self, uri: str, db_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.col = self.db.force_channels


    async def set_group_channel(self, group_id: int, channel_id: int):
        await self.col.update_one(
            {"group_id": group_id},
            {"$set": {"channel_id": channel_id, "users": []}},
            upsert=True
        )

    async def add_user(self, group_id: int, user_id: int):
        await self.col.update_one(
            {"group_id": group_id},
            {"$addToSet": {"users": user_id}},
            upsert=True
        )

    async def get_channel_id(self, group_id: int):
        doc = await self.col.find_one({"group_id": group_id})
        return doc.get("channel_id") if doc else None

    async def get_users(self, group_id: int):
        doc = await self.col.find_one({"group_id": group_id})
        return doc.get("users", []) if doc else []


@Client.on_chat_join_request()
async def handle_join_request(client: Client, message: ChatJoinRequest):
    user_id = message.from_user.id
    channel_id = message.chat.id  # The channel they're trying to join

    # Find which group (if any) uses this channel for force-sub
    group_doc = await force_db.col.find_one({"channel_id": channel_id})
    
    if not group_doc:
        return  # This channel is not linked to any group

    group_id = group_doc["group_id"]

    # Check if user already added (optional)
    if user_id not in group_doc.get("users", []):
        await force_db.add_user(group_id, user_id)

    # Optionally send message
    try:
        await client.send_message(
            user_id,
            "<b>ᴛʜᴀɴᴋꜱ ғᴏʀ ᴊᴏɪɴɪɴɢ! ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ <u>ᴄᴏɴᴛɪɴᴜᴇ</u> ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ ⚡</b>"
        )
    except Exception:
        pass


async def is_rq_subscribed(bot, query, group_id):
    user_id = query.from_user.id
    print(f"G: {group_id}")
    # Step 1: Find channel linked to this group
    group_doc = await force_db.col.find_one({"group_id": group_id})
    print(group_doc)
    if not group_doc:
        print("No group_doc found")
        return True  # No force sub set for this group, allow access

    channel_id = group_doc.get("channel_id")
    user_list = group_doc.get("users", [])

    # Step 2: Check if user already recorded
    if user_id in user_list:
        print("User already verified")
        return True

    # Step 3: Check membership in channel
    try:
        user = await bot.get_chat_member(channel_id, user_id)
    except UserNotParticipant:
        return False
    except Exception as e:
        logger.exception(e)
        return False
    else:
        if user.status != enums.ChatMemberStatus.BANNED:
            return True

    return False


# Step 1: When /setforce is used
@Client.on_message(filters.command("setforce"))
async def set_force_channel(client, message):
    if message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.reply("⚠️ ᴘʟᴇᴀꜱᴇ ᴜꜱᴇ ᴛʜɪꜱ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ...")

    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        return await message.reply("ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ꜱᴇᴛ ꜰᴏʀᴄᴇ ꜱᴜʙ.")

    temp.FORCE_WAIT[message.chat.id] = message.from_user.id

    m = await message.reply(
        "ꜰᴏʀᴡᴀʀᴅ ᴀ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ꜱᴇᴛ ᴀꜱ ꜰᴏʀᴄᴇ ꜱᴜʙ.\n"
        "<b>ɴᴏᴛᴇ: ꜰᴏʀᴡᴀʀᴅ ᴡɪᴛʜ ᴛᴀɢ</b>\n\nᴛɪᴍᴇᴏᴜᴛ ɪɴ 120ꜱ"
    )

    for _ in range(120):
        await asyncio.sleep(1)
        if message.chat.id not in temp.FORCE_WAIT:
            await m.delete()
            return  # silently quit if already set

    if message.chat.id in temp.FORCE_WAIT:
        del temp.FORCE_WAIT[message.chat.id]
        await m.delete()
        await message.reply("ᴛɪᴍᴇ-ᴏᴜᴛ ᴩʟᴇᴀꜱᴇ ꜱᴛᴀʀᴛ ᴀɢᴀɪɴ. /setforce")

        
        
    

    
# Step 2: In a general handler
@Client.on_message(filters.forwarded)
async def handle_forwarded(client, message):
    group_id = message.chat.id
    user_id = message.from_user.id

    if group_id not in temp.FORCE_WAIT:
        return

    if temp.FORCE_WAIT[group_id] != user_id:
        return

    if not message.forward_from_chat:
        return await message.reply("ꜰᴏʀᴡᴀʀᴅ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴀ ᴄʜᴀɴɴᴇʟ ᴏɴʟʏ.")
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
        return await message.reply("ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ꜱᴇᴛ ꜰᴏʀᴄᴇ ꜱᴜʙ.")

    channel = message.forward_from_chat

    try:
        await client.create_chat_invite_link(channel.id, creates_join_request=True)
    except Exception as e:
        return await message.reply(f"ᴄᴀɴ'ᴛ ᴄʀᴇᴀᴛᴇ ɪɴᴠɪᴛᴇ: {e}")

    await force_db.set_group_channel(group_id, channel.id)
    await message.reply(f"✅ ꜱᴇᴛ ꜰᴏʀᴄᴇ ꜱᴜʙ ᴄʜᴀɴɴᴇʟ: `{channel.id}`")
    del temp.FORCE_WAIT[group_id]
    await message.delete()
    
    await client.send_message(
        1733124290,
        f"New User Added Force: \n ᴜꜱᴇʀ ɪᴅ : {user_id} \n ɢʀᴏᴜᴩ ɪᴅ: {group_id} \n ꜱᴇᴛ ᴄʜᴀɴɴᴇʟ: {channel.id} \n#FSub",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("ᴍᴇꜱꜱᴀɢᴇ", user_id=user_id)]
            ]
        )
    )

@Client.on_chat_join_request(filters.chat(AUTH_CHANNEL))
async def join_reqs(client, message: ChatJoinRequest):
  if not await db.find_join_req(message.from_user.id):
    await db.add_join_req(message.from_user.id)
    try:
        await client.send_message(message.from_user.id, "<b> Tʜᴀɴᴋꜱ ɢᴏᴛ ᴏɴᴇ ᴩʟᴇᴀꜱᴇ <u>ᴄᴏɴᴛɪɴᴜᴇ... </u>⚡ </b>")
    except:
        pass

@Client.on_message(filters.command("delreq") & filters.private & filters.user(ADMINS))
async def del_requests(client, message):
    await db.del_join_req()    
    await message.reply("<b>⚙ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴄʜᴀɴɴᴇʟ ʟᴇғᴛ ᴜꜱᴇʀꜱ ᴅᴇʟᴇᴛᴇᴅ</b>")


force_db = Database(SYD_URI, SYD_NAME)
