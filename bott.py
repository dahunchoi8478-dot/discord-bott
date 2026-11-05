
import os
import threading
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask

# -------------------------
# Render 웹서버
# -------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Discord Team Bot is running!"

def run_web():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# 웹서버 별도 실행
threading.Thread(target=run_web, daemon=True).start()


# -------------------------
# 팀 음성채널 설정
# -------------------------
TEAM_CHANNELS = [
    "빨간팀",
    "주황팀",
    "노란팀",
    "초록팀",
    "파란팀",
    "보라팀"
]


# -------------------------
# Discord 설정
# -------------------------
intents = discord.Intents.default()
intents.voice_states = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# -------------------------
# 명령어 등록
# -------------------------
@bot.event
async def setup_hook():

    print("봇 초기 설정 시작")

    try:
        guild_id = os.getenv("GUILD_ID")

        if guild_id:
            # 테스트 서버에 즉시 명령어 등록
            guild = discord.Object(id=int(guild_id))

            bot.tree.copy_global_to(guild=guild)

            synced = await bot.tree.sync(guild=guild)

            print(f"테스트 서버 명령어 등록 완료: {len(synced)}개")

        else:
            # 전체 서버에 명령어 등록
            synced = await bot.tree.sync()

            print(f"전역 명령어 등록 완료: {len(synced)}개")

    except Exception as e:
        print(f"명령어 등록 실패: {repr(e)}")


@bot.event
async def on_ready():
    print("==============================")
    print(f"봇 로그인 성공: {bot.user}")
    print(f"봇 ID: {bot.user.id}")
    print("디스코드 연결 완료")
    print("==============================")


# -------------------------
# /팀짜기 명령어
# -------------------------
@bot.tree.command(
    name="팀짜기",
    description="현재 팀 음성채널 접속 인원을 정리합니다."
)
@app_commands.guild_only()
async def team_list(interaction: discord.Interaction):

    guild = interaction.guild

    if guild is None:
        await interaction.response.send_message(
            "서버에서만 사용할 수 있습니다.",
            ephemeral=True
        )
        return

    result = []

    for team_name in TEAM_CHANNELS:

        members = []

        for channel in guild.voice_channels:

            if team_name in channel.name:

                for member in channel.members:

                    if not member.bot:
                        members.append(member.display_name)

        if members:
            result.append(" ".join(members))

    if result:
        message = "\n".join(result)
    else:
        message = "현재 접속 중인 인원이 없습니다."

    await interaction.response.send_message(
        message,
        allowed_mentions=discord.AllowedMentions.none()
    )


# -------------------------
# 봇 실행
# -------------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN이 설정되지 않았습니다.")

bot.run(TOKEN)
