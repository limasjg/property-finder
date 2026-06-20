import os
from dotenv import load_dotenv

load_dotenv()

def mask_secret(value):
	if not value:
		return "<vazio>"
	if len(value) <= 4:
		return "****"
	return f"{value[:2]}***{value[-2:]}"


print(f"EMAIL_RECIPIENT: {os.getenv('EMAIL_RECIPIENT', '<vazio>')}")
print(f"EMAIL_PASSWORD: {mask_secret(os.getenv('EMAIL_PASSWORD'))}")
print(f"EMAIL_SENDER: {os.getenv('EMAIL_SENDER', '<vazio>')}")
