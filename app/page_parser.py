from selenium import webdriver
import re
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from app.models import Tag, Content, Comment, UserInfo, Reel


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


def extract_reel_tags(driver: webdriver.Chrome) -> list[Tag]:
    tag_xp = "//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs xlh3980 xvmahel x1n0sxbx x6prxxf xvq8zen xo1l8bm x1fey0fg']"
    tag_divs = driver.find_elements(
        By.XPATH,
        tag_xp,
    )
    return [
        Tag(name=i.text, url=i.find_element(By.TAG_NAME, "a").get_attribute("href"))
        for i in tag_divs
    ]


def extract_reel_describe(driver: webdriver.Chrome) -> str:
    desc_divs = driver.find_elements(
        By.XPATH, "//div[@class='xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs x126k92a']"
    )
    return desc_divs[0].text


def extract_reel_numbers(driver: webdriver.Chrome) -> list[str]:
    # 定位至 reel 右下方按鈕區域
    numbers_xp = "//div[@class='x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x2lah0s x193iq5w x6s0dn4 x1gslohp x12nagc xzboxd6 x14l7nz5']"
    numbers = driver.find_elements(By.XPATH, numbers_xp)
    # 過濾掉內部有 aria-label 的元素, 且若取到 '' 設定為 "0", 注意若有賞星星按鈕, 總物件會達到 5, 使用 [-3:] 選取倒數 3 個
    return [
        num.text if num.text else "0"
        for num in numbers
        if not num.find_elements(By.XPATH, ".//*[@aria-label]")
    ][-3:]


def extract_reel_author(driver: webdriver.Chrome) -> UserInfo:
    reel_author_ele = driver.find_elements(
        By.XPATH, "//a[@aria-label='查看擁有者個人檔案']"
    )[1]
    user_name = reel_author_ele.text
    user_url = reel_author_ele.get_attribute("href")
    user_id = parse_user_id_from_fb_url(user_url)

    return UserInfo(name=user_name, id=user_id, url=user_url)


def extract_content(driver: webdriver.Chrome, article: WebElement):
    """
    根據處理留言型態做不同處理
    - 貼圖類
    - 圖片類
    - 文字留言帶有表情符號
    """
    try:
        script = """
        var parent = arguments[0];
        var result = "";

        function extractText(node) {
            node.childNodes.forEach(child => {
                if (child.nodeType === Node.TEXT_NODE) {
                    result += child.textContent.trim();
                } else if (child.nodeType === Node.ELEMENT_NODE) {
                    if (child.tagName === "SPAN") {
                        var img = child.querySelector("img");
                        if (img) {
                            result += img.alt;  // 添加表情符號 alt 文字
                        }
                    } else if (child.tagName === "A") {
                        var link = child.getAttribute("href");  // 提取 a 標籤的網址
                        if (link) {
                            result += ` [[${child.text}: ${link}]] `;  // 加上網址
                        }
                    } else if (child.tagName === "DIV") {
                        if (result.trim() !== "") {
                            result += "\\n";  // 保持段落間換行
                        }
                        extractText(child);  // 遞迴處理內部結構
                    }
                }
            });
        }

        extractText(parent);
        return result;

        """

        text_divs = article.find_elements(By.XPATH, './/span[@dir="auto" and @lang]')
        if text_divs:
            # 取得 text 元素, 準備逐行解析
            text_ele = text_divs[0]
            result_text = driver.execute_script(script, text_ele)
            ret = Content(
                type="text",
                text=result_text,
                img_alt=None,
                img_url=None,
            )
        else:
            ret = Content(
                type="empty",
                text="沒有任何文字",
                img_alt=None,
                img_url=None,
            )

        # 檢查是否有圖片
        img_divs = article.find_elements(
            By.XPATH, ".//div[@class='x78zum5 xv55zj0 x1vvkbs']"
        )
        if img_divs:
            img_ele = img_divs[0].find_element(By.TAG_NAME, "img")
            ret.img_alt = img_ele.get_attribute("alt")
            ret.img_url = img_ele.get_attribute("src")
            ret.type += "+img"

        return ret

    except Exception as e:
        logger.error(e)
        return Content(
            type="unknown",
            text="留言內容解析失敗",
            img_alt=None,
            img_url=None,
        )


def extract_article(driver: webdriver.Chrome):
    main_comment_divs = driver.find_elements(
        By.XPATH,
        '//div[@role="article" and (contains(@aria-label, "的留言") or contains(@aria-label, "的回覆"))]',
    )

    tmp = []
    for article in main_comment_divs:
        user_name = article.find_elements(By.XPATH, ".//a[@attributionsrc and @role]")[
            1
        ].text

        user_url = article.find_element(
            By.XPATH, './/a[contains(@href, "facebook.com")]'
        ).get_attribute("href")
        user_id = parse_user_id_from_fb_url(user_url)

        content = extract_content(driver, article)

        try:
            likes = article.find_element(
                By.XPATH,
                './/span[contains(@class, "xuxw1ft") and not(contains(@class, "xktsk01"))]',
            ).text
        except Exception as e:
            logger.debug("此文章沒有任何讚")
            likes = "0"

        tmp.append(
            Comment(
                user=UserInfo(name=user_name, id=user_id, url=user_url),
                like_counts=likes,
                **content.model_dump(),
            )
        )
    return tmp


def scrape_reel(driver: webdriver.Chrome, url: str = "") -> Reel:
    likes, comments, shares = extract_reel_numbers(driver)
    return Reel(
        url=url,
        user=extract_reel_author(driver),
        text=extract_reel_describe(driver),
        tags=extract_reel_tags(driver),
        like_counts=likes,
        comment_counts=comments,
        share_counts=shares,
        comments=extract_article(driver),
    )
