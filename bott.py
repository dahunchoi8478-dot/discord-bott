import os
import discord
from discord import app_commands
from discord.ext import commands

# 📌 [추가] 렌더 무료 플랜 절전 방지를 위한 웹서버 코드
from flask import Flask
import threading

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# 봇 실행 전에 웹서버 켜기
keep_alive()

# 팀 음성채널 이름
TEAM_CHANNELS = [
    "빨간팀",
    "주황팀",
    "노란팀",
    "초록팀",
    "파란팀",
    "보라팀"
]

# 디스코드 권한 설정
intents = discord.Intents.default()
intents.voice_states = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# 봇 접속 및 명령어 등록
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"봇 로그인 완료: {bot.user}")
        print(f"명령어 등록 완료: {len(synced)}개")
    except Exception as e:
        print(f"명령어 등록 오류: {e}")


# /팀짜기 명령어
@bot.tree.command(
    name="팀짜기",
    description="현재 음성채널 접속 인원을 정리합니다."
)
@app_commands.guild_only()
async def team_list(interaction: discord.Interaction):

    guild = interaction.guild

    if guild is None:
        return

    result = []

    # 팀 순서대로 인원 확인
    for team_name in TEAM_CHANNELS:

        members = []

        for channel in guild.voice_channels:

            # 채널 이름에 팀 이름이 포함되어 있는지 확인
            if team_name in channel.name:

                # 현재 음성채널 접속자만 가져오기
                for member in channel.members:

                    # 봇 계정 제외
                    if not member.bot:
                        members.append(member.display_name)

        # 인원이 있는 팀만 출력
        if members:
            result.append(" ".join(members))

    # 최종 결과
    if result:
        message = "\n".join(result)
    else:
        message = "현재 접속 중인 인원이 없습니다."

    await interaction.response.send_message(
        message,
        allowed_mentions=discord.AllowedMentions.none()
    )


# 봇 실행
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("봇 토큰이 설정되지 않았습니다.")

bot.run(TOKEN)