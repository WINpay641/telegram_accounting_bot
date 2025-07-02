const { recordAddress } = require("../../core/store");

module.exports = async (ctx) => {
  const address = ctx.message.text.trim();
  const from = @${ctx.from.username || ctx.from.id};
  const info = recordAddress(ctx, address, from);

  return ctx.reply(
    验证地址：\n${address}\n验证次数：${info.count}\n上次发送人：${info.lastUser}\n本次发送人：${from}
  );
};
