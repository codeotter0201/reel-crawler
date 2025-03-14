from selenium.webdriver.remote.webelement import WebElement
from bs4 import BeautifulSoup
import re
import pickle
from typing import List
import os

from app.models import Reel


def parse_web_element_to_soup(element: WebElement) -> BeautifulSoup:
    soup = BeautifulSoup(element.get_attribute("outerHTML"), "html.parser")
    print(soup.prettify())
    return soup


def parse_user_id_from_fb_url(url: str) -> str:
    # 若網址為 profile.php?id= 格式，擷取數字 ID
    match = re.search(r"facebook\.com/profile\.php\?id=(\d+)", url)
    if match:
        return match.group(1)

    # 否則擷取 facebook.com/ 後面第一段內容（直到遇到 / 或 ?）
    match = re.search(r"facebook\.com/([^/?]+)", url)
    if match:
        return match.group(1)

    return ""


def save_reels(reels: List[Reel], file_path: str = "download_data/data.pkl"):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            try:
                existing_data = pickle.load(f)
                if not isinstance(existing_data, list):
                    existing_data = []
            except (EOFError, pickle.UnpicklingError):
                existing_data = []
    else:
        existing_data = []

    reels = [i.model_dump() for i in reels]
    existing_data.extend(reels)

    with open(file_path, "wb") as f:
        pickle.dump(existing_data, f)


def load_reels(file_path: str = "download_data/data.pkl") -> List[Reel]:
    if not os.path.exists(file_path):
        return []

    with open(file_path, "rb") as f:
        try:
            data_list = pickle.load(f)
            if data_list:
                data_list = [Reel(**data) for data in data_list]
            return data_list if isinstance(data_list, list) else []
        except (EOFError, pickle.UnpicklingError):
            return []
