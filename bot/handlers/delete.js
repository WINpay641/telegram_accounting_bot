const { clearBill } = require("../../core/store");

module.exports = async (ctx) => {
  clearBill(ctx);
  return ctx.reply("已删除今日账单记录");
};
