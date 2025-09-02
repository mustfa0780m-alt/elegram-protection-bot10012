import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.channels import GetParticipantRequest

# ===== إعدادات البوت من Config Vars =====
api_id = int(os.getenv("19544986"))
api_hash = os.getenv("83d3621e6be385938ba3618fa0f0b543")
bot_token = os.getenv("8426678140:AAG3721Hak7V0u_ACZOl2pQHzMgY7Udxk4k")
channel_link = os.getenv("@sutazz")  # ضع رابط القناة هنا كمتغير بيئة

client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

# المستخدمون المعلقون على الانضمام للقناة
pending_users = {}  # {user_id: chat_id}

# ===== حدث دخول عضو جديد للمجموعة =====
@client.on(events.ChatAction)
async def new_user(event):
    if event.user_joined or event.user_added:
        user = await event.get_user()
        chat = await event.get_chat()
        # إرسال رسالة تحذيرية
        await event.reply(f'عزيزي @{user.username if user.username else user.first_name} انضم الى قناة طـز {channel_link} ثم ارجع الينا نحن ننتظرك')
        # منع ارسال الرسائل
        await client.edit_permissions(chat.id, user.id, send_messages=False)
        # إضافة المستخدم لقائمة الانتظار
        pending_users[user.id] = chat.id

# ===== فحص القناة كل 10 ثواني =====
async def check_channel():
    while True:
        to_remove = []
        for user_id, chat_id in pending_users.items():
            try:
                participant = await client(GetParticipantRequest(channel=channel_link, user_id=user_id))
                if participant:
                    # فتح ارسال الرسائل
                    await client.edit_permissions(chat_id, user_id, send_messages=True)
                    # الرد على المستخدم
                    await client.send_message(chat_id, f'مرحباً @{participant.user.username if participant.user.username else participant.user.first_name} لقد تم تفعيل رسائلك 🎉')
                    to_remove.append(user_id)
            except:
                pass
        # إزالة المستخدمين الذين انضموا
        for user_id in to_remove:
            pending_users.pop(user_id)
        await asyncio.sleep(10)

# تشغيل البوت
async def main():
    asyncio.create_task(check_channel())
    print("Bot is running...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())