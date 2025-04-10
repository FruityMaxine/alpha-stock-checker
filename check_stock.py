import os
import time
import logging
from bs4 import BeautifulSoup
from mail_utils import send_email

# 用于判断使用哪种浏览器：如果环境变量 GITHUB_ACTIONS 为 true，则采用 Chrome；否则采用 Edge
def init_driver():
    # 判断是否运行在 GitHub Actions 环境中
    if os.environ.get("GITHUB_ACTIONS", "false").lower() == "true":
        # 在 GitHub Actions（Linux 环境），使用 Chrome（通常 pre-installed）
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        service = Service(ChromeDriverManager().install())
        logging.info("使用 Chrome 浏览器 (GitHub Actions 环境)")
        return webdriver.Chrome(service=service, options=chrome_options)
    else:
        # 本地环境，使用 Microsoft Edge
        from selenium import webdriver
        from selenium.webdriver.edge.options import Options as EdgeOptions
        from selenium.webdriver.edge.service import Service as EdgeService
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        
        edge_options = EdgeOptions()
        edge_options.use_chromium = True
        edge_options.add_argument("--headless")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--window-size=1920,1080")
        # 指定 Edge 浏览器可执行文件的位置（如果非默认路径，请修改此处）
        edge_options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        service = EdgeService(EdgeChromiumDriverManager().install())
        logging.info("使用 Microsoft Edge 浏览器 (本地 Windows 环境)")
        return webdriver.Edge(service=service, options=edge_options)


def check_stock_selenium(url):
    """
    使用 Selenium 加载目标页面，并等待 JavaScript 执行完成后，
    从最终渲染的 DOM 中判断库存状态：
      - 查找 class 为 "product-form-inline-atc-button" 的按钮；
      - 如果按钮存在且带有 disabled 属性，则返回 False（无货）；
      - 如果按钮存在且没有 disabled 属性，则返回 True（有货）。
    """
    driver = init_driver()
    driver.get(url)
    # 等待页面加载和 JS 执行（根据情况调整等待时间；可使用 WebDriverWait 进行更精确等待）
    time.sleep(5)
    
    try:
        # 定位最终呈现库存状态的内联按钮
        button = driver.find_element("css selector", ".product-form-inline-atc-button")
        button_html = button.get_attribute("outerHTML")
        logging.debug("Selenium 检测到内联按钮:\n" + button_html)
        # 判断按钮的 disabled 属性
        if button.get_attribute("disabled") is not None:
            logging.info("Selenium 检测到按钮带有 disabled 属性，判断为缺货。")
            stock = False
        else:
            logging.info("Selenium 检测到按钮未带 disabled 属性，判断为有货。")
            stock = True
    except Exception as e:
        logging.error(f"Selenium 检测失败: {e}")
        stock = None

    driver.quit()
    return stock


def main():
    # 默认目标页面 URL 和接收通知的邮箱已写入代码，支持环境变量覆盖
    stock_url = os.environ.get("STOCK_URL", "https://example.com/product-page")
    notify_email = os.environ.get("NOTIFY_EMAIL", "your_email@example.com")
    
    # 配置日志，输出 DEBUG 信息便于调试
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info(f"开始检测产品库存，目标 URL：{stock_url}")
    
    stock_status = check_stock_selenium(stock_url)
    
    if stock_status is None:
        logging.info("无法确定产品的库存状态。")
    elif stock_status:
        logging.info("Selenium 检测到产品【有货】！")
        subject = "AlphaM现货通知"
        content = f"快看！AlphaM在 {stock_url} 已经有货了，赶紧下单吧！"
        send_email(notify_email, subject, content)
    else:
        logging.info("Selenium 检测到产品【缺货】。")

if __name__ == "__main__":
    main()
