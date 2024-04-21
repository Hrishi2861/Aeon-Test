from time import time
from quoters import Quote
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.filters import command, regex
from psutil import cpu_percent, virtual_memory, disk_usage
import asyncio
from bot import status_reply_dict_lock, download_dict, download_dict_lock, botStartTime, Interval, config_dict, bot
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import sendMessage, deleteMessage, one_minute_del, sendStatusMessage, update_all_messages
from bot.helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time, turn_page, setInterval, new_task
from bot.modules import images
@new_task
async def mirror_status(_, message):
    sticker_message = await message.reply_sticker("CAACAgIAAxkBAAEXzJtlezBU92o9SmsFleHxnuyQWpkHnQACogEAAjDUnRH1ZwABIuJAFVczBA")
    await asyncio.sleep(2)
    await sticker_message.delete()
    async with download_dict_lock:
        count = len(download_dict)

    if count == 0:
        currentTime = get_readable_time(time() - botStartTime)
        free = get_readable_file_size(disk_usage('/usr/src/app/downloads/').free)
        quote = Quote.print().split('―', 1)[0].strip().replace("“", "").replace("”", "")

        msg = f'<b>{quote} ❤️</b>\n\n'
        msg += f"<b><a href='https://t.me/JetMirror'>Pᴏᴡᴇʀᴇᴅ ʙʏ ᴊᴇᴛ-ᴍɪʀʀᴏʀ 🚀♥️</a></b>\n\n"
        msg += '<b>ᴜɴɪɴsᴛᴀʟʟ ᴛᴇʟᴇɢʀᴀᴍ ᴀɴᴅ ᴇɴᴊᴏʏ ʏᴏᴜʀ ʟɪғᴇ!!</b>\n\nɴᴏ ᴅᴏᴡɴʟᴏᴀᴅs ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ɪɴ ᴘʀᴏɢʀᴇss.\n'
        msg += f"\n<b>⌑ ʙᴏᴛ ᴜᴘᴛɪᴍᴇ</b>: {currentTime}"
        msg += f"\n<b>⌑ ғʀᴇᴇ ᴅɪsᴋ sᴘᴀᴄᴇ</b>: {free}"
        
        reply_message = await sendMessage(message, msg, photo='IMAGES')
        await deleteMessage(message)
        await one_minute_del(reply_message)
    else:
        await sendStatusMessage(message)
        await deleteMessage(message)
        async with status_reply_dict_lock:
            if Interval:
                Interval[0].cancel()
                Interval.clear()
                Interval.append(setInterval(1, update_all_messages))


@new_task
async def status_pages(_, query):
    await query.answer()
    data = query.data.split()
    if data[1] == "ref":
        await update_all_messages(True)
    else:
        await turn_page(data)


bot.add_handler(MessageHandler(mirror_status, filters=command(BotCommands.StatusCommand) & CustomFilters.authorized))
bot.add_handler(CallbackQueryHandler(status_pages, filters=regex("^status")))
