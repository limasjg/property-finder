import os
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("EMAIL_RECIPIENT"))
print(os.getenv("EMAIL_PASSWORD"))
print(os.getenv("EMAIL_SENDER"))
