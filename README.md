# magick
magick is a discord self-bot written in python which aims to add the following features:
- message purging
- reaction spam, reaction removing
- chat exports via https://github.com/tyrrrz/discordchatexporter
- timed message sending
- timed message deletion
- discord hidden deletion (hiding deleted messages from vencord)
- message spam
- AI

**please note that using self-bots and modified clients is against the Discord Terms of Service and may result in you being terminated off their platform. I do not condone the usage of this software.**

## usage instructions
1. clone the repository and cd into it:
`git clone https://github.com/carbonicality/magick`
`cd magick`

2. install dependencies (ensure you have python)
`pip install discord.py-self aiohttp`

3. run the script
`python main.py`

4. enter your discord token[1]

5. select your operating system

6. enter a hackclub AI API key if needed (you can change the endpoint in main.py)

[1] - please note that we do not store or maliciously use your discord token. however, it is still a risk to use your discord token. please be cautious and ensure you know what you're doing.

## commands
### messaging
- sb!purge <amount>: deletes your own messages using the provided limit (default 500 if unprovided)
- sb!spam <count> <phrase>: sends a specific message multiple times based on the count
- sb!msgsend <HH:MM> <message>: sends a message at a specific time
- sb!msgdelete <HH:MM> <msgId>: delete a specific message at a specific time using the message id

### reactions
- sb!react <count> <emoji>: reacts to a specified number of recent messages in the channel with the chosen emoji
- sb!removereacts <limit> <emoji>: removes all reactions placed by the current user for a specific emoji and a specific amount of messages dictated by limit and emoji

### utilities
- sb!export <date>: uses DiscordChatExporter to export all messages until a specific date
- sb!sdelete <msgId>: deletes a message silently (i.e doesn't show up on Vencord) for the provided message id.
- sb!ai <prompt>: asks the AI (gemini 3 flash preview) the provided prompt. by default uses the hack club AI endpoint.

## customisability
this tool is designed to be customisable, so in main.py, you can change the prefix, default purge limit and deletion delay in the 3 top variables in lines 9 to 11:
`PREFIX = "sb!"`
`PURGE_LIMIT = 500`
`DEL_DELAY = 0.2`