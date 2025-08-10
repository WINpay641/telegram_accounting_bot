# template_manager.py
from telegram.ext import ContextTypes
from config import Config

templates = {}
last_file_id = {}
last_file_message = {}

async def handle_template_commands(update, context: ContextTypes.DEFAULT_TYPE, message_text, chat_id, username, is_operator):
    """处理模板相关命令和文件上传"""
    from user_manager import operating_groups

    if message_text == "群发说明":
        help_text = """
### 群发指令说明
**注意**：此说明仅在私聊中通过指令 群发说明 查看，所有群发相关功能仅在私聊中有效，所有操作员均可使用。当前版本暂不支持群发任务调度，请升级到 SuperGrok 订阅计划以启用，详情请访问 https://x.ai/grok。
1. 获取群 ID 的方式  
   - 方法：  
     1. 打开 Telegram 应用，进入目标群聊。  
     2. 点击群聊名称进入群组信息页面。  
     3. 点击“添加成员”或“邀请链接”（需要管理员权限），复制群 ID（例如 `-1001234567890`）。  
     4. 在私聊中手动输入群 ID 使用 编队 指令。  
   - 注意：群 ID 需为数字格式，例如 `-1001234567890`。
2. 编辑模板  
   - 指令：`编辑 模板名 广告文`  
   - 功能：创建或更新指定模板名对应的广告文，并自动关联最近在私聊发送的动图、视频或图片文件 ID。  
   - 示例：  
     - 先发送一个 .gif 文件，机器人回复文件 ID。  
     - 然后输入 编辑 模板1 欢迎体验我们的服务！  
     - 结果：模板 模板1 记录广告文“欢迎体验我们的服务！”及相关文件 ID。  
   - 注意：若模板已存在，则覆盖原有内容。
3. 创建/更新编队  
   - 指令：`编队 队名 群ID, 群ID`  
   - 功能：创建或更新指定队名对应的群组列表，使用逗号分隔多个群 ID。  
   - 示例：`编队 广告队 -1001234567890, -1009876543210`  
   - 结果：成功时回复“编队已更新”，若群 ID 无效则回复“任务目标有误请检查”。
4. 从编队删除群组  
   - 指令：`删除 队名 群ID, 群ID`  
   - 功能：从指定队名中删除一个或多个群 ID。  
   - 示例：`删除 广告队 -1001234567890`  
   - 结果：成功时回复“群组已从编队移除”，若队名或群 ID 无效则回复“任务目标有误请检查”。
### 注意事项
- **私聊限制**：以上指令仅在私聊与机器人对话时有效。
- **文件支持**：支持动图（`.gif`）、视频（`.mp4`）和图片（`.jpg/.png`），发送文件后自动返回文件 ID。
- **调度功能**：任务调度（如 任务 和 `任务列表`）当前不可用，请升级到 SuperGrok 订阅计划以启用，详情请访问 https://x.ai/grok。
- **错误处理**：编队不存在或群 ID 无效时，回复“任务目标有误请检查”。
        """
        await context.bot.send_message(chat_id=chat_id, text=help_text)
        return

    file_id = None
    file_type = None
    if update.message.animation:
        file_id = update.message.animation.file_id
        file_type = "动图"
    elif update.message.document:
        file_id = update.message.document.file_id
        file_type = "视频"
    elif update.message.video:
        file_id = update.message.video.file_id
        file_type = "视频"
    elif update.message.photo and len(update.message.photo) > 0:
        file_id = update.message.photo[-1].file_id
        file_type = "图片"
    
    if file_id:
        caption = update.message.caption or update.message.text or None
        print(f"[{Config.get_timestamp()}] 处理文件消息，类型: {file_type}, 文件ID: {file_id}, 文本: {caption or '无'}")
        last_file_id[chat_id] = file_id
        last_file_message[chat_id] = {"file_id": file_id, "caption": caption}
        await context.bot.send_message(chat_id=chat_id, text=f"{file_type}文件 ID: {file_id}")
        return
    
    if message_text.startswith("编辑 "):
        parts = message_text.split(" ", 2)
        if len(parts) == 3 and parts[1] and parts[2]:
            template_name = parts[1]
            message = parts[2]
            if is_operator or username == Config.INITIAL_ADMIN_USERNAME:
                file_id = last_file_id.get(chat_id)
                if file_id:
                    templates[template_name] = {"message": message, "file_id": file_id}
                    await context.bot.send_message(chat_id=chat_id, text=f"模板 {template_name} 已更新")
                else:
                    await context.bot.send_message(chat_id=chat_id, text="请先发送动图、视频或图片以获取文件 ID")
            else:
                await context.bot.send_message(chat_id=chat_id, text="仅操作员可执行此操作，请联系管理员设置权限")
        else:
            await context.bot.send_message(chat_id=chat_id, text="使用格式：编辑 模板名 广告文")
        return
    
    if message_text.startswith("任务 ") or message_text == "任务列表":
        await context.bot.send_message(chat_id=chat_id, text="群发任务功能当前不可用")
