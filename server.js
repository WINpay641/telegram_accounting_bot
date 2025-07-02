const express = require("express");
const { Telegraf } = require("telegraf");
const bot = require("./bot");
const { BOT_TOKEN } = require("./config/env");

const app = express();
app.use(express.json());

const tgBot = new Telegraf(BOT_TOKEN);
bot(tgBot);

tgBot.telegram.setMyCommands([
  { command: "start", description: "启动机器人" },
]);

app.post(`/webhook/${BOT_TOKEN}`, (req, res) => {
  tgBot.handleUpdate(req.body);
  res.sendStatus(200);
});

app.get("/", (_, res) => {
  res.send("Bot is running.");
});

app.listen(process.env.PORT || 3000, () => {
  console.log("Server started");
});
