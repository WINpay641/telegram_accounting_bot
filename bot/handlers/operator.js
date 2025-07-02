const { setOperator } = require("../../core/store");

module.exports = async (ctx) => {
  const match = ctx.message.text.match(/^设置操作人(@[\w\d_]+)$/);
  if (!match) return ctx.reply("格式错误，应为 设置操作人@用户名");

  const username = match[1];
  setOperator(ctx, username);
  return ctx.reply(`设置成功：操作人 ${username}`);
};
