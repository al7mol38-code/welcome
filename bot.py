import os
import discord
from discord.ext import commands
from PIL import Image
import requests
from io import BytesIO
import asyncio

# إعدادات البوت
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# آيدي روم الترحيب والتجربة
WELCOME_CHANNEL_ID = 1533469148493906002
# رابط الصورة الأساسية التي صممناها
BASE_IMAGE_URL = "https://r2.erweima.ai/ai_image/46472330f3124e5ca07e94239111fb82.png"

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح باسم: {bot.user.name}")
    # تحميل الصورة الأساسية مسبقاً لتسريع العملية
    try:
        response = requests.get(BASE_IMAGE_URL)
        global base_image
        base_image = Image.open(BytesIO(response.content)).convert("RGBA")
        print("تم تحميل الصورة الأساسية بنجاح.")
    except Exception as e:
        print(f"خطأ في تحميل الصورة الأساسية: {e}")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel is not None:
        await send_dynamic_welcome(channel, member)

@bot.command(name="تجربة")
@commands.has_permissions(administrator=True)
async def test_welcome(ctx):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel is None:
        channel = ctx.channel
    
    await ctx.send("جاري إنشاء صورة الترحيب الديناميكية...")
    await send_dynamic_welcome(channel, ctx.author)
    try:
        await ctx.message.delete()
    except:
        pass

async def send_dynamic_welcome(channel, member):
    try:
        # 1. تحميل صورة بروفايل العضو
        avatar_url = member.display_avatar.replace(size=256, format="png").url
        response = requests.get(avatar_url)
        avatar_img = Image.open(BytesIO(response.content)).convert("RGBA")

        # 2. إنشاء قناع دائري (Mask) لقص صورة العضو
        mask = Image.new('L', avatar_img.size, 0)
        draw_mask = Image.Draw(mask)
        draw_mask.ellipse((0, 0) + avatar_img.size, fill=255)
        
        # تطبيق القناع على صورة البروفايل
        output = Image.new("RGBA", avatar_img.size, (0,0,0,0))
        output.paste(avatar_img, (0,0), mask=mask)
        
        # تغيير حجم الصورة الدائرية لتناسب الدائرة الزرقاء في التصميم (حوالي 300x300 بكسل)
        avatar_resized = output.resize((305, 305), Image.Resampling.LANCZOS)

        # 3. دمج صورة العضو داخل نسخة من الصورة الأساسية
        # إحداثيات مركز الدائرة الزرقاء في التصميم هي تقريباً (670, 270)
        # سنقوم بضبط الإحداثيات (x, y) لتكون في المنتصف تماماً
        position = (523, 120) # هذه الإحداثيات تم حسابها لتناسب الصورة الأصلية

        # إنشاء نسخة عمل من الصورة الأساسية
        working_image = base_image.copy()
        working_image.paste(avatar_resized, position, avatar_resized)

        # 4. حفظ الصورة الناتجة محلياً
        temp_filename = f"welcome_{member.id}.png"
        working_image.save(temp_filename)

        # 5. تجهيز النص الترحيمي
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

        # 6. إرسال الرسالة مع الصورة المدمجة
        file = discord.File(temp_filename)
        embed = discord.Embed(
            title="🎉 مرحباً بك في السيرفر!",
            description=welcome_description,
            color=discord.Color.blue()
        )
        embed.set_image(url=f"attachment://{temp_filename}")
        # إزالة الصورة المصغرة لأن الصورة الرئيسية تغني عنها
        # embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"رقم العضو: {member.id} | تم تفعيل الصورة الديناميكية")

        await channel.send(embed=embed, file=file)

        # 7. تنظيف الملف المؤقت
        await asyncio.sleep(1) # تأخير بسيط لضمان إرسال الملف قبل حذفه
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    except Exception as e:
        print(f"خطأ في إنشاء الترحيب الديناميكي: {e}")
        # في حال حدوث خطأ، أرسل الرسالة النصية على الأقل
        await channel.send(f"مرحباً بك {member.mention}! (حدث خطأ في تحميل الصورة الديناميكية)")

# تشغيل البوت
TOKEN = os.environ.get("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("خطأ: لم يتم العثور على توكن البوت.")
