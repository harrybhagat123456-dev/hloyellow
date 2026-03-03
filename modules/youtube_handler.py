import os
import requests
import subprocess
import asyncio
import yt_dlp
from pytube import YouTube
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from vars import CREDIT, cookies_file_path, AUTH_USERS
import globals
from saini import sanitize_filename


async def cookies_handler(client: Client, m: Message):
    editable = await m.reply_text("**Please upload the YouTube Cookies file (.txt format).**")
    try:
        input_message: Message = await client.listen(m.chat.id)
        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await m.reply_text("Invalid file type. Please upload a .txt file.")
            return
        downloaded_path = await input_message.download()
        with open(downloaded_path, "r") as uploaded_file:
            cookies_content = uploaded_file.read()
        with open(cookies_file_path, "w") as target_file:
            target_file.write(cookies_content)
        await editable.delete()
        await input_message.delete()
        await m.reply_text("✅ Cookies updated successfully.\n📂 Saved in `youtube_cookies.txt`.")
    except Exception as e:
        await m.reply_text(f"__**Failed Reason**__\n<blockquote>{str(e)}</blockquote>")


async def getcookies_handler(client: Client, m: Message):
    try:
        await client.send_document(chat_id=m.chat.id, document=cookies_file_path, caption="Here is the `youtube_cookies.txt` file.")
    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")


async def ytm_handler(bot: Client, m: Message):
    globals.processing_request = True
    globals.cancel_requested = False
    editable = await m.reply_text("**Input Type**\n\n<blockquote><b>01 •Send me the .txt file containing YouTube links\n02 •Send Single link or Set of YouTube multiple links</b></blockquote>")
    input: Message = await bot.listen(editable.chat.id)
    if input.document and input.document.file_name.endswith(".txt"):
        x = await input.download()
        file_name, ext = os.path.splitext(os.path.basename(x))
        playlist_name = file_name.replace('_', ' ')
        try:
            with open(x, "r") as f:
                content = f.read()
            content = content.split("\n")
            links = []
            for i in content:
                links.append(i.split("://", 1))
            os.remove(x)
        except:
            await m.reply_text("**Invalid file input.**")
            os.remove(x)
            return

        await editable.edit(f"**•ᴛᴏᴛᴀʟ 🔗 ʟɪɴᴋs ғᴏᴜɴᴅ ᴀʀᴇ --__{len(links)}__--\n•sᴇɴᴅ ғʀᴏᴍ ᴡʜᴇʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ...")
        try:
            input0: Message = await bot.listen(editable.chat.id, timeout=20)
            raw_text = input0.text
            await input0.delete(True)
        except asyncio.TimeoutError:
            raw_text = '1'

        await editable.delete()
        arg = int(raw_text)
        count = int(raw_text)
        try:
            if raw_text == "1":
                playlist_message = await m.reply_text(f"<blockquote><b>⏯️Playlist : {playlist_name}</b></blockquote>")
                await bot.pin_chat_message(m.chat.id, playlist_message.id)
                message_id = playlist_message.id
                pinning_message_id = message_id + 1
                await bot.delete_messages(m.chat.id, pinning_message_id)
        except Exception as e:
            pass

    elif input.text:
        content = input.text.strip()
        content = content.split("\n")
        links = []
        for i in content:
            links.append(i.split("://", 1))
        count = 1
        arg = 1
        await editable.delete()
        await input.delete(True)
    else:
        await m.reply_text("**Invalid input. Send either a .txt file or YouTube links set**")
        return
    try:
        for i in range(arg-1, len(links)):
            if globals.cancel_requested:
                await m.reply_text("🚦**STOPPED**🚦")
                globals.processing_request = False
                globals.cancel_requested = False
                return
            link = links[i][1]

            if "youtube.com/embed/" in link or "youtube-nocookie.com/embed/" in link:
                video_id = link.split("/embed/")[1].split("?")[0].split("/")[0]
                Vxy = f"www.youtube.com/watch?v={video_id}"
            elif "youtu.be/" in link:
                Vxy = link
            else:
                Vxy = link

            if Vxy.startswith("http://") or Vxy.startswith("https://"):
                url = Vxy
            else:
                url = "https://" + Vxy

            try:
                cmd_title = f'yt-dlp --get-title --cookies {cookies_file_path} "{url}"'
                result = subprocess.run(cmd_title, shell=True, capture_output=True, text=True, timeout=10)

                if result.returncode == 0 and result.stdout.strip():
                    audio_title = result.stdout.strip()[:80]
                else:
                    audio_title = f"YouTube_Video_{count:03d}"
            except Exception as e:
                print(f"Title extraction error: {e}")
                audio_title = f"YouTube_Video_{count:03d}"

            audio_title = audio_title.replace("_", " ")
            name = f'{audio_title[:60]} {CREDIT}'
            name1 = f'{audio_title} {CREDIT}'

            clean_name = sanitize_filename(name)

            if "youtube.com" in url or "youtu.be" in url:
                prog = await m.reply_text(f"<i><b>Audio Downloading</b></i>\n<blockquote><b>{str(count).zfill(3)}) {name1}</b></blockquote>")

                output_template = f"{str(count).zfill(3)} {clean_name}"
                cmd = f'yt-dlp -x --audio-format mp3 --cookies {cookies_file_path} "{url}" -o "{output_template}.%(ext)s" -R 10 --fragment-retries 10'
                print(f"Running command: {cmd}")

                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                print(f"yt-dlp stdout: {result.stdout}")
                print(f"yt-dlp stderr: {result.stderr}")

                expected_file = f'{output_template}.mp3'
                if os.path.exists(expected_file):
                    await prog.delete(True)
                    print(f"File {expected_file} exists, attempting to send...")
                    try:
                        await bot.send_document(chat_id=m.chat.id, document=expected_file, caption=f'**🎵 Title : **[{str(count).zfill(3)}] - {name1}.mp3\n\n🔗**Video link** : {url}\n\n🌟** Extracted By **: {CREDIT}')
                        os.remove(expected_file)
                        count += 1
                    except Exception as e:
                        await m.reply_text(f'⚠️**Downloading Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {url}\n**Error** =>> {str(e)}', disable_web_page_preview=True)
                        count += 1
                else:
                    await prog.delete(True)
                    files_in_dir = os.listdir('.')
                    mp3_files = [f for f in files_in_dir if f.endswith('.mp3')]
                    print(f"Expected file: {expected_file}, Files in directory: {mp3_files}")
                    await m.reply_text(f'⚠️**Downloading Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {url}\n**File not found after download**\n**Expected:** `{expected_file}`', disable_web_page_preview=True)
                    count += 1

    except Exception as e:
        await m.reply_text(f"<b>Failed Reason:</b>\n<blockquote><b>{str(e)}</b></blockquote>")
    finally:
        await m.reply_text("<blockquote><b>All YouTube Music Download Successfully</b></blockquote>")


async def y2t_handler(bot: Client, message: Message):
    user_id = str(message.from_user.id)
    editable = await message.reply_text(f"<blockquote><b>Send YouTube Website/Playlist link for convert in .txt file</b></blockquote>")
    input_message: Message = await bot.listen(message.chat.id)
    youtube_link = input_message.text.strip()
    await input_message.delete(True)
    await editable.delete(True)

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'force_generic_extractor': True,
        'forcejson': True,
        'cookies': 'youtube_cookies.txt'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(youtube_link, download=False)
            if 'entries' in result:
                title = result.get('title', 'youtube_playlist')
            else:
                title = result.get('title', 'youtube_video')
        except yt_dlp.utils.DownloadError as e:
            await message.reply_text(f"<blockquote>{str(e)}</blockquote>")
            return

    videos = []
    if 'entries' in result:
        for entry in result['entries']:
            video_title = entry.get('title', 'No title')
            url = entry['url']
            videos.append(f"{video_title}: {url}")
    else:
        video_title = result.get('title', 'No title')
        url = result['url']
        videos.append(f"{video_title}: {url}")

    txt_file = os.path.join("downloads", f'{title}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)
    with open(txt_file, 'w') as f:
        f.write('\n'.join(videos))

    await message.reply_document(document=txt_file, caption=f'<a href="{youtube_link}">__**Click Here to Open Link**__</a>\n<blockquote>{title}.txt</blockquote>\n')
    os.remove(txt_file)


def register_youtube_handlers(bot):
    bot.on_message(filters.command("cookies") & filters.private)(cookies_handler)
    bot.on_message(filters.command("getcookies") & filters.private)(getcookies_handler)
    bot.on_message(filters.command(["ytm"]))(ytm_handler)
    bot.on_message(filters.command(["y2t"]))(y2t_handler)
