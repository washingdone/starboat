# A Starboard bot for Discord

# Import dependencies
import disnake # needed for controlling access to discord
from disnake.ext import commands # needed for controlling slash commands
import json # needed for parsing config file

class starboatOptions(): # build custom options class
    def __init__(self, configPath): # define init behavior
        config = json.load(open(configPath)) # load config file as json object
        archiveEmote = config["archiveEmote"] # store archive emote in variable
        archiveEmote = disnake.PartialEmoji.from_str(archiveEmote) # transform emoji into PartialEmoji from discord class

        overrideEmote = config["overrideEmote"] # store maunal archive emote in variable
        overrideEmote = disnake.PartialEmoji.from_str(overrideEmote) # transform emoji into PartialEmoji from discord class
        
        confirmEmote = config["confirmEmote"] # store confirmation emote in variable
        confirmEmote = disnake.PartialEmoji.from_str(confirmEmote) # transform emoji into PartialEmoji from discord class
        
        self.token = config["token"] # store token in object
        self.arcEmote = archiveEmote # store archive emote in object
        self.manEmote = overrideEmote # store manual archive emote in object
        self.confEmote = confirmEmote # store confirmation emote in object
        self.channel = config["archiveChannel"] # store archive channel id in object to be transformed later
        self.manRole = config["overrideRole"] # store archivist role id in object to be transformed later
        self.minReacts = config["minReacts"] # store number of reacts required to archive message
        
        print(f"Initialized starboat options using {configPath}") # print completeion of init to console

class starboatClient(commands.InteractionBot): # build custom client class
    async def on_ready(self): # define listener behavior for bot ready notifications
        options.channel = await client.fetch_channel(options.channel) # fetch Channel object from client and store in options object
        options.manRole = options.channel.guild.get_role(options.manRole) # fetch Role object from guild and store in options object
        print(f'Logged on as {self.user}!') # log bot readiness to console

    async def on_message(self, message: disnake.Message): # define listener behavior for new messages
        if (message.author == self.user): print(f'===== Message Sent =====\n{message.content}') # log bot message to console

    async def on_raw_reaction_add(self, payload: disnake.RawReactionActionEvent): # define listener behavior for new reaction event (need raw method to capture all reactions, not just cached messages)
        if (options.arcEmote == payload.emoji or options.manEmote == payload.emoji): # check for equality between the emojis defined in the config and the message's emoji
            canChannel = await self.fetch_channel(payload.channel_id) # get channel of message
            canMessage = await canChannel.fetch_message(payload.message_id) # get message object
            
            reacts = canMessage.reactions # store array of reactions for looping
            ignoreMessage, forceArchive = False, False
            for react in reacts: # search raction array
                if (str(react.emoji) == str(options.arcEmote) and react.count != options.minReacts): ignoreMessage = True # exit if have not met reaction count
                if (str(react.emoji) == str(options.manEmote)): # check if emoji is equal to manual override emoji
                    async for user in react.users(): # search members who reacted with emoji
                        try:
                            if (user.roles.index(options.manRole)): forceArchive = True # unignore message since override requested
                        except:
                            continue # if failed we know is not Member type, so cannot be admin user              
                if (str(react.emoji) == str(options.confEmote)): ignoreMessage = True # exit if message already pinned


            if (ignoreMessage == True and forceArchive == False): return # exit if criteria not met

            arcContent = f"{canMessage.channel.mention} - {canMessage.created_at.date()} - {canMessage.author.mention}\n" # build archive message (split for clarity)
            arcContent += f"{canMessage.content}"

            buttonView = disnake.ui.View() # build view nessecary to hold button
            button = disnake.ui.Button(style=disnake.ButtonStyle.link, label="Jump to Message", url=canMessage.jump_url) # build jump button
            buttonView.add_item(button) # add button to view

            await options.channel.send(content=arcContent, view=buttonView) # send message to archive channel
            await canMessage.add_reaction(options.confEmote) # react to message confirming addition to archive


intents = disnake.Intents.default() # load intents class
intents.message_content = True # ensure nessecary intents

client = starboatClient(intents=intents) # define client
options = starboatOptions("./configFile") # define options

@client.slash_command(name="upload_screenshot", description="Add file to message") # inform system we are registering a new command
async def uploadScreenshot(interaction, message_id: str, image: disnake.Attachment): # define new command
    message = await options.channel.fetch_message(message_id) # find requested Message object
    await message.edit(attachments=None) # remove existing Attachments
    await message.edit(file=await image.to_file()) # upload Attachment as a File
    await interaction.response.send_message(content="Done!", delete_after=5) # Inform user of completetion
    

client.run(options.token) # run client

