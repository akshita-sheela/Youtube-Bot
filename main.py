import discord
from discord.ext import commands
import os
from youtube_dl import YoutubeDL
from discord.flags import alias_flag_value

client = commands.Bot(command_prefix = "!")

@client.event
async def on_ready():
  print ("bot be ready yall")


def initialize(self,client):
  self.client= client
    #Basically this is going to determine if the music is playing or not
  self.is_playing = False

  #This list is going to keep track of the music that is supposed to be playing in the queue
  #Its a 2d Array containing [song,channel]
  self.music_queue= []
  self.YDL_OPTIONS = {'format':'bestaudio', 'nonplaylist':'True'}
  self.FFMPEG_OPTIONS = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options':'-vn'}

  self.vc = ""

#defining a utility function to serch for the urls on the internet
def search_yt(self,item):
  #this is getting the imported youtubedl library in the format specified by ydl_options and giving is a short name as ydl
  with YoutubeDL(self.YDL_OPTIONS) as ydl: 
    #info is getting the urls of the item we wanted
    #info = url
    try: 
      info = ydl.extract_info("ytsearch:%s" % item, download=False)['enteries'][0]
    except Exception:
      return False
  #we are storing the title and the url in the music_queue list
  return {'source': info['formats'][0]['url'],'title':info['title']}

#Once a song is finised, this function will look into the music_queue list and check if there are anyother song and then continue to play them 
def play_next(self):
  #if there are any songs in the queue 
  if len(self.music_queue)>0:
    #the status of if it's playing would be true
    self.is_playing= True

    #this is getting the url of the of the first song 
    #source is from the dictionary ??
    m_url = self.music_queue[0][0]['source']

    #this removes the first song from the queue
    self.music_queue.pop(0)

    #this is playing the first song from the m_url
    #recursion occurs because if there isn't a nother 
    self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
  else: 
    self.isplaying = False

#because this is based upon requests and callback this would be a async function

async def play_music(self): 
  if len(self.is_playing)>0:
    self.is_playing=True

    m_url= self.music_queue[0][0]['source']

    #make sure that the bot is connected to the voice channel
    #is it is not connected then we want to connect to the channel 
    #we store the channel in the second paramenter in the music queue so we can use that 
    if self.vc == ""  or not self.vc.is_connected(): 
      #we are connecting the bot the the musicqueue
      #???
      self.vc ==  await self.music_queue[0][1].connect
    else: 
      #if we are already connected but the user is in a different channel, then we need to move the bot to that channel
      self.vc == await self.bot.move_to(self.music_queue[0][1])

      #removing the first element from the music queue
      self.music_queue.pop(0)

      self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())

  else: 
    self.is_playing = False

@commands.command(alias= "play")
#ctx is the content of the channel
#args is storing the music that the user wants
async def play(self,ctx,*args):
  query = "".join(args) #convert the argument into a string so we have read what music the user wants

  voice_channel= ctx.message.author.voice.channel #this showsin which voice channel the user is connected within

  if voice_channel == None: 
    print("Please connect to a channel")
  else: 
    song = self.search_yt(query)
    if type(song)==type(True):
      await ctx.send("Cannot download the song. Try again :/")
    else: 
      await ctx.send("Added to the queue :))")
      self.music_queue.append([song, voice_channel])

      if self.is_playing == False: 
        self.play_music();


@commands.command()

async def queue(self,ctx):

  retval = ""
  for i in range(0,len(self.music_queue)):
    retval = retval + self.music_queue[i][0]['title'] + "\n"

  print(retval)

  if retval !="":
    await ctx.send(retval)
  else:
    await ctx.send("No music in the queue")

@commands.command()

async def skip(self,ctx):

  if self.vc != "":
    self.vc.stop()
  else: 
    await self.play_music()

client.run(os.environ["TOKEN"])
