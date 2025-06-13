import os
# import dotenv
# dotenv.load_dotenv()
class Settings:
    MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"
    # DEBUG = "TRUE"
    PROVIDER = "novita"
    API_KEY = os.getenv('HF_TOKEN')

settings = Settings()