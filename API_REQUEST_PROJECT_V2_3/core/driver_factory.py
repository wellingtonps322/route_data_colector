from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


class DriverFactory():

    def __init__(self) -> None:
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--log-level=3')  # Disable console log
        chrome_options.add_experimental_option("detach", True)
        service = Service(ChromeDriverManager().install())
        # WebDriverWait(driver, timeout=10)  # .until(document_initialised)
        # browser.maximize_window()
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        # self.driver.implicitly_wait(20)

    def getDriver(self):
        return self.driver

    def getUrl(self, url: str):
        self.driver.get(url=url)

    def killDriver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
