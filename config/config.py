import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PostgreSQL environment variables
DB_HOST = os.getenv("DB_HOST") or ""
DB_PORT = os.getenv("DB_PORT") or ""
DB_NAME = os.getenv("DB_NAME") or ""
DB_USER = os.getenv("DB_USER") or ""
DB_PASSWORD = os.getenv("DB_PASSWORD") or ""

# https://chatgpt.com/c/683553b0-b65c-8011-a14c-3d84797ae3a7
# https://grok.com/chat/75af6701-5d24-451a-b3a2-dc802455b4fa