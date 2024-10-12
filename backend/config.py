import os

from dotenv import load_dotenv
load_dotenv()


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "secretkey",
)
if not SECRET_KEY:
    SECRET_KEY = os.urandom(32)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 120
REFRESH_TOKEN_EXPIRES_MINUTES = 15 * 24 * 60  # 15 days

