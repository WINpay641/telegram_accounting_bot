# group_manager.py
import re
from telegram.ext import ContextTypes
from config import Config

team_groups = {}

async def handle_group_commands(update, context: ContextTypes.DEFAULT_TYPE, message_text, chat_id, username, is_operator):
    """处理私聊中的群组相关命令"""
    from user_manager import operating_groups

    if message_text == "编队列表":
        if is_operator or username == Config.INITIAL_ADMIN_USERNAME:
            if team_groups:
                response = "编队列表：\n" + "\n".join(f"{team}: {', '.join(groups)}" for team, groups in sorted(team_groups.items()))
            else:
                response = "无编队"
            print(f"[{Config.get_timestamp()}] 编队列表响应: {response}")
            await context.bot.send_message(chat_id=chat_id, text=response)
        else:
            await context.bot.send_message(chat_id=chat_id, text="仅操作员可查看编队列表，请联系管理员设置权限")
    
    elif message_text.startswith("编队 "):
        parts = message_text.split(" ", 2)
        if len(parts) == 3 and parts[1] and parts[2]:
            team_name = parts[1]
            if is_operator or username == Config.INITIAL_ADMIN_USERNAME:
                try:
                    group_ids = [gid.strip() for gid in re.split(r'[,，]', parts[2]) if gid.strip()]
                    if not group_ids:
                        raise ValueError("群ID列表为空")
                    for gid in group_ids:
                        if not gid.startswith("-") or not gid[1:].isdigit():
                            raise ValueError(f"无效群ID: {gid}")
                    team_groups[team_name] = list(set(team_groups.get(team_name, []) + group_ids))
                    print(f"[{Config.get_timestamp()}] 编队输入: 队名={team_name}, 群ID={group_ids}")
                    await context.bot.send_message(chat_id=chat_id, text=f"编队已更新: {team_name}，包含群组: {', '.join(group_ids)}")
                except ValueError as e:
                    print(f"[{Config.get_timestamp()}] 编队解析失败: {e}")
                    await context.bot.send_message(chat_id=chat_id, text=f"任务目标有误请检查: {e}")
            else:
                await context.bot.send_message(chat_id=chat_id, text="仅操作员可执行此操作，请联系管理员设置权限")
        else:
            await context.bot.send_message(chat_id=chat_id, text="使用格式：编队 队名 群ID,群ID")
    
    elif message_text.startswith("删除 "):
        parts = message_text.split(" ", 2)
        if len(parts) == 3 and parts[1] and parts[2]:
            team_name = parts[1]
            if is_operator or username == Config.INITIAL_ADMIN_USERNAME:
                try:
                    group_ids = [gid.strip() for gid in re.split(r'[,，]', parts[2]) if gid.strip()]
                    if not group_ids:
                        raise ValueError("群ID列表为空")
                    if team_name in team_groups:
                        for gid in group_ids:
                            if gid in team_groups[team_name]:
                                team_groups[team_name].remove(gid)
                        if not team_groups[team_name]:
                            del team_groups[team_name]
                        print(f"[{Config.get_timestamp()}] 删除群组: 队名={team_name}, 群ID={group_ids}")
                        await context.bot.send_message(chat_id=chat_id, text="群组已从编队移除")
                    else:
                        await context.bot.send_message(chat_id=chat_id, text="任务目标有误请检查: 编队不存在")
                except ValueError as e:
                    print(f"[{Config.get_timestamp()}] 删除解析失败: {e}")
                    await context.bot.send_message(chat_id=chat_id, text=f"任务目标有误请检查: {e}")
            else:
                await context.bot.send_message(chat_id=chat_id, text="仅操作员可执行此操作，请联系管理员设置权限")
        else:
            await context.bot.send_message(chat_id=chat_id, text="使用格式：删除 队名 群ID,群ID")
