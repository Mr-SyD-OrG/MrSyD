from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest
from database.users_chats_db import db
from info import ADMINS, SYD_URI, SYD_NAME, AUTH_CHANNEL

from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest

from motor.motor_asyncio import AsyncIOMotorClient


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
from pyrogram.errors import UserNotParticipant
from pyrogram import enums

async def is_rq_subscribed(bot, query, group_id):
    user_id = query.from_user.id

    # Step 1: Find channel linked to this group
    group_doc = await force_db.col.find_one({"group_id": group_id})
    if not group_doc:
        return True  # No force sub set for this group, allow access

    channel_id = group_doc.get("channel_id")
    user_list = group_doc.get("users", [])

    # Step 2: Check if user already recorded
    if user_id in user_list:
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

from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired, PeerIdInvalid, RPCError
from pyrogram.types import ChatInviteLink

@Client.on_message(filters.command("setforce"))
async def set_force_channel(client: Client, message: Message):
    if message.chat.type == "private":
        await message.reply("ᴘʟᴇᴀꜱᴇ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ᴀ ɢʀᴏᴜᴘ ᴡʜᴇʀᴇ ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀᴅᴍɪɴ.")
        return

    group_id = message.chat.id
    user_id = message.from_user.id

    # Check if user is an admin
    try:
        member = await client.get_chat_member(group_id, user_id)
        if member.status not in ("administrator", "creator"):
            await message.reply("ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ꜱᴇᴛ ᴛʜᴇ ꜰᴏʀᴄᴇ ꜱᴜʙꜱᴄʀɪʙᴇ ᴄʜᴀɴɴᴇʟ.")
            return
    except ChatAdminRequired:
        await message.reply("ɪ ɴᴇᴇᴅ ᴀᴅᴍɪɴ ʀɪɢʜᴛꜱ ᴛᴏ ᴄʜᴇᴄᴋ ᴀᴅᴍɪɴꜱ.")
        return

    await message.reply_text("ꜱᴇɴᴅ ᴛʜᴇ ʟᴀꜱᴛ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ʏᴏᴜʀ ꜰᴏʀᴄᴇ ꜱᴜʙꜱᴄʀɪʙᴇ ᴄʜᴀɴɴᴇʟ (ᴍᴀᴋᴇ ꜱᴜʀᴇ ɪ ᴀᴍ ᴀɴ ᴀᴅᴍɪɴ ᴛʜᴇʀᴇ).")

    try:
        response = await client.ask(
            chat_id=group_id,
            filters=filters.forwarded & filters.user(user_id),
            timeout=60
        )
    except Exception:
        await message.reply("⛔ ᴛɪᴍᴇᴏᴜᴛ. ᴄᴀɴᴄᴇʟᴇᴅ.")
        return

    if not response.forward_from_chat:
        await message.reply("❌ ᴘʟᴇᴀꜱᴇ ꜰᴏʀᴡᴀʀᴅ ᴀ ᴍᴇꜱꜱᴀɢᴇ ꜰʀᴏᴍ ᴀ ᴄʜᴀɴɴᴇʟ.")
        return

    channel = response.forward_from_chat
    channel_id = channel.id

    # Check if bot has permission to create invite link
    try:
        await client.create_chat_invite_link(
            chat_id=channel_id,
            creates_join_request=True,
            name=f"TestPerm_{group_id}"
        )
    except ChatAdminRequired:
        await message.reply("❌ ɪ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴀᴛ ᴄʜᴀɴɴᴇʟ ᴡɪᴛʜ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴄʀᴇᴀᴛᴇ ɪɴᴠɪᴛᴇ ʟɪɴᴋꜱ.")
        return
    except RPCError as e:
        await message.reply(f"⚠️ ᴇʀʀᴏʀ: {e}")
        return

    # All checks passed — store channel for group
    await force_db.set_group_channel(group_id, channel_id)
    await message.reply(f"✅ ꜱᴇᴛ ꜰᴏʀᴄᴇ ꜱᴜʙ ᴄʜᴀɴɴᴇʟ ᴛᴏ `{channel_id}`.")

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
