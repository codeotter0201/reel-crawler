import os
from selenium import webdriver

from app.config import Settings

setting = Settings()
WEBDRIVER_PATH = setting.WEB_DRIVER_PATH


def get_default_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")

    pwd_path = os.path.abspath(".")
    options.add_argument(rf"--user-data-dir={pwd_path}/{WEBDRIVER_PATH}")
    return options


driver = webdriver.Chrome(options=get_default_chrome_options())
