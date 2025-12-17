#!/usr/bin/env python3
"""
Afrikaans AI Chatbot - Terminal Demo
"""

import os
import json
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

SYSTEM_PROMPT = """Jy is 'n vriendelike en behulpsame AI-assistent wat in Afrikaans kommunikeer.

Reëls:
- Antwoord ALTYD in Afrikaans, tensy die gebruiker spesifiek vra vir 'n ander taal.
- Gebruik natuurlike, alledaagse Afrikaans.
- Wees vriendelik en geduldig.
- As jy nie seker is van 'n Afrikaanse woord nie, gebruik die mees algemene term.
"""

def load_config():
	if os.path.exists(CONFIG_PATH):
		with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
			return json.load(f)
	return {}

def main():
	config = load_config()

	client = OpenAI(
		api_key=config.get("api_key", ""),
		base_url=config.get("base_url", "https://openrouter.ai/api/v1")
	)
	model = config.get("model", "moonshotai/kimi-k2-0905")

	conversation = []

	# Afrikaans UI
	print("\n" + "=" * 50)
	print("🇿🇦  AFRIKAANSE AI ASSISTENT")
	print("=" * 50)
	print("Welkom! Ek is jou Afrikaanse AI-assistent.")
	print("Tik jou boodskap en druk Enter.")
	print("Tik 'stop' om te sluit.\n")

	while True:
		try:
			user_input = input("Jy: ").strip()
		except (KeyboardInterrupt, EOFError):
			print("\n\nTotsiens! 👋")
			break

		if not user_input:
			continue

		if user_input.lower() in ['stop', 'exit', 'quit']:
			print("\nTotsiens! Lekker dag verder! 👋")
			break

		conversation.append({"role": "user", "content": user_input})

		try:
			resp = client.chat.completions.create(
				model=model,
				messages=[
					{"role": "system", "content": SYSTEM_PROMPT},
					*conversation
				],
				max_tokens=1000
			)
			reply = resp.choices[0].message.content.strip()
			conversation.append({"role": "assistant", "content": reply})
			print(f"\nAssistent: {reply}\n")

		except Exception as e:
			print(f"\nFout: {e}\n")

if __name__ == "__main__":
	main()