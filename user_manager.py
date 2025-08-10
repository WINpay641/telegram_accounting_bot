# user_manager.py
from telegram.ext import ContextTypes
from config import Config
import re
from datetime import datetime

user_history = {}
operating_groups = {"private": {}}
is_accounting_enabled = {}
address_verify_count = {}
exchange_rates = {}

async def welcome_new_member(update, context: ContextTypes.DEFAULT_TYPE):
    """处理新成员加入"""
    chat_id = str(update.message.chat_id)
    if chat_id not in user_history:
        user_history[chat_id] = {}

    for member in update.message.new_chat_members:
        user_id = str(member.id)
        username = member.username
        first_name = member.first_name.strip() if member.first_name else None
        nickname = first_name or username or "新朋友"
        timestamp = Config.get_timestamp()

        user_history[chat_id][user_id] = {"username": username, "first_name": first_name}
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"欢迎 {nickname} 来到本群，入金叫卡找winpay，是你最好的选择"
        )

        if user_id in user_history[chat_id]:
            old_data = user_history[chat_id][user_id].copy()
            old_username = old_data["username"]
            old_first_name = old_data["first_name"]
            formatted_time = datetime.now(Config.TIMEZONE).strftime("%Y年%m月%d日 %H:%M")
            if username and username != old_username and first_name == old_first_name:
                warning = f"⚠️防骗提示⚠️ ({first_name}) 的用户名不一致\n之前用户名：@{old_username}\n现在用户名：@{username}\n修改时间：{formatted_time}\n请注意查证‼️"
                await context.bot.send_message(chat_id=chat_id, text=warning)
                print(f"[{timestamp}] 用户名变更警告: {first_name}, 之前 @{old_username}, 现在 @{username}")
            elif first_name and first_name != old_first_name and username == old_username:
                warning = f"⚠️防骗提示⚠️ (@{username}) 的昵称不一致\n之前昵称：{old_first_name}\n现在昵称：{first_name}\n修改时间：{formatted_time}\n请注意查证‼️"
                await context.bot.send_message(chat_id=chat_id, text=warning)
                print(f"[{timestamp}] 昵称变更警告: @{username}, 之前 {old_first_name}, 现在 {first_name}")

async def handle_message(update, context):
    """处理消息并路由到对应模块"""
    from transaction_parser import parse_transaction
    from transaction_manager import handle_bill, initialize_chat_transactions
    from group_manager import handle_group_commands
    from template_manager import handle_template_commands

    message_text = update.message.text.strip() if update.message.text else ""
    chat_id = str(update.message.chat_id)
    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name.strip() if update.message.from_user.first_name else None
    operator_name = first_name or username or "未知用户"
    timestamp = Config.get_timestamp()

    print(f"[{timestamp}] 收到消息: '{message_text}' 从用户 {user_id}, username: {username}, chat_id: {chat_id}")

    # 初始化群组数据
    initialize_chat_transactions(chat_id)
    if chat_id not in user_history:
        user_history[chat_id] = {}
    if chat_id not in operating_groups:
        operating_groups[chat_id] = {Config.INITIAL_ADMIN_USERNAME: True}
    if chat_id not in is_accounting_enabled:
        is_accounting_enabled[chat_id] = True
    if chat_id not in address_verify_count:
        address_verify_count[chat_id] = {"count": 0, "last_user": None}
    if chat_id not in exchange_rates:
        exchange_rates[chat_id] = {"deposit": 1.0, "withdraw": 1.0, "deposit_fee": 0.0, "withdraw_fee": 0.0}

    # 更新用户历史
    if user_id not in user_history[chat_id]:
        user_history[chat_id][user_id] = {"username": username, "first_name": first_name}
        print(f"[{timestamp}] 初始化用户 {user_id} 记录: username={username}, first_name={first_name}")
    else:
        old_data = user_history[chat_id][user_id].copy()
        old_username = old_data["username"]
        old_first_name = old_data["first_name"]
        formatted_time = datetime.now(Config.TIMEZONE).strftime("%Y年%m月%d日 %H:%M")
        if username and username != old_username and first_name == old_first_name:
            warning = f"⚠️防骗提示⚠️ ({first_name}) 的用户名不一致\n之前用户名：@{old_username}\n现在用户名：@{username}\n修改时间：{formatted_time}\n请注意查证‼️"
            await context.bot.send_message(chat_id=chat_id, text=warning)
            print(f"[{timestamp}] 用户名变更警告: {first_name}, 之前 @{old_username}, 现在 @{username}")
        elif first_name and first_name != old_first_name and username == old_username:
            warning = f"⚠️防骗提示⚠️ (@{username}) 的昵称不一致\n之前昵称：{old_first_name}\n现在昵称：{first_name}\n修改时间：{formatted_time}\n请注意查证‼️"
            await context.bot.send_message(chat_id=chat_id, text=warning)
            print(f"[{timestamp}] 昵称变更警告: @{username}, 之前 {old_first_name}, 现在 {first_name}")

    # 检查操作员权限
    is_operator = username and (username in operating_groups.get(chat_id, {}) or 
                              (update.message.chat.type == "private" and username in operating_groups.get("private", {})))

    # 处理文件上传
    if update.message.chat.type == "private" and (update.message.animation or update.message.document or update.message.video or update.message.photo):
        return await handle_template_commands(update, context, message_text, chat_id, username, is_operator)

    # 过滤非命令消息
    if not any(message_text.startswith(cmd) or message_text == cmd for cmd in [
        "开始", "停止记账", "恢复记账", "说明", "入款", "+", "下发", "设置操作员", "删除操作员",
        "设置入款汇率", "设置入款费率", "设置下发汇率", "设置下发费率", "账单", "+0", "删除",
        "删除账单", "日切", "操作员列表", "编队", "删除", "编辑", "任务", "任务列表", "群发说明"
    ]) and not re.match(r'^[T][a-km-zA-HJ-NP-Z1-9]{33}$', message_text):
        return

    # 限制非操作员命令
    if not is_operator and message_text not in ["账单", "+0", "说明"]:
        if username:
            await context.bot.send_message(chat_id=chat_id, text=f"@{username}非操作员，请联系管理员设置权限")
        return

    # 处理命令
    if message_text == "开始":
        if is_operator:
            transactions[chat_id].clear()
            is_accounting_enabled[chat_id] = True
            await context.bot.send_message(chat_id=chat_id, text="欢迎使用 winpay小秘书，入金叫卡找winpay，是你最好的选择")

    elif message_text == "停止记账":
        if is_operator:
            is_accounting_enabled[chat_id] = False
            await context.bot.send_message(chat_id=chat_id, text="已暂停记账功能")

    elif message_text == "恢复记账":
        if is_operator:
            is_accounting_enabled[chat_id] = True
            await context.bot.send_message(chat_id=chat_id, text="记账功能已恢复")

    elif message_text == "说明":
        help_text = """
可用指令：
开始使用：开始
记入入款：入款 或 +100 或 +100u/U
记入下发：下发 100 或 下发 50u/U
设置操作员：设置操作员 @用户名
删除操作员：删除操作员 @用户名
设置入款汇率
设置入款费率
设置下发汇率
设置下发费率
查看交易记录：账单 或 +0 
撤销交易记录 - 回复入款或下发消息+删除
清空账单：删除账单
查看操作员：操作员列表
        """
        await context.bot.send_message(chat_id=chat_id, text=help_text)

    elif (message_text.startswith("入款") or message_text.startswith("+")) and message_text != "+0":
        if is_operator and is_accounting_enabled.get(chat_id, True):
            transaction = parse_transaction(message_text, chat_id, operator_name, update.message.date, exchange_rates)
            if transaction:
                transactions[chat_id].append(transaction)
                await handle_bill(update, context, exchange_rates)
            else:
                await context.bot.send_message(chat_id=chat_id, text="请输入正确金额，例如：入款1000 或 +1000 或 +100u")

    elif message_text.startswith("下发"):
        if is_operator and is_accounting_enabled.get(chat_id, True):
            transaction = parse_transaction(message_text, chat_id, operator_name, update.message.date, exchange_rates)
            if transaction:
                transactions[chat_id].append(transaction)
                await handle_bill(update, context, exchange_rates)
            else:
                await context.bot.send_message(chat_id=chat_id, text="请输入正确金额，例如：下发500 或 下发50u")

    elif message_text.startswith("设置操作员"):
        if is_operator:
            operator = message_text.replace("设置操作员", "").strip()
            if operator.startswith("@"):
                operator = operator[1:]
                operating_groups[chat_id][operator] = True
                operating_groups["private"][operator] = True
                await context.bot.send_message(chat_id=chat_id, text=f"已将 @{operator} 设置为操作员")
            else:
                await context.bot.send_message(chat_id=chat_id, text="请使用格式：设置操作员 @用户名")

    elif message_text.startswith("删除操作员"):
        if is_operator:
            operator = message_text.replace("删除操作员", "").strip()
            if operator.startswith("@"):
                operator = operator[1:]
                if operator in operating_groups.get(chat_id, {}):
                    del operating_groups[chat_id][operator]
                    if operator in operating_groups.get("private", {}):
                        del operating_groups["private"][operator]
                    await context.bot.send_message(chat_id=chat_id, text=f"已删除 @{operator} 操作员权限")
                else:
                    await context.bot.send_message(chat_id=chat_id, text=f"@{operator} 不是当前群组的操作员")
            else:
                await context.bot.send_message(chat_id=chat_id, text="请使用格式：删除操作员 @用户名")

    elif message_text.startswith("设置入款汇率"):
        if is_operator and is_accounting_enabled.get(chat_id, True):
            try:
                rate = float(message_text.replace("设置入款汇率", "").strip())
                exchange_rates[chat_id]["deposit"] = round(rate, 3)
                await context.bot.send_message(chat_id=chat_id, text=f"设置成功入款汇率 {format_exchange_rate(exchange_rates[chat_id]['deposit'])}")
            except ValueError:
                await context.bot.send_message(chat_id=chat_id, text="请输入正确汇率，例如：设置入款汇率0.98")

    elif message_text.startswith("设置入款费率"):
        if is_operator and is_accounting_enabled.get(chat_id, True):
            try:
                rate = float(message_text.replace("设置入款费率", "").strip()) / 100
                exchange_rates[chat_id]["deposit_fee"] = rate
                await context.bot.send_message(chat_id=chat_id, text=f"设置成功入款费率 {int(rate*100)}%")
            except ValueError:
                await context.bot.send_message(chat_id=chat_id, text="请输入正确费率，例如：设置入款费率8")

    elif message_text.startswith("设置下发汇率"):
        if is_operator and is_accounting_enabled.get(chat_id, True):
            try:
                rate = float(message_text.replace("设置下发汇率", "").strip())
                exchange_rates[chat_id]["withdraw"] = round(rate, 3)
                await context.bot.send_message(chat_id=chat_id, text=f"设置成功下发汇率 {format_exchange_rate(exchange_rates[chat_id]['withdraw'])}")
            except ValueError:
                await context.bot.send_message(chat_id=chat_id, text="请输入正确汇率，例如：设置下发汇率1.25")

    elif message_text.startswith("设置下发费率"):
        if is_operator and is_accounting_enabled.get(chat_id, True):
            try:
                rate = float(message_text.replace("设置下发费率", "").strip()) / 100
                exchange_rates[chat_id]["withdraw_fee"] = rate
                await context.bot.send_message(chat_id=chat_id, text=f"设置成功下发费率 {int(rate*100)}%")
            except ValueError:
                await context.bot.send_message(chat_id=chat_id, text="请输入正确费率，例如：设置下发费率8")

    elif message_text == "账单" or message_text == "+0":
        await handle_bill(update, context, exchange_rates)

    elif message_text == "删除":
        if is_operator and is_accounting_enabled.get(chat_id, True):
            if update.message.reply_to_message:
                original_message = update.message.reply_to_message.text.strip()
                print(f"[{timestamp}] 尝试删除，原始消息: '{original_message}'")
                if original_message.startswith("+") and not original_message == "+0":
                    amount_str = original_message.replace("+", "").strip()
                    amount = float(amount_str.rstrip('uU'))
                    has_u = amount_str.lower().endswith('u')
                    for t in transactions[chat_id][:]:
                        if t.startswith("入款"):
                            t_amount = float(t.split(" -> ")[0].split()[1].rstrip('u'))
                            t_has_u = t.split()[1].endswith('u')
                            if t_amount == amount and has_u == t_has_u:
                                transactions[chat_id].remove(t)
                                await context.bot.send_message(chat_id=chat_id, text=f"入款 {format_amount(amount)}{'u' if has_u else ''} 已被撤销")
                                await handle_bill(update, context, exchange_rates)
                                return
                elif original_message.startswith("下发"):
                    amount_str = original_message.replace("下发", "").strip()
                    amount = float(amount_str.rstrip('uU'))
                    has_u = amount_str.lower().endswith('u')
                    for t in transactions[chat_id][:]:
                        if t.startswith("下发"):
                            t_amount = float(t.split(" -> ")[0].split()[1].rstrip('u'))
                            t_has_u = t.split()[1].endswith('u')
                            if t_amount == amount and has_u == t_has_u:
                                transactions[chat_id].remove(t)
                                await context.bot.send_message(chat_id=chat_id, text=f"下发 {format_amount(amount)}{'u' if has_u else ''} 已被撤销")
                                await handle_bill(update, context, exchange_rates)
                                return
            await context.bot.send_message(chat_id=chat_id, text="无法撤销此消息，请确保回复正确的入款或下发记录")

    elif message_text == "删除账单":
        if is_operator and is_accounting_enabled.get(chat_id, True):
            transactions[chat_id].clear()
            await context.bot.send_message(chat_id=chat_id, text="当前账单已结算💰，重新开始记账")

    elif message_text == "日切" and username == Config.INITIAL_ADMIN_USERNAME:
        if is_operator and is_accounting_enabled.get(chat_id, True):
            transactions[chat_id].clear()
            await context.bot.send_message(chat_id=chat_id, text="交易记录已清空")

    elif message_text == "操作员列表":
        if is_operator:
            op_list = ", ".join([f"@{op}" for op in operating_groups.get(chat_id, {})])
            private_op_list = ", ".join([f"@{op}" for op in operating_groups.get("private", {})]) if "private" in operating_groups else "无"
            await context.bot.send_message(chat_id=chat_id, text=f"当前群组操作员列表: {op_list if op_list else '无'}\n私聊操作员列表: {private_op_list}")

    elif re.match(r'^[T][a-km-zA-HJ-NP-Z1-9]{33}$', message_text):
        if is_accounting_enabled.get(chat_id, True):
            current_user = f"@{username}" if username else "未知用户"
            address_verify_count[chat_id]["count"] += 1
            last_user = address_verify_count[chat_id]["last_user"] or "无"
            address_verify_count[chat_id]["last_user"] = current_user
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"{message_text}\n验证次数：{address_verify_count[chat_id]['count']}\n本次发送人：{current_user}\n上次发送人：{last_user}"
            )

    elif update.message.chat.type == "private":
        await handle_group_commands(update, context, message_text, chat_id, username, is_operator)
