const { getBillText } = require("../../core/store");

module.exports = async (ctx) => {
  return ctx.reply(getBillText(ctx));
};
