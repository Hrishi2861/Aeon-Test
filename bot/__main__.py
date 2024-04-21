import platform
from time import time
from datetime import datetime
from sys import executable
from os import execl as osexecl
from asyncio import create_subprocess_exec, gather
from uuid import uuid4
from base64 import b64decode
from quoters import Quote
from html import escape
import asyncio
from cloudscraper import create_scraper
import asyncio
from requests import get as rget
from pytz import timezone
from bs4 import BeautifulSoup
from signal import signal, SIGINT
from aiofiles.os import path as aiopath, remove as aioremove
from aiofiles import open as aiopen
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, cpu_freq, virtual_memory, net_io_counters, boot_time
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.filters import command, private, regex
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot, config_dict, user_data, botStartTime, LOGGER, Interval, DATABASE_URL, QbInterval, scheduler, bot_name
from .helper.ext_utils.fs_utils import start_cleanup, clean_all, exit_clean_up
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time, cmd_exec, sync_to_async, set_commands, update_user_ldata, new_thread, new_task
from .helper.ext_utils.db_handler import DbManager
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.message_utils import sendMessage, editMessage, sendFile, deleteMessage, one_minute_del, five_minute_del
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.button_build import ButtonMaker
from .helper.listeners.aria2_listener import start_aria2_listener
from .modules import authorize, cancel_mirror, mirror_leech, status, torrent_search, torrent_select, ytdlp, rss, shell, eval, users_settings, bot_settings, speedtest, images, mediainfo, broadcast
from .helper.mirror_utils.gdrive_utils import count, delete, list, clone

@new_thread
async def stats(_, message):
    sticker_message = await message.reply_sticker("CAACAgIAAxkBAAEYonplzwrczhVu3I6HqPBzro3L2JU6YAACvAUAAj-VzAoTSKpoG9FPRjQE")
    await asyncio.sleep(2)
    await sticker_message.delete()
    total, used, free, disk = disk_usage('/')
    memory = virtual_memory()
    currentTime = get_readable_time(time() - botStartTime)
    osUptime = get_readable_time(time() - boot_time())
    cpuUsage = cpu_percent(interval=0.5)
    quote = Quote.print().split('―', 1)[0].strip().replace("“", "").replace("”", "")
    limit_mapping = {
        '🧲 Tᴏʀʀᴇɴᴛ'  : config_dict.get('TORRENT_LIMIT',  '∞'),
        '🟢 Gᴅʀɪᴠᴇ'   : config_dict.get('GDRIVE_LIMIT',   '∞'),
        '🔴 Yᴛᴅʟᴘ'    : config_dict.get('YTDLP_LIMIT',    '∞'),
        '🔗 Dɪʀᴇᴄᴛ'   : config_dict.get('DIRECT_LIMIT',   '∞'),
        '🚀 Lᴇᴇᴄʜ'    : config_dict.get('LEECH_LIMIT',    '∞'),
        '⚡️ Cʟᴏɴᴇ'     : config_dict.get('CLONE_LIMIT',    '∞'),
        'Ⓜ️ Mᴇɢᴀ'     : config_dict.get('MEGA_LIMIT',     '∞'),
        '👤 Usᴇʀ ᴛᴀsᴋ': config_dict.get('USER_MAX_TASKS', '∞')}
    system_info = f'<b>{quote}</b>\n\n\n'\
        f'<b>Sʏsᴛᴇᴍ sᴛᴀᴛs 🚀♥️</b>\n\n'\
        f'🤖 Bᴏᴛ ᴜᴘᴛɪᴍᴇ : {currentTime}\n'\
        f'🖥️ Sʏs ᴜᴘᴛɪᴍᴇ : {osUptime}\n'\
        f'⚡️ Cᴘᴜ ᴜsᴀɢᴇ  : {cpuUsage}%\n'\
        f'🧨 Rᴀᴍ ᴜsᴀɢᴇ  : {memory.percent}%\n'\
        f'💿 Dɪsᴋ ᴜsᴀɢᴇ : {disk}%\n'\
        f'🪫 Fʀᴇᴇ sᴘᴀᴄᴇ : {get_readable_file_size(free)}\n'\
        f'💯 Tᴏᴛᴀʟ sᴘᴀᴄᴇ: {get_readable_file_size(total)}\n\n'\
            
    limitations = f'<b>Lɪᴍɪᴛᴀᴛɪᴏɴs 🚀♥️</b>\n\n'
    
    for k, v in limit_mapping.items():
        if v == '':
            v = '∞'
        elif k = 'User task':
            v = f'{v}GB/Link'
        else:
            v = f'{v} Tasks/user'
        limitations += f' {k:<11}: {v}\n'

    stats = system_info + limitations
    reply_message = await sendMessage(message, stats, photo='IMAGES')
    await deleteMessage(message)
    await one_minute_del(reply_message)

@new_thread
async def start(client, message):
    sticker_message = await message.reply_sticker("CAACAgIAAxkBAAEXyPRledQ6luKt1QABSPMPi2s4rgH3xMUAAmkdAALpI4hJ8xCGgSybQv8zBA")
    await asyncio.sleep(2)
    await sticker_message.delete()
    buttons = ButtonMaker()
    reply_markup = buttons.build_menu(2)
    if len(message.command) > 1 and message.command[1] == "aeon":
        await deleteMessage(message)
    elif len(message.command) > 1 and message.command[1] == "pmc":
        await sendMessage(message, 'Bot started')
        await deleteMessage(message)
    elif len(message.command) > 1 and len(message.command[1]) == 36:
        userid = message.from_user.id
        input_token = message.command[1]
        if DATABASE_URL:
            stored_token = await DbManager().get_user_token(userid)
            if stored_token is None:
                return await sendMessage(message, '<b>Tʜɪs ᴛᴏᴋᴇɴ ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ!!</b>\n\nKɪɴᴅʟʏ ɢᴇɴᴇʀᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ.')
            if input_token != stored_token:
                return await sendMessage(message, '<b>Iɴᴠᴀʟɪᴅ ᴛᴏᴋᴇɴ!!</b>\n\nKɪɴᴅʟʏ ɢᴇɴᴇʀᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ.')
        if userid not in user_data:
            return await sendMessage(message, '<b>Tʜɪs ᴛᴏᴋᴇɴ ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ!!</b>\n\nKɪɴᴅʟʏ ɢᴇɴᴇʀᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ.')
        data = user_data[userid]
        if 'token' not in data or data['token'] != input_token:
            return await sendMessage(message, '<b>Tʜɪs ᴛᴏᴋᴇɴ ʜᴀs ᴀʟʀᴇᴀᴅʏ ʙᴇᴇɴ ᴜsᴇᴅ!!</b>\n\nKɪɴᴅʟʏ ɢᴇɴᴇʀᴀᴛᴇ ᴀ ɴᴇᴡ ᴏɴᴇ.')
        token = str(uuid4())
        token_time = time()
        data['token'] = token
        data['time'] = token_time
        user_data[userid].update(data)
        if DATABASE_URL:
            await DbManager().update_user_tdata(userid, token, token_time)
        msg = '<b>Yᴏᴜʀ ᴛᴏᴋᴇɴ ʜᴀs ʙᴇᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ ɢᴇɴᴇʀᴀᴛᴇᴅ!</b> 🚀♥️\n\n'
        msg += f'Iᴛ ᴡɪʟʟ ʙᴇ ᴠᴀʟɪᴅ ғᴏʀ {get_readable_time(int(config_dict["TOKEN_TIMEOUT"]), True)}'
        return await sendMessage(message, msg)
    elif await CustomFilters.authorized(client, message):
        help_command = f"/{BotCommands.HelpCommand}"
        start_string = f'This bot can mirror all your links|files|torrents to Google Drive or any rclone cloud or to telegram.\n<b>Type {help_command} to get a list of available commands</b>'
        await sendMessage(message, start_string, photo='IMAGES')
    else:
        await sendMessage(message, 'Yᴏᴜ Aʀᴇ Nᴏᴛ ᴀ Aᴜᴛʜᴏʀɪᴢᴇᴅ Usᴇʀ!\nYᴏᴜ Cᴀɴ Usᴇ Mᴇ ᴀᴛ <a href="https://telegram.me/JetMirror">ᴊᴇᴛ-ᴍɪʀʀᴏʀ🚀♥️</a>', photo='IMAGES')
    await DbManager().update_pm_users(message.from_user.id)


async def restart(client, message):
    sticker_message = await message.reply_sticker("CAACAgUAAxkBAAEXrSRlbwYlArKGw0lVGUGHquKMqbu3fQACLggAAmCIwVXm28BgWp1jmzME")
    await asyncio.sleep(2)
    await sticker_message.delete()
    restart_message = await sendMessage(message, 'Restarting...')
    if scheduler.running:
        scheduler.shutdown(wait=False)
    for interval in [QbInterval, Interval]:
        if interval:
            interval[0].cancel()
    await sync_to_async(clean_all)
    proc1 = await create_subprocess_exec('pkill', '-9', '-f', '-e', 'gunicorn|buffet|openstack|render|zcl')
    proc2 = await create_subprocess_exec('python3', 'update.py')
    await gather(proc1.wait(), proc2.wait())
    async with aiopen(".restartmsg", "w") as f:
        await f.write(f"{restart_message.chat.id}\n{restart_message.id}\n")
    osexecl(executable, executable, "-m", "bot")


async def ping(_, message):
    start_time = int(round(time() * 1000))
    reply = await sendMessage(message, 'Starting ping...')
    end_time = int(round(time() * 1000))
    value=(end_time - start_time)
    await editMessage(reply, f'{value} ms.')


@new_task
async def AeonCallback(_, query):
    message = query.message
    user_id = query.from_user.id
    data = query.data.split()
    if user_id != int(data[1]):
        return await query.answer(text="Tʜɪs ᴍᴇssᴀɢᴇ ɪs ɴᴏᴛ ʏᴏᴜʀ's!", show_alert=True)
    elif data[2] == "logdisplay":
        await query.answer()
        async with aiopen('log.txt', 'r') as f:
            logFileLines = (await f.read()).splitlines()
        def parseline(line):
            try:
                return "[" + line.split('] [', 1)[1]
            except IndexError:
                return line
        ind, Loglines = 1, ''
        try:
            while len(Loglines) <= 3500:
                Loglines = parseline(logFileLines[-ind]) + '\n' + Loglines
                if ind == len(logFileLines): 
                    break
                ind += 1
            startLine = f"<b>Showing last {ind} lines from log.txt:</b> \n\n----------<b>START LOG</b>----------\n\n"
            endLine = "\n----------<b>END LOG</b>----------"
            btn = ButtonMaker()
            btn.ibutton('Close', f'aeon {user_id} close')
            reply_message = await sendMessage(message, startLine + escape(Loglines) + endLine, btn.build_menu(1))
            await query.edit_message_reply_markup(None)
            await deleteMessage(message)
            await five_minute_del(reply_message)
        except Exception as err:
            LOGGER.error(f"TG Log Display : {str(err)}")
    elif data[2] == "webpaste":
        await query.answer()
        async with aiopen('log.txt', 'r') as f:
            logFile = await f.read()
        cget = create_scraper().request
        resp = cget('POST', 'https://spaceb.in/api/v1/documents', data={'content': logFile, 'extension': 'None'}).json()
        if resp['status'] == 201:
            btn = ButtonMaker()
            btn.ubutton('Web paste', f"https://spaceb.in/{resp['payload']['id']}")
            await query.edit_message_reply_markup(btn.build_menu(1))
        else:
        	  LOGGER.error(f"Web paste failed : {str(err)}")
    elif data[2] == "botpm":
        await query.answer(url=f"https://t.me/{bot_name}?start=aeon")
    elif data[2] == "pmc":
        await query.answer(url=f"https://t.me/{bot_name}?start=pmc")
    else:
        await query.answer()
        await deleteMessage(message)
    
@new_task
async def log(_, message):
    buttons = ButtonMaker()
    buttons.ibutton('Log display', f'aeon {message.from_user.id} logdisplay')
    buttons.ibutton('Web paste', f'aeon {message.from_user.id} webpaste')
    reply_message = await sendFile(message, 'log.txt', buttons=buttons.build_menu(1))
    await deleteMessage(message)
    await five_minute_del(reply_message)


help_string = f'''<b>NOTE: Try each command without any arguments to see more details.</b>

/{BotCommands.MirrorCommand[0]} - Start mirroring to Google Drive.
/{BotCommands.LeechCommand[0]} - Start leeching to Telegram.
/{BotCommands.YtdlCommand[0]} - Mirror links supported by yt-dlp.
/{BotCommands.YtdlLeechCommand[0]} - Leech links supported by yt-dlp.
/{BotCommands.CloneCommand[0]} - Copy files/folders to Google Drive.
/{BotCommands.CountCommand} - Count files/folders in Google Drive.
/{BotCommands.UserSetCommand[0]} - User settings.
/{BotCommands.BtSelectCommand} - Select files from torrents by gid or reply.
/{BotCommands.StopAllCommand[0]} - Cancel all [status] tasks.
/{BotCommands.ListCommand} - Search in Google Drive(s).
/{BotCommands.SearchCommand} - Search for torrents with API or plugins.
/{BotCommands.StatusCommand[0]} - Show status of all downloads.
/{BotCommands.StatsCommand[0]} - Show stats of the machine hosting the bot.
'''


@new_task
async def bot_help(client, message):
    reply_message = await sendMessage(message, help_string)
    await deleteMessage(message)
    await one_minute_del(reply_message)


async def restart_notification():
    if await aiopath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
    else:
        chat_id, msg_id = 0, 0
    if await aiopath.isfile(".restartmsg"):
        rmsg = 'Restarted Successfully!'
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=rmsg)
        except:
            pass
        await aioremove(".restartmsg")


async def main():
    await gather(start_cleanup(), torrent_search.initiate_search_tools(), restart_notification(), set_commands(bot))
    await sync_to_async(start_aria2_listener, wait=False)
    
    bot.add_handler(MessageHandler(start, filters=command(BotCommands.StartCommand)))
    bot.add_handler(MessageHandler(log, filters=command(BotCommands.LogCommand) & CustomFilters.sudo))
    bot.add_handler(MessageHandler(restart, filters=command(BotCommands.RestartCommand) & CustomFilters.sudo))
    bot.add_handler(MessageHandler(ping, filters=command(BotCommands.PingCommand) & CustomFilters.authorized))
    bot.add_handler(MessageHandler(bot_help, filters=command(BotCommands.HelpCommand) & CustomFilters.authorized))
    bot.add_handler(MessageHandler(stats, filters=command(BotCommands.StatsCommand) & CustomFilters.authorized))
    bot.add_handler(CallbackQueryHandler(AeonCallback, filters=regex(r'^aeon')))
    LOGGER.info("Bot Started!")
    signal(SIGINT, exit_clean_up)

bot.loop.run_until_complete(main())
bot.loop.run_forever()
