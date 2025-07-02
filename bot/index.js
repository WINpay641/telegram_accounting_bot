const setupRouter = require("./router");
const { ensureStoreInitialized } = require("../core/store");

module.exports = (bot) => {
  bot.on("text", async (ctx) => {
    await ensureStoreInitialized(ctx);
    await setupRouter(ctx);
  });
};
