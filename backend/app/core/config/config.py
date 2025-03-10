import openai
from environs import Env

env = Env()
env.read_env()

DB_USER = env.str("DB_USER", "root")
DB_PASSWORD = env.str("DB_PASSWORD", "password")
DB_HOST = env.str("DB_HOST", "localhost")
DB_NAME = env.str("DB_NAME", "chatgpt_db")
DB_PORT = env.str("DB_PORT", "3306")

openai.api_key = env.str("GPT_API_KEY")
openai.base_url = env.str("GPT_URL")

DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
