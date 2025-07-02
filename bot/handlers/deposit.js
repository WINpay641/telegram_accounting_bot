const { addDeposit } = require("../../core/store");
const { parseAmount } = require("../../core/utils");

module.exports = async (ctx) => {
  const amount = parseAmount(ctx.message.text);
  if (!amount) return ctx.reply("格式错误：入款金额无效");

  addDeposit(ctx, amount);
  return ctx.reply(`入款成功：${amount.toFixed(2)}`);
};
