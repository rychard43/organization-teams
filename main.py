import discord
import os
from discord.ext import commands
import random
from config import TOKEN_DISCORD

intents = discord.Intents.all()
intents.members = True
voice_channel_list = []
voiceChannel_1, voiceChannel_2 = None, None
members_alocados = []

channel_name1 = '🔵Equipe Azul'
channel_name2 = '🔴Equipe Vermelha'
channel_lobby = 'Lobby'

bot = commands.Bot(command_prefix='$', intents=intents)
TOKEM = TOKEN_DISCORD


def fetchVoiceChannels():
    global voiceChannel_1, voiceChannel_2
    global voice_channel_list
    for guild in bot.guilds:
        for channel in guild.voice_channels:
            voice_channel_list.append(channel)

    print("Lista canais de vooz:")
    [print(i, info) for i, info in enumerate(voice_channel_list)]

    for index, vc in enumerate(voice_channel_list):
        if vc.name == channel_name1:
            voiceChannel_1 = index
            print(f"Achou {channel_name1}")
        if vc.name == channel_name2:
            voiceChannel_2 = index
            print(f"Achou {channel_name2}")


@bot.command(name="alocar_times")
async def alocar_times(ctx, voice_channel: discord.VoiceChannel):
    members = voice_channel.members
    random.shuffle(members)

    if len(members) > 0:
        max_team_size = 5
        num_teams = (len(members) + max_team_size - 1) // max_team_size
        teams = [members[i * max_team_size:(i + 1) * max_team_size] for i in range(num_teams)]

        # move os times para os canais
        for i, team in enumerate(teams):
            channel_name = channel_name1 if i == 0 else channel_name2
            channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)
            if channel:
                for member in team:
                    await member.move_to(channel)
                    members_alocados.append(member)
            else:
                await ctx.send(
                    f"Não foi possível encontrar o canal {channel_name}. Certifique-se de que ele existe e tente novamente.")

        await ctx.send(f"{len(members)} membros foram divididos em {len(teams)} times.")

        # envia a lista de jogadores alocados dos dois times
        team1 = [member.name for member in teams[0]]
        team2 = [member.name for member in teams[1]]
        await ctx.send(f"{channel_name1}: {', '.join(team1)}\n{channel_name2} {', '.join(team2)}")
        members_alocados.clear()
    else:
        await ctx.send("Não há membros no canal de voz.")


@bot.command(name="voltar")
async def voltar(ctx, voice_channel: discord.VoiceChannel):
    if voice_channel is None:
        await ctx.send("Por favor, especifique um canal de voz para voltar os membros.")
        return

    if not isinstance(voice_channel, discord.VoiceChannel):
        await ctx.send("Por favor, especifique um canal de voz válido.")
        return

    for member in members_alocados:
        await member.move_to(voice_channel)


@bot.command(name="criar_salas",
             description="Create environment for bot to set up your homies in voice channels. (TYPE THIS COMMAND FIRST)")
async def criar_salas(ctx):
    guild = ctx.guild
    mbed = discord.Embed(title='Bad permission', description='Não pode cirar os canais.')
    if ctx.author.guild_permissions.manage_channels:
        await guild.create_voice_channel(name=channel_name1)
        await guild.create_voice_channel(name=channel_name2)
        await guild.create_voice_channel(name=channel_lobby)
        mbed = discord.Embed(title='Success',
                             description=f'Os canais de voz {channel_name1}, {channel_name2} e {channel_lobby} foram criados.')
        await ctx.send(embed=mbed)
        fetchVoiceChannels()
    else:
        await ctx.send("Sem permissões")


@bot.command(name='ajuda')
async def ajuda(ctx):
    embed = discord.Embed(title='Comandos disponíveis', description='Lista de comandos do bot',
                          color=discord.Color.green())

    embed.add_field(name='$criar_salas', value='Cria os canais de voz para alocar os times.', inline=False)
    embed.add_field(name='$alocar_times "<canal de voz>"',
                    value='Aloca os membros presentes no canal de voz em dois times. (Ex: $alocar_times "Sala do Sorteio")',
                    inline=False)
    embed.add_field(name='$voltar "<canal de voz>"',
                    value='Move os membros alocados de volta para o canal de voz especificado.(Ex: $voltar "Sala do Sorteio")',
                    inline=False)

    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    msg = f'''
  BOT NAME     {bot.user.name}  Rychard
  BOT ID       {bot.user.id}
  DIRECTORY    {os.path.abspath(os.getcwd())}
  '''
    print(msg)
    fetchVoiceChannels()
    await bot.change_presence(activity=discord.Game(name="$help"))


bot.run(TOKEM)
