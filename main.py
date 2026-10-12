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
# تأكد أن هذا الرابط المباشر للصورة تعمل بشكل صحيح ويمكن فتحه في المتصفح
BASE_IMAGE_URL = (
    "https://r2.erweima.ai/ai_image/46472330f3124e5ca07e94239111fb82.png"
)


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
    await send_dynamic_welcome(channel, member)


@bot.tree.command(name="تجربة", description="تجربة شكل رسالة الترحيب والصورة")
@app_commands.checks.has_permissions(administrator=True)
async def test_welcome_slash(interaction: discord.Interaction):
  await interaction.response.defer(thinking=True)

  channel = bot.get_channel(WELCOME_CHANNEL_ID)
  if channel is None:
    channel = interaction.channel

  await send_dynamic_welcome(channel, interaction.user)
  await interaction.followup.send(
      "تم ارسال رسالة التجربة بنجاح! ✅", ephemeral=True
  )


async def send_dynamic_welcome(channel, member):
  temp_filename = f"welcome_{member.id}.png"
  try:
    # 1. تحميل الصورة الأساسية في كل مرة لضمان عدم تلفها
    base_response = requests.get(BASE_IMAGE_URL, timeout=10)
    if base_response.status_code != 200:
      raise Exception("فشل تحميل الصورة الأساسية من الرابط")
    base_image = Image.open(BytesIO(base_response.content)).convert("RGBA")

    # 2. تحميل صورة بروفايل العضو
    avatar_url = member.display_avatar.replace(size=256, format="png").url
    avatar_response = requests.get(avatar_url, timeout=10)
    avatar_img = Image.open(BytesIO(avatar_response.content)).convert("RGBA")

    # 3. قص الصورة على شكل دائرة
    mask = Image.new("L", avatar_img.size, 0)
    draw_mask = Image.Draw(mask)
    draw_mask.ellipse((0, 0) + avatar_img.size, fill=255)

    output = Image.new("RGBA", avatar_img.size, (0, 0, 0, 0))
    output.paste(avatar_img, (0, 0), mask=mask)

    avatar_resized = output.resize((305, 305), Image.Resampling.LANCZOS)

    # 4. دمج صورة العضو في الإحداثيات المحددة
    position = (523, 120)
    working_image = base_image.copy()
    working_image.paste(avatar_resized, position, avatar_resized)

    # 5. حفظ الصورة المؤقتة
    working_image.save(temp_filename)

    # 6. النص الترحيمي
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

    file = discord.File(temp_filename)
    embed = discord.Embed(
        title="🎉 مرحباً بك في السيرفر!",
        description=welcome_description,
        color=discord.Color.blue(),
    )
    embed.set_image(url=f"attachment://{temp_filename}")
    embed.set_footer(text=f"رقم العضو: {member.id} | ترحيب تفاعلي")

    await channel.send(embed=embed, file=file)

  except Exception as e:
    print(f"خطأ تفصيلي في معالجة الصورة: {e}")
    # إرسال رسالة توضح سبب الخطأ بدقة لتسهيل الحل
    await channel.send(
        f"مرحباً بك {member.mention}! (حدث خطأ في معالجة الصورة: {str(e)})"
    )

  finally:
    # تنظيف الملف المؤقت لكي لا يمتلئ السيرفر
    if os.path.exists(temp_filename):
      try:
        os.remove(temp_filename)
      except:
        pass


TOKEN = os.environ.get("DISCORD_TOKEN")
if TOKEN:
  bot.run(TOKEN)
else:
  print("خطأ: لم يتم العثور على توكن البوت.")
    
