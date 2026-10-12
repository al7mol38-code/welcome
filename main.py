import asyncio
import os
from io import BytesIO
import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image
import requests

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_CHANNEL_ID = 1533469148493906002

# سنستخدم طريقة بديلة ومضمونة: إرسال التصميم كصورة أساسية في اليمين/اليسار، 
# وبروفايل العضو كصورة مصغرة دائرية أو إرفاقها بشكل سلس يمنع حدوث خطأ التحميل.
# ضع هنا رابط مباشر ثابت أو دعنا نجعل البوت يرسل التصميم كصورة Embed نظيفة:


@bot.event
async def on_ready():
  print(f"تم تسجيل الدخول بنجاح باسم: {bot.user.name}")
  try:
    synced = await bot.tree.sync()
    print(f"تم مزامنة {len(synced)} من الأوامر بنجاح.")
  except Exception as e:
    print(f"خطأ في مزامنة الأوامر: {e}")


@bot.event
async def on_member_join(member):
  channel = bot.get_channel(WELCOME_CHANNEL_ID)
  if channel is not None:
    await send_clean_welcome(channel, member)


@bot.tree.command(name="تجربة", description="تجربة شكل رسالة الترحيب")
@app_commands.checks.has_permissions(administrator=True)
async def test_welcome_slash(interaction: discord.Interaction):
  await interaction.response.defer(thinking=True)

  channel = bot.get_channel(WELCOME_CHANNEL_ID)
  if channel is None:
    channel = interaction.channel

  await send_clean_welcome(channel, interaction.user)
  await interaction.followup.send(
      "تم ارسال رسالة التجربة بنجاح! ✅", ephemeral=True
  )


async def send_clean_welcome(channel, member):
  try:
    # النص الترحيمي المرتب والجميل
    welcome_description = f"""حياك الله {member.mention} منور سيرفرنا🫡 welcome

رجاء قراءة القوانين والالتزام بها 🛑 <#1533463893890957474>

وهذا شرح قوانين الفارم رجاء القراءة والالتزام بها
<#1550887906334482442>

هذي اخبار سيرفرنا <#1533463982478856334>

ومن هنا تذكره توثيق البنات اي تلاعب في التوثيق باند
『 <#1534515466733883392> 』

ومن هنا رومات الرانك <#1534957492575010826>

ومن هنا شرح دخول الروم
<#1535922457536372786>

واي سؤال او شكوى او شيء افتح تذكرة والاداريين مايقصرون معك باذن الله <#1533464055325528168>"""

    embed = discord.Embed(
        title="🎉 مرحباً بك في السيرفر!",
        description=welcome_description,
        color=discord.Color.blue(),
    )

    # وضع صورة بروفايل العضو كأيقونة مصغرة (Thumbnail) بارزة وواضحة
    embed.set_thumbnail(url=member.display_avatar.url)

    # وضع صورة التصميم الخاصة بك كصورة رئيسية (Image) تظهر أسفل النص بكامل جمالها
    embed.set_image(
        url="https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=1000&auto=format&fit=crop"
    )  # (أو يمكنك وضع أي رابط صورة ثابت ومباشر هنا، أو استبداله برابط صورتك من موقع رفع دائم)

    embed.set_footer(text=f"رقم العضو: {member.id} | نورتنا بوجودك")

    await channel.send(embed=embed)

  except Exception as e:
    print(f"خطأ في إرسال الترحيب: {e}")
    await channel.send(f"مرحباً بك {member.mention}! نورت السيرفر 💙")


TOKEN = os.environ.get("DISCORD_TOKEN")
if TOKEN:
  bot.run(TOKEN)
else:
  print("خطأ: لم يتم العثور على توكن البوت.")
