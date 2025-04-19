#pip install python-telegram-bot
#pip install openai
#pip install requests beautifulsoup4
# pip install lxml

import time
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

from chat import Chat
from pt_tool import TJUpt

ALLOWED_USERS = [123456789, 123456789]# Telegram 用户 ID 白名单
TOKEN='1111111111:22222222222222222222222222222222222'#bot的密钥
chat_api_key = "sk-11111111111111111111111111111111"# DeepSeek API Key
TJUpt_passkey = "11111111111111111111111111111111"#pt站点passkey
TJUpt_downloadpath = r"D:\your_path\tg.torrent"#种子下载目录
proxy_url = 'http://127.0.0.1:7890'#代理服务器地址
#https://api.telegram.org/bot{TOKEN}}/getupdates#浏览器打开后可用于查看用户id

WAITING_FOR_CHAT = 1
WAITING_FOR_TRANSLATE = 2
WAITING_FOR_PT = 3

'''测试服务器是否在线'''
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id  # 获取用户的 Telegram ID
    if user_id not in ALLOWED_USERS:
        print(f"用户 {user_id} 试图使用bot测试，但被拒绝。")
        return  # 直接返回，不回复该用户
    text = 'bot收到！'
    await context.bot.send_message(chat_id=update.effective_chat.id,text=text)

'''取消当前会话'''
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id  # 获取用户的 Telegram ID
    if user_id not in ALLOWED_USERS:
        print(f"用户 {user_id} 试图使用bot取消，但被拒绝。")
        return  # 直接返回，不回复该用户
    context.user_data['active_conversation'] = False  # 结束对话，清除标志
    await update.message.reply_text("当前会话已结束")
    return ConversationHandler.END  # 结束会话

'''聊天'''
async def chat_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id  
    if user_id not in ALLOWED_USERS:
        print(f"用户 {user_id} 试图使用bot聊天，但被拒绝。")
        return  # 直接返回，不回复该用户
    if context.user_data.get('active_conversation', False):
        await update.message.reply_text("你当前已有一个任务正在进行，请先结束当前任务。")
        return ConversationHandler.END  # 如果有对话进行，结束新对话的启动
    context.user_data['active_conversation'] = True  # 设置标志，表示对话正在进行
    await update.message.reply_text("你好！我是由深度求索（DeepSeek）开发的人工智能助手，擅长通过自然语言处理提供信息查询、对话交流和问题解答。有需要帮忙的，尽管告诉我！")
    context.user_data['chat_entity'] = Chat(chat_api_key)
    return WAITING_FOR_CHAT  # 进入等待用户输入的状态
async def chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id  
    if user_id not in ALLOWED_USERS:
        print(f"用户 {user_id} 试图使用bot聊天，但被拒绝。")
        return  # 直接返回，不回复该用户
    user_text = update.message.text  # 获取用户输入的文本
    chat = context.user_data.get('chat_entity')
    assistant_response = chat.chat(user_text)
    await update.message.reply_text(assistant_response)
    return WAITING_FOR_CHAT    # 继续会话

'''翻译'''
async def translate_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id  
    if user_id not in ALLOWED_USERS:
        print(f"用户 {user_id} 试图使用bot翻译，但被拒绝。")
        return  # 直接返回，不回复该用户
    if context.user_data.get('active_conversation', False):
        await update.message.reply_text("你当前已有一个任务正在进行，请先结束当前任务。")
        return ConversationHandler.END  # 如果有对话进行，结束新对话的启动
    context.user_data['active_conversation'] = True  # 设置标志，表示对话正在进行
    await update.message.reply_text("请输入翻译内容")
    context.user_data['chat_entity'] = Chat(chat_api_key)
    return WAITING_FOR_TRANSLATE  # 进入等待用户输入的状态
async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id  
    if user_id not in ALLOWED_USERS:
        print(f"用户 {user_id} 试图使用bot翻译，但被拒绝。")
        return  # 直接返回，不回复该用户
    user_text = update.message.text  # 获取用户输入的文本
    chat = context.user_data.get('chat_entity')
    assistant_response = chat.chat(f"请用学术语言将以下内容翻译成中文: {user_text}")
    await update.message.reply_text(assistant_response)
    chat.clear_history()
    return WAITING_FOR_TRANSLATE    # 继续会话

'''PT'''
async def pt_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id  
    if user_id not in ALLOWED_USERS:
        print(f"用户 {user_id} 试图使用bot PT，但被拒绝。")
        return  # 直接返回，不回复该用户
    if context.user_data.get('active_conversation', False):
        await update.message.reply_text("你当前已有一个任务正在进行，请先结束当前任务。")
        return ConversationHandler.END  # 如果有对话进行，结束新对话的启动
    context.user_data['active_conversation'] = True  # 设置标志，表示对话正在进行
    await update.message.reply_text("请输入影片名称")
    context.user_data['pt_entity'] = TJUpt(TJUpt_passkey, TJUpt_downloadpath)
    return WAITING_FOR_PT  # 进入等待用户输入的状态
async def pt_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id  
    if user_id not in ALLOWED_USERS:
        print(f"用户 {user_id} 试图使用bot PT，但被拒绝。")
        return  # 直接返回，不回复该用户
    user_text = update.message.text  # 获取用户输入的文本
    pt = context.user_data.get('pt_entity')
    if user_text.isdigit() and user_text in "0123456789":
        await update.message.reply_text(pt.download_file(int(user_text)))
    else:
        await update.message.reply_text(pt.get_resources(user_text))
    return WAITING_FOR_PT    # 继续会话


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')



application = ApplicationBuilder().token(TOKEN).proxy_url(proxy_url).get_updates_proxy_url(proxy_url).build()#使用代理
#application = ApplicationBuilder().token(TOKEN).build()#不使用代理

application.add_handler(CommandHandler('test', test))


chat_handler = ConversationHandler(
    entry_points=[CommandHandler("chat", chat_start)],  # 入口命令
    states={
        WAITING_FOR_CHAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message)],  # 处理用户输入的文本
    },
    fallbacks=[CommandHandler("cancel", cancel)],  # 处理 /cancel 取消
)
application.add_handler(chat_handler)


translate_handler = ConversationHandler(
    entry_points=[CommandHandler("translate", translate_start)],  # 入口命令
    states={
        WAITING_FOR_TRANSLATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message)],  # 处理用户输入的文本
    },
    fallbacks=[CommandHandler("cancel", cancel)],  # 处理 /cancel 取消
)
application.add_handler(translate_handler)


pt_handler = ConversationHandler(
    entry_points=[CommandHandler("pt", pt_start)],  # 入口命令
    states={
        WAITING_FOR_PT: [MessageHandler(filters.TEXT & ~filters.COMMAND, pt_message)],  # 处理用户输入的文本
    },
    fallbacks=[CommandHandler("cancel", cancel)],  # 处理 /cancel 取消
)
application.add_handler(pt_handler)

application.add_error_handler(error)

application.run_polling(poll_interval=2)  # 每 2 秒轮询一次




