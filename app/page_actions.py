from selenium import webdriver
from bs4 import BeautifulSoup
import time
from loguru import logger
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from app.config import Settings

setting = Settings()
USER_EMAIL = setting.USER_EMAIL
USER_PASSWORD = setting.USER_PASSWORD


def parse_web_element_to_soup(element: WebElement) -> BeautifulSoup:
    soup = BeautifulSoup(element.get_attribute("outerHTML"), "html.parser")
    print(soup.prettify())
    return soup


def login_fb(driver: webdriver.Chrome) -> None:
    ## 登入
    driver.get("https://www.facebook.com/")

    ## 檢查登入狀態 登入
    email_input_list = driver.find_elements(By.XPATH, '//*[@id="email"]')
    if email_input_list:
        print("登入中...")
        email_input = email_input_list[0]
        email_input.clear()
        email_input.send_keys(USER_EMAIL)
        time.sleep(0.1)
        pw_input = driver.find_element(By.XPATH, '//*[@id="pass"]')
        pw_input.clear()
        pw_input.send_keys(USER_PASSWORD)
        time.sleep(0.1)

        x = "//form/div[2]/button"
        login_btn = driver.find_element(By.XPATH, x)
        login_btn.click()
        print("登入成功")
    else:
        print("已登入")


def open_reel_url(
    driver: webdriver.Chrome,
    url: str = "https://www.facebook.com/reel/23958360287087979",
) -> None:
    ## 跳轉至指定頁面
    # driver.get("https://www.facebook.com/reel/644982128203468")
    driver.get(url)

    ## 若有影片下方有 查看更多 產生點擊行為
    xp = "//div/div/div[2]/div[1]/div/div[1]/div[2]/div/div/div[3]/span/div/div"
    content_load_more_btn_list = driver.find_elements(
        By.XPATH, f'{xp}[contains(text(), "查看更多")]'
    )
    if content_load_more_btn_list:
        logger.info("打開標籤頁面")
        content_load_more_btn_list[0].click()
        time.sleep(0.5)
    else:
        logger.debug("沒有更多標籤")

    ## 如果留言區沒有打開, 就點擊留言按鈕
    comment_section = driver.find_elements(By.XPATH, '//div[@role="complementary"]')
    if not comment_section:
        logger.info("打開留言區")
        comment_button_list = driver.find_elements(
            By.XPATH, '//div[@role="button" and @aria-label="留言"]'
        )
        comment_button_list[0].click()
        time.sleep(0.5)
    else:
        logger.debug("留言區已經開啟")

    time.sleep(3)

    ## 第一個元素為 filter, 其他元素為每一個留言的選項(檢舉...etc)
    comment_section = driver.find_elements(
        By.XPATH, '//div[@role="button" and @aria-haspopup="menu"]'
    )

    # 檢查有沒有留言, 如果沒有留言就結束
    if not comment_section:
        logger.info("Reel 沒有任何留言")
        return

    ## 判斷 filter 是否為 "所有留言" 若不是則觸發所有留言點擊
    if comment_section[0].text != "所有留言":
        logger.info("打開過濾選單")
        comment_section[0].click()

        ## 點擊過濾選項
        logger.info('點擊"所有留言選項"')
        comment_filters = driver.find_elements(By.XPATH, '//div[@role="menuitem"]')
        comment_filters[-1].click()
    else:
        logger.debug("已是查看所有留言模式")

    time.sleep(3)


def scroll_all_comments(driver: webdriver.Chrome) -> None:
    comment_body_xpath = "//html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div/div/div/div/div[2]/div/div[1]/div/div[1]/div/div[3]/div/div"
    comment_body = driver.find_element(By.XPATH, comment_body_xpath)

    while True:
        comment_body_rows = comment_body.find_elements(By.XPATH, "./*")

        # 檢查是否有"查看更多留言"按鈕
        load_more_button = None
        for ele in comment_body_rows[::-1]:  # 反向遍歷
            if "查看更多留言" in ele.text:
                load_more_button = ele
                break

        # 如果找到了"查看更多留言"按鈕，點擊並等待
        if load_more_button:
            # 滾動到最底部
            comment_section = driver.find_elements(
                By.XPATH, '//div[@role="button" and @aria-haspopup="menu"]'
            )
            comment_section[0].send_keys(Keys.END)
            time.sleep(1)  # 加點延遲，確保加載完成

            logger.debug("讀取更多留言")
            load_more_button.click()
            time.sleep(1)  # 加點延遲，確保加載完成

        else:
            # 沒有更多留言可讀取
            logger.info("讀取完畢")
            break


def click_reply_btn(driver: webdriver.Chrome):
    reply_btn_xp = '//div[@class="x1i10hfl xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 xe8uvvx xdj266r x11i5rnm xat24cr x2lwn1j xeuugli xexx8yu x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x3nfvp2 x87ps6o x1lku1pv x1a2a7pz x6s0dn4 xi81zsa x1q0g3np x1iyjqo2 xs83m0k xsyo7zv x1mnrxsn"]'
    reply_divs = driver.find_elements(
        By.XPATH,
        reply_btn_xp,
    )

    if not reply_divs:
        logger.info("回覆按鈕皆點擊成功")
        return
    else:
        for reply_btn in reply_divs:
            logger.debug("移動並點擊回覆按鈕")
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'start'});", reply_btn
            )
            reply_btn.click()
            time.sleep(0.3)

    # waiting for rendering
    time.sleep(1)
    click_reply_btn(driver)
