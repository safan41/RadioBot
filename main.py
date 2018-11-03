import os
import discord
from discord.ext import commands
from radiopy import Player
import urllib.request
client = discord.Client()
bot = commands.Bot(command_prefix=',', description='A Discord Radio Bot.')
bot.remove_command('help')

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Shrek meme bot thing", description="Very bot. So much nice. List of commands are:", color=0x33bd33)

    embed.add_field(name="?hello", value="Gives a nice greet message", inline=False)
    embed.add_field(name="?meme <meme>", value="Returns given meme information from knowyourmeme.com", inline=False)
    embed.add_field(name="?memereview <literally anything>", value="Returns a rating of anything basically", inline=False)
    embed.add_field(name="?ping", value="Returns ping", inline=False)
    embed.add_field(name="?compute <expression>", value="Solves simple Maths", inline=False)
    embed.add_field(name="?help", value="Gives this message", inline=False)
    embed.add_field(name="?top <subreddit>", value="Takes given subreddit and returns top of all time", inline=False)
    embed.add_field(name="?hot <subreddit>", value="Takes given subreddit and returns hot", inline=False)

    await ctx.send(embed=embed)
    await ctx.send("Any additional support for this bot can be found at @safan41#9134 and @ithinknotdumbo#5355's discord server: https://discord.gg/BAnCs4E")
@bot.command()
async def hello(ctx):
    await ctx.send('Hello {0.author.mention}'.format(ctx))

@bot.command()
async def peepee(ctx):
    await ctx.send('poopoo man')

@bot.command()
async def ping(ctx):
    await ctx.send(" :ping_pong: Pong! Ping: {}ms".format(round(bot.latency * 1000)))

@bot.command()
async def list(ctx):
    x = Player({}).print_list()
    await ctx.send(x)

if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('libopus.so')
 
class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player
 
    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)
 
class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())
 
    def is_playing(self):
        if self.voice is None or self.current is None:
            return False
 
        player = self.current.player
        return not player.is_done()
 
    @property
    def player(self):
        return self.current.player
 
    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()
 
    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)
 
    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, 'Now playing ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()
 
class Music:
    """Voice related commands.
 
    Works in multiple servers at once.
    """
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}
 
    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state
 
        return state
 
    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice
 
    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass
 
    @commands.command(name='connect', aliases=['join'])
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        """Connect to voice.
        Parameters
        ------------
        channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        This command also handles moving the bot to different channels.
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                await ctx.send('No channel to join. Please either specify a valid channel or join one.')

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except:
                await ctx.send(f'Moving to channel: <{channel}> timed out.')
        else:
            await channel.connect()
        await ctx.send(f'Connected to: **{channel}**', delete_after=20)
    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(query))

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

bot.add_cog(Music(bot))

bot.run(os.environ['TOKEN'])