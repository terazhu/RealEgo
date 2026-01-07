import os

class Settings:
    # Database
    MYSQL_HOST = "mysql3cadafbd4a23.rds.ivolces.com"
    MYSQL_PORT = 3306
    MYSQL_USER = "tera"
    MYSQL_PASSWORD = os.getenv("TERA_MYSQL_PASS", "tera") # Default or from env
    MYSQL_DB = "realego" # Assuming a DB name, will need to create if not exists
    DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

    # TOS
    TOS_ENDPOINT = "terazhu.tos-cn-beijing.volces.com"
    TOS_REGION = "cn-beijing"
    TOS_AK = os.getenv("TERA_TOS_AK")
    TOS_SK = os.getenv("TERA_TOS_SK")
    TOS_BUCKET = "realego-data" # Will use a specific bucket name

    # Mem0
    MEM0_API_URL = "https://mem0-cnlfjzigaku8gczkzo.mem0.volces.com"
    MEM0_API_KEY = os.getenv("MEM_KEY", "95af5d48-a629-5cdb-b914-341ae85313a6")

    # LLM (ARK)
    ARK_API_URL = "https://ark.cn-beijing.volces.com/api/v3"
    ARK_API_KEY = os.getenv("ARK_API_KEY")
    ARK_MODEL = "ep-20251211110617-l2jqj"

    # Security
    SECRET_KEY = "your-secret-key-here" # Change in production
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

settings = Settings()
