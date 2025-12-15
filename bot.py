#!/usr/bin/env python3
"""
Simple Telegram AI Bot
- Loads personality from system_prompt.txt
- Stores conversation history per user
"""

import os
import json
from datetime import datetime
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
DATA_DIR = os.path.join(BASE_DIR, "data")
PROMPT_PATH = os.path.join(BASE_DIR, "system_prompt.txt")

def load_config():
	with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
		return json.load(f)

def load_system_prompt():
	if os.path.exists(PROMPT_PATH):
		with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
			return f.read().strip()
	return "You are a helpful assistant."

def load_conversation(user_id: str) -> list:
	os.makedirs(DATA_DIR, exist_ok=True)
	path = os.path.join(DATA_DIR, f"{user_id}.json")
	if os.path.exists(path):
		with open(path, 'r', encoding='utf-8') as f:
			return json.load(f)
	return []

def save_conversation(user_id: str, conversation: list):
	os.makedirs(DATA_DIR, exist_ok=True)
	path = os.path.join(DATA_DIR, f"{user_id}.json")
	with open(path, 'w', encoding='utf-8') as f:
		json.dump(conversation, f, indent=2, ensure_ascii=False)

def get_history_text(conversation: list, limit: int = 20) -> str:
	recent = conversation[-limit:]
	lines = []
	for m in recent:
		role = "Assistant" if m["role"] == "assistant" else "User"
		lines.append(f"{role}: {m['content']}")
	return "\n".join(lines)

config = load_config()
client = OpenAI(
	api_key=config.get("api_key"),
	base_url=config.get("base_url", "https://openrouter.ai/api/v1")
)
MODEL = config.get("model", "moonshotai/kimi-k2-0905")

async def generate_response(user_id: str, message: str) -> str:
	system_prompt = load_system_prompt()
	conversation = load_conversation(user_id)

	# Add user message
	conversation.append({
		"role": "user",
		"content": message,
		"timestamp": datetime.now().isoformat()
	})

	# Build context
	history = get_history_text(conversation)

	try:
		resp = client.chat.completions.create(
			model=MODEL,
			messages=[
				{"role": "system", "content": system_prompt},
				{"role": "user", "content": f"Conversation:\n{history}"}
			],
			max_tokens=1000
		)
		reply = resp.choices[0].message.content.strip()

		# Save assistant response
		conversation.append({
			"role": "assistant",
			"content": reply,
			"timestamp": datetime.now().isoformat()
		})
		save_conversation(user_id, conversation)

		return reply
	except Exception as e:
		return f"Error: {e}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not update.message or not update.message.text:
		return

	user_id = str(update.effective_user.id)
	message = update.message.text.strip()

	# Command: clear history
	if message.lower() == "/clear":
		save_conversation(user_id, [])
		await update.message.reply_text("✅ Conversation cleared.")
		return

	# Generate response
	response = await generate_response(user_id, message)
	await update.message.reply_text(response)

def main():
	token = config.get("telegram_token")
	if not token:
		print("❌ Set telegram_token in config.json")
		return

	print(f"🤖 Bot starting...")
	print(f"📝 Model: {MODEL}")

	app = ApplicationBuilder().token(token).build()
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
	app.add_handler(MessageHandler(filters.Regex(r"^/clear$"), handle_message))

	print("✅ Ready!")
	app.run_polling()

if __name__ == "__main__":
	main()