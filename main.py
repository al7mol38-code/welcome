import asyncio
import os
from io import BytesIO
import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw
import requests

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_CHANNEL_ID = 1533463896118001838
# تم استخدام رابط بديل ومضمون 100% لتجاوز حظر التحميل
BASE_IMAGE_URL = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1920&auto=format&fit=crop"

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

@bot.tree.command(name="تجربة", description="تجربة شكل رسالة الترحيب والدائرة")
@app_commands.checks.has_permissions(administrator=True)
async def test_welcome_slash(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel is None:
        channel = interaction.channel
        
    await send_dynamic_welcome(channel, interaction.user, interaction)

async def send_dynamic_welcome(channel, member, interaction=None):
    temp_filename = f"welcome_{member.id}.png"
    try:
        # إضافة ترويض (Headers) لكي لا ترفض بعض المواقع طلب البوت
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        base_response = requests.get(BASE_IMAGE_URL, headers=headers, timeout=15)
        if base_response.status_code != 200:
            raise Exception(f"فشل تحميل الصورة الأساسية (كود الخطأ: {base_response.status_code})")
        base_image = Image.open(BytesIO(base_response.content)).convert("RGBA")

        avatar_url = member.display_avatar.replace(size=256, format="png").url
        avatar_response = requests.get(avatar_url, headers=headers, timeout=10)
        if avatar_response.status_code != 200:
            raise Exception("فشل تحميل صورة بروفايل العضو")
            
        avatar_img = Image.open(BytesIO(avatar_response.content)).convert("RGBA")

        mask = Image.new("L", avatar_img.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0) + avatar_img.size, fill=255)

        output = Image.new("RGBA", avatar_img.size, (0, 0, 0, 0))
        output.paste(avatar_img, (0, 0), mask=mask)

        avatar_resized = output.resize((380, 380), Image.Resampling.LANCZOS)
        position = (650, 190)
        
        working_image = base_image.copy()
        working_image.paste(avatar_resized, position, avatar_resized)

        working_image.save(temp_filename)

        welcome_description = f"""### 🌟 حياك الله {member.mention} في سيرفرنا! 🌟

> **نورتنا يا بطل، نتمنى لك قضاء أمتع الأوقات معنا 🫡**

---

📌 **قوانين السيرفر الأساسية:** 
> 🛑 الرجاء قراءتها والالتزام بها تاماً: <#1533463893890957474>

📜 **قوانين الفارم:** 
> للشرح الكامل والتفصيلي: <#1550887906334482442>

📢 **أخبار السيرفر:** 
> تابع كل جديد من هنا: <#1533463982478856334>

🌸 **توثيق البنات:** 
> 『 <#1534515466733883392> 』 *(تحذير: أي تلاعب يعرضك للباند فوراً)*

🏆 **رومات الرانك:** 
> للانضمام والمنافسة: <#1534957492575010826>

🎧 **شرح دخول الروم:** 
> الخطوات بالتفصيل: <#1535922457536372786>

🛠️ **الدعم الفني والمساعدة:** 
> لأي سؤال أو استفسار، افتح تذكرة والإدارة ما تقصر معك: <#1533464055325528168>"""

        file = discord.File(temp_filename)
        embed = discord.Embed(
            title="🎉 أهلاً بك في Farm of Legends!",
            description=welcome_description,
            color=discord.Color.from_rgb(46, 204, 113)
        )
        embed.set_image(url=f"attachment://{temp_filename}")
        embed.set_footer(text=f"رقم العضو: {member.id} | Farm of Legends Bot", icon_url=bot.user.display_avatar.url)

        await channel.send(embed=embed, file=file)
        
        if interaction:
            await interaction.followup.send("تم ارسال رسالة التجربة بنجاح إلى الروم المخصص! ✅", ephemeral=True)

    except Exception as e:
        print(f"خطأ تفصيلي في معالجة الصورة: {e}")
        if interaction:
            try:
                await interaction.followup.send(f"حدث خطأ أثناء معالجة الصورة: {str(e)}", ephemeral=True)
            except:
                pass
        
    finally:
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
