const { addWithdraw } = require("../../core/store");
const { parseAmount } = require("../../core/utils");

module.exports = async (ctx) => {
  const amount = parseAmount(ctx.message.text);
  if (!amount) return ctx.reply("格式错误：出款金额无效");

  addWithdraw(ctx, amount);
  return ctx.reply(`出款成功：${amount.toFixed(2)}`);
};
