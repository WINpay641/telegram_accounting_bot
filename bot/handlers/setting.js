const { setSetting } = require("../../core/store");

module.exports = async (ctx) => {
  const text = ctx.message.text;

  const match = text.match(/^设置(入款|出款)?(费率|汇率)([\d.]+%?)$/);
  if (!match) return ctx.reply("格式错误：应为 设置入款费率1.2% 或 设置出款汇率6.89");

  const type = match[1] || "入款";
  const target = match[2];
  const raw = match[3];
  const key = (type === "入款" ? "in" : "out") + (target === "费率" ? "Fee" : "Rate");

  const value = raw.includes("%") ? parseFloat(raw) / 100 : parseFloat(raw);
  if (isNaN(value)) return ctx.reply("数值错误");

  setSetting(ctx, key, value);

  const suffix = target === "费率" ? ${(value * 100).toFixed(1)}% : value.toFixed(3);
  return ctx.reply(`设置成功：${type}${target}${suffix}`);
};
