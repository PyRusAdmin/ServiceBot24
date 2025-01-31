import environs
from loguru import logger

try:
    env = environs.Env()
    env.read_env('.env')

    CRYPTOMUS_API_KEY = env('CRYPTOMUS_API_KEY')
    CRYPTOMUS_MERCHANT_ID = env('CRYPTOMUS_MERCHANT_ID')
except Exception as e:
    logger.exception(f"Error: {e}")
