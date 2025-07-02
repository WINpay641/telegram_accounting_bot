const { addSend, getBillText } = require("../../core/store");
const { parseAmount } = require("../../core/utils");

module.exports = async (ctx) => {
  const amount = parseAmount(ctx.message.text);
  if (!amount) return ctx.reply("格式错误：下发金额无效");

  addSend(ctx, amount);
  return ctx.reply(getBillText(ctx));
};
