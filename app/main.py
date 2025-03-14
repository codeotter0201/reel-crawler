import sys

from app.webdriver_setup import driver
from app.page_actions import (
    login_fb,
    open_reel_url,
    scroll_all_comments,
    click_reply_btn,
)
from app.page_parser import scrape_reel
from app.utils import save_reels

if __name__ == "__main__":
    tmp = []

    # 檢查是否有提供網址參數
    if len(sys.argv) < 2:
        print("請提供至少一個 Facebook Reel 網址")
        print("使用方式: python main.py <url1> <url2> ...")
        sys.exit(1)

    # 從命令列參數獲取所有網址
    urls = sys.argv[1:]

    # 登入 Facebook（只需要登入一次）
    login_fb(driver)

    # 處理每個網址
    for url in urls:
        try:
            print(f"\n處理網址: {url}")
            open_reel_url(driver, url)
            scroll_all_comments(driver)
            click_reply_btn(driver)

            ret = scrape_reel(driver, url)
            # print(ret)

            tmp.append(ret)

        except Exception as e:
            print(f"處理網址 {url} 時發生錯誤: {str(e)}")
            continue

    save_reels(tmp)

    driver.close()
