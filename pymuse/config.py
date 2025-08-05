import yaml
import sys
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class ConfigSchema(BaseModel):
    token: str
    database: str
    timeout: int
    admins: list[int]
    info: str
    commands: list[tuple[str, str]]


config_path = "config.yml"
if len(sys.argv) == 2:
    config_path = sys.argv[1]


with open(config_path, "r", encoding="utf-8") as file:
    _cfgYml: dict = yaml.safe_load(file)

# ---------- flo ---------- ver ---------- lin >

admins = []
adminsStr = os.environ.get("ADMINS")
if adminsStr:
    admins = adminsStr.split(",")

_cfgEnv = {
    "token": os.environ["TELEGRAM_TOKEN"],
    "admins": admins,
}

_cfgYml.update(_cfgEnv)

config = ConfigSchema.model_validate(_cfgYml)
