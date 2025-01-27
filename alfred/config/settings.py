import os

class Config:
    REDIS_URL = os.getenv("REDIS_FEX_NEJI_READ_WRITE")


loaded_config = Config()