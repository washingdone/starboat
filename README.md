# Starboat
A Custom Starboard Bot

## Features
- Allow all users to vote on messages to archive
- Allow members with a role to force an archive
- Allow members with a role to add attachments to an archive post
- Allow members with a role to remove attachments of an archive post
- Configurable channel, role, reactions, and threshold

------------------------------------------------------------------------------------------------------------------------------------------------------

# Permissions
## Application
- Oauth2 Method: In-app
- Oauth2 Scopes: bot, application.commands
- Bot Privileged Gateway Intents: Message Content Intent

## Bot User
- Read Messages
- Send Messages
- Embed Links
- Attach Files
- Read Message History
- Add Reactions

------------------------------------------------------------------------------------------------------------------------------------------------------

# Installation
Notes: The following instuctions assume Ubuntu
## Packages
#### system
Required: python-3, python3-venv
#### pip
Required: disnake

## Setup
```shell
python3 -m venv starboat
source starboat/bin/activate
pip install -U disnake
python3 main.py
```
