import re
import logging
import asyncio
import importlib
from sys import argv
from pyrogram import idle
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import (
    AccessTokenExpired,
    AccessTokenInvalid,
)
from PROMUSIC.utils.database import get_assistant
from concurrent.futures import ThreadPoolExecutor
from config import API_ID, API_HASH
from PROMUSIC import app
from config import OWNER_ID
from PROMUSIC.misc import SUDOERS
from PROMUSIC.utils.database import get_assistant, clonebotdb
from PROMUSIC.utils.database.clonedb import has_user_cloned_any_bot
from config import LOGGER_ID, CLONE_LOGGER
import requests
from PROMUSIC.utils.decorators.language import language
from pyrogram.errors import PeerIdInvalid

from datetime import datetime
CLONES = set()

C_BOT_DESC = "Wᴀɴᴛ ᴀ ʙᴏᴛ ʟɪᴋᴇ ᴛʜɪs? Cʟᴏɴᴇ ɪᴛ ɴᴏᴡ! ✅\n\nVɪsɪᴛ: @Purvi_Music_Robot ᴛᴏ ɢᴇᴛ sᴛᴀʀᴛᴇᴅ!\n\n - Uᴘᴅᴀᴛᴇ: @PURVI_SUPPORT\n - Sᴜᴘᴘᴏʀᴛ: @PURVI_UPDATES"

C_BOT_COMMANDS = [
                {"command": "/start", "description": "sᴛᴀʀᴛs ᴛʜᴇ ᴍᴜsɪᴄ ʙᴏᴛ"},
                {"command": "/help", "description": "ɢᴇᴛ ʜᴇʟᴩ ᴍᴇɴᴜ ᴡɪᴛʜ ᴇxᴩʟᴀɴᴀᴛɪᴏɴ ᴏғ ᴄᴏᴍᴍᴀɴᴅs."},
                {"command": "/play", "description": "sᴛᴀʀᴛs sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴛʀᴀᴄᴋ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ."},
                {"command": "/pause", "description": "ᴩᴀᴜsᴇ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ."},
                {"command": "/resume", "description": "ʀᴇsᴜᴍᴇ ᴛʜᴇ ᴩᴀᴜsᴇᴅ sᴛʀᴇᴀᴍ."},
                {"command": "/skip", "description": "ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ ᴀɴᴅ sᴛᴀʀᴛ sᴛʀᴇᴀᴍɪɴɢ ᴛʜᴇ ɴᴇxᴛ ᴛʀᴀᴄᴋ ɪɴ ǫᴜᴇᴜᴇ."},
                {"command": "/end", "description": "ᴄʟᴇᴀʀs ᴛʜᴇ ǫᴜᴇᴜᴇ ᴀɴᴅ ᴇɴᴅ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴩʟᴀʏɪɴɢ sᴛʀᴇᴀᴍ."},
                {"command": "/ping", "description": "ᴛʜᴇ ᴩɪɴɢ ᴀɴᴅ sʏsᴛᴇᴍ sᴛᴀᴛs ᴏғ ᴛʜᴇ ʙᴏᴛ."},
                {"command": "/clone", "description": "ᴍᴀᴋᴇ ʏᴏᴜʀ ᴏᴡɴ ᴍᴜsɪᴄ ʙᴏᴛ"}

            ]


@app.on_message(filters.command("clone"))
@language
async def clone_txt(client, message, _):
    userbot = await get_assistant(message.chat.id)

    # check user has already clone bot ? -------
    userid = message.from_user.id
    has_already_cbot = await has_user_cloned_any_bot(userid)

    if has_already_cbot:
        if message.from_user.id != OWNER_ID:
            return await message.reply_text(_["C_B_H_0"])
    else:
        pass
    
    # check user has already clone bot ? -------

    if len(message.command) > 1:
        bot_token = message.text.split("/clone", 1)[1].strip()
        mi = await message.reply_text(_["C_B_H_2"])
        try:
            ai = Client(
                bot_token,
                API_ID,
                API_HASH,
                bot_token=bot_token,
                plugins=dict(root="PROMUSIC.cplugin"), 
            )
            await ai.start()
            bot = await ai.get_me()
            bot_users = await ai.get_users(bot.username)
            bot_id = bot_users.id
            c_b_owner_fname = message.from_user.first_name
            c_bot_owner = message.from_user.id

        except (AccessTokenExpired, AccessTokenInvalid):
            await mi.edit_text(_["C_B_H_3"])
            return
        except Exception as e:
            if "database is locked" in str(e).lower():
                await message.reply_text(_["C_B_H_4"])
            else:
                await mi.edit_text(f"An error occurred: {str(e)}")
            return

        # Proceed with the cloning process
        await mi.edit_text(_["C_B_H_5"])
        try:

            await app.send_message(
                CLONE_LOGGER, f"**#NewClonedBot**\n\n**Bᴏᴛ:- {bot.mention}**\n**Usᴇʀɴᴀᴍᴇ:** @{bot.username}\n**Bᴏᴛ ID :** `{bot_id}`\n\n**Oᴡɴᴇʀ : ** [{c_b_owner_fname}](tg://user?id={c_bot_owner})"
            )
            await userbot.send_message(bot.username, "/start")

            details = {
                "bot_id": bot.id,
                "is_bot": True,
                "user_id": message.from_user.id,
                "name": bot.first_name,
                "token": bot_token,
                "username": bot.username,
                "channel": "PURVI_SUPPORT",
                "support": "PURVI_UPDATES",
                "premium" : False,
                "Date" : False,
            }
            clonebotdb.insert_one(details)
            CLONES.add(bot.id)

            #set bot info ----------------------------
            def set_bot_commands():
                url = f"https://api.telegram.org/bot{bot_token}/setMyCommands"
                
                params = {"commands": C_BOT_COMMANDS}
                response = requests.post(url, json=params)
                print(response.json())

            set_bot_commands()

            # Set bot's "Description" AutoMatically On Every Restart
            def set_bot_desc():
                url = f"https://api.telegram.org/bot{bot_token}/setMyDescription"
                params = {"description": C_BOT_DESC}
                response = requests.post(url, data=params)
                if response.status_code == 200:
                    logging.info(f"Successfully updated Description for bot: {bot_token}")
                else:
                    logging.error(f"Failed to update Description: {response.text}")

            set_bot_desc()

            #set bot info ----------------------------

            await mi.edit_text(_["C_B_H_6"].format(bot.username))
        except BaseException as e:
            logging.exception("Error while cloning bot.")
            await mi.edit_text(
                f"⚠️ <b>ᴇʀʀᴏʀ:</b>\n\n<code>{e}</code>\n\n**ᴋɪɴᴅʟʏ ғᴏᴡᴀʀᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ @PURVI_UPDATES ᴛᴏ ɢᴇᴛ ᴀssɪsᴛᴀɴᴄᴇ**"
            )
    else:
        await message.reply_text(_["C_B_H_1"])


@app.on_message(
    filters.command(
        [
            "delbot",
            "rmbot",
            "delcloned",
            "delclone",
            "deleteclone",
            "removeclone",
            "cancelclone",
        ]
    )
)
@language
async def delete_cloned_bot(client, message, _):
    try:
        if len(message.command) < 2:
            await message.reply_text(_["C_B_H_8"])
            return

        bot_token = " ".join(message.command[1:])
        await message.reply_text(_["C_B_H_9"])

        cloned_bot = clonebotdb.find_one({"token": bot_token})
        if cloned_bot:
            clonebotdb.delete_one({"token": bot_token})
            CLONES.remove(cloned_bot["bot_id"])
            await message.reply_text(_["C_B_H_10"])
            await restart_bots() #temp
        else:
            await message.reply_text(_["C_B_H_11"])
    except Exception as e:
        await message.reply_text(_["C_B_H_12"])
        logging.exception(e)





@app.on_message(filters.command("delallclone") & filters.user(OWNER_ID))
@language
async def delete_all_cloned_bots(client, message, _):
    try:
        await message.reply_text(_["C_B_H_14"])

        # Delete all cloned bots from the database
        clonebotdb.delete_many({})

        # Clear the CLONES set
        CLONES.clear()

        await message.reply_text(_["C_B_H_15"])
    except Exception as e:
        await message.reply_text("An error occurred while deleting all cloned bots.")
        logging.exception(e)


@app.on_message(filters.command(["mybot", "mybots"], prefixes=["/", "."]))
@language
async def my_cloned_bots(client, message, _):
    try:
        user_id = message.from_user.id
        cloned_bots = list(clonebotdb.find({"user_id": user_id}))
        
        if not cloned_bots:
            await message.reply_text(_["C_B_H_16"])
            return
        
        total_clones = len(cloned_bots)
        text = f"**Yᴏᴜʀ Cʟᴏɴᴇᴅ Bᴏᴛs: {total_clones}**\n\n"
        
        for bot in cloned_bots:
            text += f"**Bᴏᴛ Nᴀᴍᴇs:** {bot['name']}\n"
            text += f"**Bᴏᴛ Usᴇʀɴᴀᴍᴇ:** @{bot['username']}\n\n"
        
        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("An error occurred while fetching your cloned bots.")


executor = ThreadPoolExecutor(max_workers=10)  # 10 bots at a time

def check_bot_token(bot_token):
    """Check if bot token is valid before starting."""
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    response = requests.get(url)
    return response.status_code == 200

def start_clone_bot(bot_token):
    """Start a bot in a separate thread."""
    if not check_bot_token(bot_token):
        logging.error(f"Invalid or expired token for bot: {bot_token}")
        return
    
    try:
        ai = Client(
            f"{bot_token}",
            API_ID,
            API_HASH,
            bot_token=bot_token,
            plugins=dict(root="PROMUSIC.cplugin"),
        )
        asyncio.run(ai.start())  # Running async function in a separate thread

        bot = asyncio.run(ai.get_me())
        CLONES.add(bot.id)

        logging.info(f"Started bot: {bot.username}")
    except Exception as e:
        logging.error(f"Error in starting bot {bot_token}: {e}")

async def restart_bots():
    """Restart all bots using threading."""
    global CLONES
    logging.info("Restarting all cloned bots...")

    bots = list(clonebotdb.find())
    bot_tokens = [bot["token"] for bot in bots]

    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(executor, start_clone_bot, token) for token in bot_tokens]

    await asyncio.gather(*tasks)

    await app.send_message(CLONE_LOGGER, "All Cloned Bots Started!")

@app.on_message(filters.command("cloned"))
@language
async def list_cloned_bots(client, message, _):
    try:
        cloned_bots = list(clonebotdb.find())
        if not cloned_bots:
            await message.reply_text("No bots have been cloned yet.")
            return

        total_clones = len(cloned_bots)
        text = f"**Tᴏᴛᴀʟ Cʟᴏɴᴇᴅ Bᴏᴛs: `{total_clones}`**\n\n"
        messages = []  # छोटे-छोटे मैसेज स्टोर करने के लिए लिस्ट

        for bot in cloned_bots:
            user_id = bot.get("user_id")
            if not user_id:
                bot_info = f"⚠️ **Bᴏᴛ ID:** `{bot['bot_id']}` - Owner ID not found.\n\n"
            else:
                try:
                    owner = await client.get_users(user_id)
                    owner_name = owner.first_name or "Unknown"
                    owner_profile_link = f"tg://user?id={user_id}"
                except PeerIdInvalid:
                    logging.warning(f"PeerIdInvalid for user_id: {user_id}")
                    owner_name = "❌ Invalid User"
                    owner_profile_link = "#"
                except Exception as err:
                    logging.exception(err)
                    owner_name = "⚠️ Error Fetching Owner"
                    owner_profile_link = "#"

                bot_info = (
                    f"**Bᴏᴛ ID:** `{bot['bot_id']}`\n"
                    f"**Bᴏᴛ Nᴀᴍᴇ:** {bot['name']}\n"
                    f"**Bᴏᴛ Usᴇʀɴᴀᴍᴇ:** @{bot['username']}\n"
                    f"**Oᴡɴᴇʀ:** [{owner_name}]({owner_profile_link})\n\n"
                )

            if len(text) + len(bot_info) > 4000:  # मैसेज लिमिट से पहले भेजें
                messages.append(text)
                text = ""

            text += bot_info

        messages.append(text)  # आखिरी बचे टेक्स्ट को लिस्ट में ऐड करें

        # छोटे-छोटे मैसेज भेजें
        for msg in messages:
            if msg.strip():  # अगर मैसेज खाली नहीं है
                await message.reply_text(msg)

    except Exception as e:
        logging.exception(e)
        await message.reply_text("An error occurred while listing cloned bots.")

#total clone
@app.on_message(filters.command("totalbots"))
@language
async def list_cloned_bots(client, message, _):
    try:
        cloned_bots = list(clonebotdb.find())
        if not cloned_bots:
            await message.reply_text("No bots have been cloned yet.")
            return

        total_clones = len(cloned_bots)
        text = f"**Tᴏᴛᴀʟ Cʟᴏɴᴇᴅ Bᴏᴛs: `{total_clones}`**\n\n"         

        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("An error occurred while listing cloned bots.")
