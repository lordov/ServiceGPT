import openai
from environs import Env

env = Env()
env.read_env()

DB_USER = env.str("DB_USER", "root")
DB_PASSWORD = env.str("DB_PASSWORD", "password")
DB_HOST = env.str("DB_HOST", "localhost")
DB_NAME = env.str("DB_NAME", "chatgpt_db")
openai.api_key = env.str("OPENAI_API_KEY")

DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
