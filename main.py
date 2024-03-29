# A Starboard bot for Discord

# Import dependencies 
import disnake # needed for controlling access to discord
from disnake.ext import commands # needed for controlling slash commands
import json # needed for parsing config file

class starboatOptions(): # define custom options class
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

class starboatClient(commands.InteractionBot): # define custom client class
    async def on_ready(self): # define listener behavior for bot ready notifications
        try:
            options.channel = await client.fetch_channel(options.channel) # fetch Channel object from client and store in options object
            for role in options.channel.guild.roles:
                if str(role.id) == options.manRole: options.manRole = role; break # if found role, fetch Role object from guild and store in options object
            options.channel.guild.roles.index(options.manRole) # index role, if not found will throw error
        except BaseException as err:
            print(f"Error transforming channel or role ID to channel, check your config file!\n{err=}")
            exit(1)
        else:
            print(f'Logged on as {self.user}!') # log bot readiness to console

    async def on_message(self, message: disnake.Message): # define listener behavior for new messages
        if (message.author == self.user): print(f'===== Message Sent =====\n{message.content}') # log bot message to console

    async def on_raw_reaction_add(self, payload: disnake.RawReactionActionEvent): # define listener behavior for new reaction event (need raw method to capture all reactions, not just cached messages)
        if (options.arcEmote == payload.emoji or options.manEmote == payload.emoji): # check for equality between the emojis defined in the config and the message's emoji
            canChannel = await self.fetch_channel(payload.channel_id) # get channel of message
            canMessage = await canChannel.fetch_message(payload.message_id) # get message object
            
            reacts = canMessage.reactions # store array of reactions for looping
            ignoreMessage, forceArchive = True, False
            for react in reacts: # search raction array
                if (str(react.emoji) == str(options.arcEmote) and react.count >= options.minReacts): ignoreMessage = False # exit if have not met reaction count
                if (str(react.emoji) == str(options.manEmote)): # check if emoji is equal to manual override emoji
                    async for user in react.users(): # search members who reacted with emoji
                        user = await canMessage.guild.fetch_member(user.id) # transform user into Member object
                        try: 
                            user.roles.index(options.manRole) # attempt to find role 
                        except ValueError:
                            pass # if value error raised, user did not have role, therefore do not unignore message
                        else:
                            forceArchive = True # unignore message since override requested
                if (str(react.emoji) == str(options.confEmote)): ignoreMessage = True # exit if message already pinned


            if (ignoreMessage == True and forceArchive == False): return # exit if criteria not met

            arcContent = f"{canMessage.channel.mention} - {canMessage.created_at.astimezone().date()} - {canMessage.author.mention}\n" # build archive message (split for clarity)
            arcContent += f"{canMessage.content}"


            arcFiles = [] # create list for storing attachments
            for attachment in canMessage.attachments: # loop through attachments in image
                arcFiles.append(await attachment.to_file()) # add file form of attachment to list

            buttonView = disnake.ui.View() # build view nessecary to hold button
            button = disnake.ui.Button(style=disnake.ButtonStyle.link, label="Jump to Message", url=canMessage.jump_url) # build jump button
            buttonView.add_item(button) # add button to view

            await options.channel.send(content=arcContent, files=arcFiles, view=buttonView) # send message to archive channel
            await canMessage.add_reaction(options.confEmote) # react to message confirming addition to archive


try:
    intents = disnake.Intents.default() # load intents class
    intents.message_content = True # ensure nessecary intents

    client = starboatClient(intents=intents) # build client
except BaseException as err:
    print(f"Error loading intents, did disnake install correctly?\n{err=}") # Print exception in case of failure to load
    exit(1)

try:
    options = starboatOptions("./configFile") # build options
except BaseException as err:
    print(f"Error generating configuration, double-check your configFile!\n{err=}") # Print exception in case of failure to build options
    exit(1)


@client.slash_command(name="upload_screenshot", description="Add file to message") # inform system we are registering a new command
async def uploadScreenshot(interaction, message_id, image: disnake.Attachment): # define new command
    """
    Add a screenshot to an archive post

    Parameters
    ----------
    message_id: ID of archive message to be edited
    image: Screenshot to attach to message
    """
    try:
        interaction.author.roles.index(options.manRole) # check for permissions
    except ValueError: # if ValueError thrown, does not have role
        await interaction.response.send_message(content="You don't have permission to do that", delete_after=5) # inform user they do not have permissions
        return
    except:
        print(f"An error has occured during the execution of upload_screenshot: \n{err.text=}\n{err.code=}\n{err.status=}\n{err.response=}\n{err.args=}\n{err=}") # print error to console
        await interaction.response.send_message(content=f"Uh oh, An error has occured `{err.code=}`") # inform user of failure
        return
        

    try:
        message = await options.channel.fetch_message(message_id) # find requested Message object
        await message.edit(file=await image.to_file()) # upload Attachment as a File
    except disnake.HTTPException as err:
        print(f"An error has occured during the execution of upload_screenshot: \n{err.text=}\n{err.code=}\n{err.status=}\n{err.response=}\n{err.args=}\n{err=}") # print error to console
        await interaction.response.send_message(content=f"Uh oh! An error has occured - Check your message ID!", delete_after=5) # inform user of failure
    except:
        print(f"An error has occured during the execution of upload_screenshot: \n{err.text=}\n{err.code=}\n{err.status=}\n{err.response=}\n{err.args=}\n{err=}") # print error to console
        await interaction.response.send_message(content=f"Uh oh, An error has occured `{err.code=}`") # inform user of failure
    else:
        await interaction.response.send_message(content="Success!", delete_after=5) # Inform user of completetion


@client.slash_command(name="remove_attachments", description=" Remove attachments from a message") # inform system we are registering a new command
async def clearAttachments(interaction, message_id): # define new command
    """
    Remove all attachments from an archive post

    Parameters
    ----------
    message_id: ID of archive message to be edited
    """
    try:
        interaction.author.roles.index(options.manRole) # check for permissions
    except ValueError: # if ValueError thrown, does not have role
        await interaction.response.send_message(content="You don't have permission to do that", delete_after=5) # inform user they do not have permissions
    except:
        print(f"An error has occured during the execution of remove_attachments: \n{err.text=}\n{err.code=}\n{err.status=}\n{err.response=}\n{err.args=}\n{err=}") # print error to console
        await interaction.response.send_message(content=f"Uh oh, An error has occured `{err.code=}`") # inform user of failure

    try:
        message = await options.channel.fetch_message(message_id) # find requested Message object
        await message.edit(attachments=None) # remove attachments from Message
    except disnake.HTTPException as err:
        print(f"An error has occured during the execution of remove_attachments: \n{err.text=}\n{err.code=}\n{err.status=}\n{err.response=}\n{err.args=}\n{err=}") # print error to console
        await interaction.response.send_message(content=f"Uh oh! An error has occured - Check your message ID!", delete_after=5) # inform user of failure
    except:
        print(f"An error has occured during the execution of remove_attachments: \n{err.text=}\n{err.code=}\n{err.status=}\n{err.response=}\n{err.args=}\n{err=}") # print error to console
        await interaction.response.send_message(content=f"Uh oh, An error has occured `{err.code=}`") # inform user of failure
    else:
        await interaction.response.send_message(content="Success!", delete_after=5) # Inform user of completetion

client.run(options.token) # run client

