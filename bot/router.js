const deposit = require("./handlers/deposit");
const withdraw = require("./handlers/withdraw");
const send = require("./handlers/send");
const bill = require("./handlers/bill");
const setting = require("./handlers/setting");
const validate = require("./handlers/validate");
const operator = require("./handlers/operator");
const remove = require("./handlers/delete");

module.exports = async (ctx) => {
  const text = ctx.message.text;

  if (/^入款/.test(text) || /^[+＋]/.test(text)) return deposit(ctx);
  if (/^出款/.test(text)) return withdraw(ctx);
  if (/^下发/.test(text)) return send(ctx);
  if (/^账单$|^\+0$/.test(text)) return bill(ctx);
  if (/^设置/.test(text)) return setting(ctx);
  if (/^删除账单$/.test(text)) return remove(ctx);
  if (/^设置操作人/.test(text)) return operator(ctx);
  if (/^[13LM][a-km-zA-HJ-NP-Z1-9]{25,}/.test(text) || /^T[0-9a-zA-Z]{30,}/.test(text)) {
    return validate(ctx);
  }

  return ctx.reply("无法识别的指令");
};
