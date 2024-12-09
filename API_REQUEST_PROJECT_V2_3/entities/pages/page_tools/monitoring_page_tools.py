from entities.pages.page_tools.page_tools import PageTools

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from time import sleep


class MonitoringPageTools(PageTools):
    def __init__(self, driver):
        super().__init__(driver)

    def setWindowServiceCenter(self, service_center: dict):
        # * Use this variable to checking
        html_page = WebDriverWait(self.driver, 30, 1).until(
            EC.visibility_of_element_located(locator=(By.XPATH, "/html/body/header/div//button")))
        sleep(1)

        self.serviceCenterChecking(service_center=service_center)

        self.click_element_by_xpath("/html/body/header/div//button")
        # * Use this variable to checking
        html_page = WebDriverWait(self.driver, 120, 1, ).until(
            EC.visibility_of_element_located(locator=(By.XPATH, "//*[@id='remote-module-container-kraken-frm-provider-attributesregion-default']/div/button")))
        self.click_element_by_xpath(
            "//*[@id='remote-module-container-kraken-frm-provider-attributesregion-default']/div/button")
        self.write_xpath("//*[@id='search-field']", service_center['region'])
        self.click_element_by_xpath(
            "/html/body//div[@class='andes-modal__overlay andes-modal__overlay--card']//div[@class='appNav__modal_wrapper--content__module'][2]//div[@class='search--results']/..//ul/li[1]")
        self.write_xpath("/html/body//div[@class='andes-modal__overlay andes-modal__overlay--card']//div[@class='appNav__modal_wrapper--content__module'][3]//div[@class='search-area']/input",
                         service_center['service_center'])
        self.click_element_by_xpath(
            "/html/body//div[@class='andes-modal__overlay andes-modal__overlay--card']//div[@class='appNav__modal_wrapper--content__module'][3]//div[@class='search--results']/..//ul/li[1]")
        self.click_element_by_xpath(
            "//div[@class='andes-modal__overlay andes-modal__overlay--card']//button[@type='submit']")

    def serviceCenterChecking(self, service_center: dict):

        html_page = WebDriverWait(self.driver, 60, 1, ).until(
            EC.visibility_of_element_located(locator=(By.XPATH, "/html/body/header/div//button")))
        result = self.checkingTextInElement(
            text=service_center['service_center'], xpath="/html/body/header/div//button")
        return result

    def getRowElementList(self):
        # row_elements = self.driver.current_window_handle().find_elements(
        #     By.CLASS_NAME, 'monitoring-row')
        row_elements = self.driver.find_elements(
            By.CLASS_NAME, 'monitoring-row')
        return row_elements

    def handle_element_not_found(self, func):
        try:
            return func()
        except NoSuchElementException:
            # Handle the element not found error here
            return 'Error'
        except AttributeError:
            return 'Error'

    ################### * BS ELEMENT #######################

    def getRouteRowElement(self):
        try:
            html_page = WebDriverWait(self.driver, 30, 1).until(
                EC.visibility_of_element_located(locator=(By.XPATH, "//ul//li//p[@class='monitoring-row-shipments__packages']")))
            return self.getHTML_bs().find_all('div', attrs={'class': 'row-link'})
        except TimeoutException as e:
            print(e.__class__.__class__)
            print(e)
            return None

    def getAllRouteNumbers(self):
        try:
            html_page = WebDriverWait(self.driver, 30, 1).until(
                EC.visibility_of_element_located(locator=(By.XPATH, "//ul//li//p[@class='monitoring-row-shipments__packages']")))

            route_number_elements = self.getHTML_bs().find_all(
                'p', attrs={'class': 'monitoring-row__bold'})

            route_number_list = [
                route_number_element
                .get_text(strip=True)
                .split()[-1]
                .replace('#', '') for route_number_element in route_number_elements]

            route_number_list = [
                int(route_number) if route_number.isnumeric() else "NULL"
                for route_number in route_number_list]

            return route_number_list

        except NoSuchElementException as e:
            print(e.__class__.__class__)
            print(e)
            return None

    def getRouteNumber(self, element):
        number = element.find(
            'p', attrs={'class': 'monitoring-row__bold'}).get_text(strip=True).split()[-1].replace('#', '')
        if number.isnumeric():
            return int(number)
        if not number:
            print('Route number is None')
            return 'NULL'
        return 'NULL'

    def getLicensePlate(self, element):
        license_plate = self.handle_element_not_found(
            lambda: element.find(
                'p', attrs={'class': 'monitoring-row-details__license'}).get_text(strip=True))
        if license_plate:
            license_plate = license_plate.split(sep='|')[0].strip()
            return f'"{license_plate}"'
        if not license_plate:
            print('License plate is None')
            return 'NULL'

    def getDriverName(self, element):
        driver_name = self.handle_element_not_found(
            lambda: element.find(
                'p', attrs={'class': 'monitoring-row-details__driver-name'}).get_text(strip=True))
        if driver_name:
            return f'"{driver_name.upper()}"'
        return 'NULL'

    def getWorkerType(self, element):
        worker_type = self.handle_element_not_found(
            lambda: element.find(
                'p', attrs={'class': 'andes-badge__content'}).get_text(strip=True))
        if worker_type:
            return f'"{worker_type}"'
        return 'NULL'

    def getRoutePercent(self, element):
        number = element.find('div', attrs={
            # + '%'
            'class': 'sc-progress-wheel__percentage'}).find('p').get_text(strip=True)
        if number.isnumeric():
            return float(number)
        return 'NULL'

    def getDeliveredPackages(self, element):
        number = element.find_all(
            'div', attrs={'class': 'monitoring-row-shipments__delivered-packages-text'})[0].find('strong').get_text(strip=True)
        if number.isnumeric():
            return int(number)
        return 'NULL'

    def getDeliveryFailurePackages(self, element):
        number = element.find_all(
            'div', attrs={'class': 'monitoring-row-shipments__delivered-packages-text'})[1].find('strong').get_text(strip=True)
        if number.isnumeric():
            return int(number)
        return 'NULL'

    def getPendingDeliveryPackages(self, element):
        number = element.find('p', attrs={
            'class': 'monitoring-row-shipments__packages'}).find('div').find('strong').get_text(strip=True)
        if number.isnumeric():
            return int(number)
        return 'NULL'

    def getRouteStatus(self, element):
        status = element.find(
            'p', attrs={'class': 'monitoring-row-details__name'}).get_text(strip=True)
        if status:
            return f'"{status}"'
        return 'NULL'

    def getRouteObservation(self, element):
        observation = element.find(
            'p', attrs={'class': 'monitoring-row-details__untracked'}).get_text(strip=True)
        if observation:
            return f'"{observation}"'
        return 'NULL'
