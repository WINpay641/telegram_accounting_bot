const { formatBill } = require("./formatter");

const data = {
  sessions: new Map(),
  addressMap: new Map(),
  operatorMap: new Map(),
};

function getSession(ctx) {
  const id = ctx.chat.id;
  if (!data.sessions.has(id)) {
    data.sessions.set(id, {
      deposits: [],
      withdraws: [],
      sends: [],
      settings: {
        inFee: 0.08,
        inRate: 1,
        outFee: 0.05,
        outRate: 1,
      },
    });
  }
  return data.sessions.get(id);
}

async function ensureStoreInitialized(ctx) {
  getSession(ctx);
}

function addDeposit(ctx, amount) {
  getSession(ctx).deposits.push({ amount });
}

function addWithdraw(ctx, amount) {
  getSession(ctx).withdraws.push({ amount });
}

function addSend(ctx, amount) {
  getSession(ctx).sends.push({ amount });
}

function getBillText(ctx) {
  return formatBill(getSession(ctx));
}

function clearBill(ctx) {
  data.sessions.set(ctx.chat.id, getSession(ctx)); // 重置
}

function setSetting(ctx, key, value) {
  getSession(ctx).settings[key] = value;
}

function recordAddress(ctx, address, from) {
  const record = data.addressMap.get(address) || { count: 0, lastUser: "无" };
  const info = {
    count: record.count + 1,
    lastUser: from,
  };
  data.addressMap.set(address, { count: info.count, lastUser: from });
  return info;
}

function setOperator(ctx, username) {
  data.operatorMap.set(ctx.chat.id, data.operatorMap.get(ctx.chat.id) || new Set());
  data.operatorMap.get(ctx.chat.id).add(username);
}

module.exports = {
  ensureStoreInitialized,
  addDeposit,
  addWithdraw,
  addSend,
  getBillText,
  clearBill,
  setSetting,
  recordAddress,
  setOperator,
};
