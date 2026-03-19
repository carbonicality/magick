import discord
import asyncio
import subprocess
from datetime import datetime
import os

#cfg
PREFIX = "sb!"
PURGE_LIMIT = 500
DEL_DELAY = 0.2

client = discord.Client()

def log(level, msg):
    print(f"[{level.upper()}] {msg}")

async def raw_sdelete(channel_id, msg_id, token):
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    payload = {
        "content":"** **",
        "nonce": str(message_id),
        "tts": False
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status==200:
                data = await resp.json()
                ghost_msg_id = data['id']
                await asyncio.sleep(0.2)
                return ghost_msg_id
    return None

@client.event
async def on_ready():
    log("info", f"logged in as {client.user} (ID: {client.user.id})")
    log("info", f"PREFIX: {PREFIX} - e.g {PREFIX}purge")
    log("info", f"PURGE_LIMIT val: {PURGE_LIMIT} messages")
    log("info", f"DEL_DELAY val: {DEL_DELAY}s")
    print()

@client.event
async def on_message(msg):
    if msg.author != client.user:
        return
    
    #purge, sb!purge
    if msg.content.lower().startswith(f"{PREFIX}purge"):
        parts = msg.content.split()
        if len(parts) > 1:
            try:
                limit = int(parts[1])
                if limit <= 0:
                    raise ValueError
            except ValueError:
                log("error", f"invalid arg '{parts[1]}' - must be a positive number")
                await msg.edit(content=f'invalid usage. try {PREFIX}purge or {PREFIX}purge <amount>')
                await asyncio.sleep(3)
                await msg.delete()
                return
        else:
            limit = PURGE_LIMIT
        channel = msg.channel
        log("info",f"purge started in #{channel.name} (ID: {channel.id}), scanning up to {limit} msgs")
        try:
            await msg.delete()
        except discord.HTTPException:
            pass
        deleted = 0
        failed = 0
        scanned = 0
        async for entry in channel.history(limit=limit):
            scanned+=1
            if entry.author == client.user:
                try:
                    await entry.delete()
                    deleted += 1
                    log("action",f"deleted msg {deleted}: \"{entry.content[:60]}{'...' if len(entry.content) > 60 else ''}\"")
                    await asyncio.sleep(DEL_DELAY)
                except discord.Forbidden:
                    failed += 1
                    log("error", f"hit discord.Forbidden on msg id {entry.id}, failed to delete")
                except discord.HTTPException as e:
                    failed += 1
                    log("warning", f"hit discord.HTTPException {entry.id}-{e}, failed to delete")
        print()
        log("info",f"purge complete! scanned {scanned}, deleted {deleted}, failed {failed}")
        print()
    
    #reaction spam, sb!react <count> <emoji>
    if msg.content.lower().startswith(f"{PREFIX}react"):
        parts = msg.content.split()
        if len(parts) < 3:
            await msg.edit(content=f"invalid usage. try {PREFIX}react <count> <emoji>")
            await asyncio.sleep(2)
            await msg.delete()
            return
        try:
            limit = int(parts[1])
            emoji = parts[2]
        except ValueError:
            await msg.edit(content="count must be a number.")
            return
        try:
            await msg.delete()
        except:
            pass
        log("info",f"reacting to {limit} messages with {emoji} in #{msg.channel.name}")
        count = 0
        async for entry in msg.channel.history(limit = limit):
            try:
                await entry.add_reaction(emoji)
                count += 1
                log("action",f"reacted to msg {count}/{limit}")
                await asyncio.sleep(DEL_DELAY)
            except discord.Forbidden:
                log("error",f"hit discord.Forbidden on msg id {entry.id}, failed to react")
                break
            except discord.HTTPException as e:
                log("warning", f"hit discord.HTTPException {entry.id}-{e}, failed to react")
                await asyncio.sleep(1)
                continue
        log("info",f"finished reacting to {count} msgs.")
    
    #reaction remover, sb!removereacts
    if msg.content.lower().startswith(f"{PREFIX}removereacts"):
        parts = msg.content.split()
        limit = PURGE_LIMIT
        emoji = None
        for part in parts[1:]:
            try:
                limit = int(part)
            except ValueError:
                emoji = part
        channel = msg.channel
        log("info",f"removing {'all' if not emoji else emoji} reactions in last {limit} msgs in #{channel.name}")
        try:
            await msg.delete()
        except discord.HTTPException:
            pass
        count = 0
        failed = 0
        async for entry in channel.history(limit=limit):
            try:
                if emoji:
                    await entry.remove_reaction(emoji,client.user)
                else:
                    for reaction in entry.reactions:
                        await reaction.remove(client.user)
                        await asyncio.sleep(0.1)
                count += 1
                log("action",f"cleared reactions on msg {count}: \"{entry.content[:60]}{'...' if len(entry.content) > 60 else ''}\"")
                await asyncio.sleep(DEL_DELAY)
            except discord.Forbidden:
                failed += 1
                log("error", f"hit discord.Forbidden on msg id {entry.id}")
            except discord.HTTPException as e:
                failed += 1
                log("warning",f"hit discord.HTTPException on {entry.id}-{e}")
        print()
        log("info",f"successfully cleared reactions on {count} msgs, failed {failed}")
        print()

    #chat export, sb!export
    if msg.content.lower().startswith(f"{PREFIX}export"):
        parts = msg.content.split()
        channel_id = msg.channel.id
        os.makedirs("exports",exist_ok=True)
        cmd = [
            "./DiscordChatExporterMac/DiscordChatExporter.Cli", # eventually i will add inputs for which os you want to use. for now, add your own discordchatexporter cli and change the file path if needed
            "export",
            "-t", TOKEN,
            "-c", str(channel_id),
            "-f", "HtmlDark",
            "-o", "exports/"
        ]
        if len(parts) > 1:
            try:
                limit = int(parts[1])
                cmd += ["--limit",str(limit)]
            except ValueError:
                log("error",f"invalid arg '{parts[1]}'")
                return
        log("info",f"exporting #{msg.channel.name}...")
        try:
            await msg.delete()
        except discord.HTTPException:
            pass
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(cmd,capture_output=True,text=True)
        )
        if result.returncode == 0:
            log("info",f"export complete, saved to exports/")
        else:
            log("error",f"export failed, {result.stderr.strip()}")
    
    #timed messages, sb!msgsend
    if msg.content.lower().startswith(f"{PREFIX}msgsend"):
        parts = msg.content.split(maxsplit=2)
        if len(parts) < 3:
            await msg.edit(content=f"invalid usage. try {PREFIX}msgsend <HH:MM> <message>")
            await asyncio.sleep(3)
            await msg.delete()
            return
        try:
            send_time = datetime.strptime(parts[1],"%H:%M").replace(
                year=datetime.now().year,
                month=datetime.now().month,
                day=datetime.now().day
            )
        except ValueError:
            await msg.edit(content="invalid time format, use HH:MM e.g 14:30")
            await asyncio.sleep(3)
            await msg.delete()
            return
        text = parts[2]
        channel = msg.channel
        now = datetime.now()
        delay = (send_time - now).total_seconds()
        if delay < 0:
            await msg.edit(content="that time has already passed today!")
            await asyncio.sleep(3)
            await msg.delete()
            return
        log("info",f"scheduled message in #{channel.name} at {parts[1]} ({int(delay)}s from now)")
        await msg.delete()
        await asyncio.sleep(delay)
        await channel.send(text)
        log("info",f"sent scheduled msg: \"{text[:60]}\"")
    
    #timed message delete, sb!msgdelete
    if msg.content.lower().startswith(f"{PREFIX}msgdelete"):
        parts = msg.content.split()
        if len(parts) < 3:
            await msg.edit(content=f"invalid usage. try {PREFIX}msgdelete <HH:MM> <msgId>")
            await asyncio.sleep(3)
            await msg.delete()
            return
        try:
            delete_time = datetime.strptime(parts[1],"%H:%M").replace(
                year=datetime.now().year,
                month=datetime.now().month,
                day=datetime.now().day
            )
            message_id=int(parts[2])
        except ValueError:
            await msg.edit(content="invalid time format. use HH:MM e.g 14:30")
            await asyncio.sleep(3)
            await msg.delete()
            return
        now = datetime.now()
        delay = (delete_time-now).total_seconds()
        if delay <0:
            await msg.edit(content="that time has already passed today!")
            await asyncio.sleep(3)
            await msg.delete()
            return
        channel = msg.channel
        log("info",f"scheduled delete of msg {message_id} at {parts[1]} ({int(delay)}s from now)")
        await msg.delete()
        await asyncio.sleep(delay)
        try:
            target = await channel.fetch_message(message_id)
            await target.delete()
            log("info",f"deleted scheduled message {message_id}")
        except discord.NotFound:
            log("error", f"message {message_id} not found")
        except discord.Forbidden:
            log("error", f"hit discord.Forbidden, can't delete msg {message_id}")
        except discord.HTTPException as e:
            log("error", f"hit discord.HTTPException-{e}")
    
    #silent delete, sb!sdelete
    if msg.content.lower().startswith(f"{PREFIX}sdelete"):
        parts = msg.content.split()
        if len(parts) <2:
            return
        target_id = parts[1]
        channel_id = msg.channel.id
        log("action",f"attempting silent delete on {target_id}")
        await msg.delete()
        ghost_id = await raw_silent_delete(channel_id, target_id, TOKEN)
        if ghost_id:
            try:
                orig_msg = await msg.channel.fetch_message(int(target_id))
                await orig_msg.delete()
                ghost_msg = await msg.channel.fetch_message(int(ghost_id))
                await ghost_msg.delete()
                log("info","silent delete successful.")
            except Exception as e:
                log("error",f"cleanup failed, {e}")
    
    #spam, sb!spam <count> <phrase>
    if msg.content.lower().startswith(f"{PREFIX}spam"):
        parts = msg.content.split(maxsplit=2)
        if len(parts) < 3:
            await msg.edit(content=f"invalid usage. try {PREFIX}spam <count> <phrase>")
            await asyncio.sleep(2)
            await msg.delete()
            return
        try:
            count = int(parts[1])
            phrase = parts[2]
        except ValueError:
            await msg.edit(content="count must be a number!")
            await asyncio.sleep(2)
            await msg.delete()
            return
        try:
            await msg.delete()
        except:
            pass
        log("info",f"spamming '{phrase[:30]}...' {count} times in #{msg.channel.name}")
        for i in range(count):
            try:
                await msg.channel.send(phrase)
                log("action",f"sent msg {i+1}/{count}")
                await asyncio.sleep(DEL_DELAY)
            except discord.Forbidden:
                log("error", "hit discord.Forbidden, failed to send messages here")
                break
            except discord.HTTPException as e:
                log("warning", f"hit discord.HTTPException-{e}")
                await asyncio.sleep(2)
        log("info",f"finished spamming {count} times!")

if __name__=='__main__':
    print("welcome to magick!")
    print("----------------------")
    TOKEN = input("enter discord token > ").strip()
    if not TOKEN:
        log("error","no token entered. exiting...")
        exit(1)
    print()
    client.run(TOKEN)
