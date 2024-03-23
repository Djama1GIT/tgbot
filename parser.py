import os.path
from io import BytesIO

from time import sleep
from typing import List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from webdriver_manager.firefox import GeckoDriverManager

from config import Settings
from logger import logger


class TextParserFromImage:
    HOST = "https://translate.yandex.ru/ocr"
    INPUT_FILE = (By.XPATH, "(//input[contains(@type, 'file')])[1]")
    OPEN_AS_TEXT = (By.XPATH, "(//button[contains(., 'Открыть как текст')])[1]")
    SPAN_TEXT = (By.XPATH, "(//div[contains(@id, 'textLayer')])/span[contains(@class, 'measurer-text_main')]")

    def __init__(self, _env_file=''):
        settings = Settings(_env_file=_env_file)

        if settings.WEBDRIVER == "CHROMIUM":
            self.DriverManager = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM)
            self.options = webdriver.ChromeOptions()
            self.web_driver = webdriver.Chrome
        elif settings.WEBDRIVER == "CHROME":
            self.DriverManager = ChromeDriverManager()
            self.options = webdriver.ChromeOptions()
            self.web_driver = webdriver.Chrome
        else:
            self.DriverManager = GeckoDriverManager()
            self.options = webdriver.FirefoxOptions()
            self.web_driver = webdriver.Firefox

        self.service = Service(executable_path=self.DriverManager.install())

        self.options.add_argument(f"--disable-blink-features={settings.DISABLE_BLINK_FEATURES}")
        self.options.add_argument(f"--user-agent={settings.USER_AGENT}")
        self.options.add_argument(f"--window-size={settings.WINDOW_SIZE}")
        self.options.page_load_strategy = settings.LOAD_STRATEGY
        if settings.NO_SANDBOX:
            self.options.add_argument(f"--no-sandbox")
        if settings.DISABLE_DEV_SHM_USAGE:
            self.options.add_argument(f"--disable-dev-shm-usage")
        if settings.HEADLESS:
            self.options.add_argument("--headless")
        if settings.DISABLE_CACHE:
            self.options.add_argument("--disable-cache")

    def initialize_driver(self) -> WebDriver:
        """Initializing and configuring the web browser driver."""
        logger.info("Initializing web driver")
        return self.web_driver(service=self.service, options=self.options)

    def send_image_to_translator(self, driver: WebDriver, photo_path: str) -> None:
        logger.info(f"Sending image to translator, photo: {photo_path}")
        driver.get(self.HOST)

        input_file = driver.find_element(*self.INPUT_FILE)
        input_file.send_keys(photo_path)
        sleep(1)

    def press_open_as_text(self, driver: webdriver):
        sleep(1)
        btn = driver.find_element(*self.OPEN_AS_TEXT)
        btn.click()
        sleep(1)

    def scrape_text_from_input(self, driver: WebDriver) -> str:
        sleep(1)
        span = driver.find_element(*self.SPAN_TEXT)
        text = span.get_attribute("innerHTML")

        return text

    def parse_text_from_image(self, photo_path: str) -> str:
        driver = self.initialize_driver()
        self.send_image_to_translator(driver, photo_path)
        self.press_open_as_text(driver)
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])
        text = self.scrape_text_from_input(driver)
        driver.close()

        return text
