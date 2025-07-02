function parseAmount(text) {
  const match = text.match(/[\d.]+/);
  return match ? parseFloat(match[0]) : null;
}

module.exports = { parseAmount };
