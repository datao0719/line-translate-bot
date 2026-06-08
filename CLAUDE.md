# line-translation-bot

## 專案概覽
LINE 翻譯機器人，使用 OpenAI GPT 進行中英文雙向翻譯，部署在 Render。

---

## 架構
- **app.py**：Flask Webhook 應用
- **部署方式**：Render Web Service（免費方案）
- **觸發方式**：LINE 傳訊息 → LINE Platform Webhook → Render → OpenAI → 回覆

---

## 功能
| 輸入 | 回覆 |
|------|------|
| 中文句子 | 英文翻譯 + 3～5 個關鍵單字/片語 |
| 英文句子 | 繁體中文翻譯 + 語法檢查 + 2～3 個相似句型 |

---

## 部署

**平台**：Render（render.com）
**啟動指令**：`gunicorn app:app`
**GitHub Repo**：datao0719/line-translate-bot

---

## 環境變數
- `LINE_CHANNEL_SECRET`
- `LINE_CHANNEL_ACCESS_TOKEN`
- `OPENAI_API_KEY`

> ⚠️ 2026-06-08 更新了 OpenAI API Key，Render 的環境變數需同步更新，否則 bot 會報錯。

---

## 注意事項
- Render 免費版 15 分鐘無流量會進入休眠，第一則訊息可能需等 30 秒
- LINE Webhook URL：`https://你的服務名稱.onrender.com/callback`
