function formatBill(session) {
  const {
    deposits = [],
    withdraws = [],
    sends = [],
    settings: { inFee, inRate, outFee, outRate },
  } = session;

  const calcU = (amount, fee, rate, isOut = false) =>
    isOut
      ? (amount * (1 + fee)) / rate
      : (amount * (1 - fee)) / rate;

  const formatAmount = (n) => (n % 1 === 0 ? n.toFixed(0) : n.toFixed(2));
  const formatRate = (n) => n.toFixed(3);
  const formatFee = (n) => ${(n * 100).toFixed(1)}%;

  let lines = [];

  if (deposits.length) {
    lines.push(`今日入款（${deposits.length}笔）：`);
    deposits.forEach((d, i) => {
      const u = calcU(d.amount, inFee, inRate);
      lines.push(`  ${i + 1}. ${formatAmount(d.amount)} => ${u.toFixed(2)}U`);
    });
  }

  if (withdraws.length) {
    lines.push(`今日出款（${withdraws.length}笔）：`);
    withdraws.forEach((w, i) => {
      const u = calcU(w.amount, outFee, outRate, true);
      lines.push(`  ${i + 1}. ${formatAmount(w.amount)} => ${u.toFixed(2)}U`);
    });
  }

  if (sends.length) {
    lines.push(`今日下发（${sends.length}笔）：`);
    sends.forEach((s, i) => {
      lines.push(`  ${i + 1}. ${formatAmount(s.amount)}U`);
    });
  }

  lines.push(`入款费率 / 入款汇率：${formatFee(inFee)} / ${formatRate(inRate)}`);
  if (withdraws.length) {
    lines.push(`出款费率 / 出款汇率：${formatFee(outFee)} / ${formatRate(outRate)}`);
  }

  const totalIn = deposits.reduce((sum, d) => sum + d.amount, 0);
  const totalInU = deposits.reduce((sum, d) => sum + calcU(d.amount, inFee, inRate), 0);
  const totalSend = sends.reduce((sum, s) => sum + s.amount, 0);

  lines.push(`应下发：${formatAmount(totalIn)} => ${totalInU.toFixed(2)}U`);
  lines.push(`总下发：${totalSend.toFixed(2)}U`);

  const diff = totalInU - totalSend;
  lines.push(`未下发：${diff.toFixed(2)}U`);

  if (withdraws.length) {
    const totalOutU = withdraws.reduce((sum, w) => sum + calcU(w.amount, outFee, outRate, true), 0);
    lines.push(`总出款：${totalOutU.toFixed(2)}U`);
    lines.push(`应回款：${totalOutU.toFixed(2)}U`);
    lines.push(`已回款：${totalSend.toFixed(2)}U`);
  }

  return lines.join("\n");
}

module.exports = { formatBill };
