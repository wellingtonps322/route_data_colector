from entities.pages.page_tools.page_tools import PageTools

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from time import sleep


class RouteDetailPageTools(PageTools):
    def __init__(self, driver):
        super().__init__(driver)
        self.attempt_get_route_number_counter = 0

    def handle_element_not_found(self, func):
        try:
            return func()
        except NoSuchElementException:
            # Handle the element not found error here
            return None

################ * SELENIUM ELEMENT ####################

    def getValueRouteTooltip(self):  # !Checking
        route_tooltip = self.handle_element_not_found(self.getServiceType())
        if route_tooltip:
            return f'"{route_tooltip}"'
        return 'NULL'

################### * BS ELEMENT #######################

    def canExtractDataFromRouteDetailPage(self):
        try:
            # html_page = WebDriverWait(self.driver, 5, 1, TimeoutException).until(
            #     EC.visibility_of_element_located(locator=(By.XPATH, "//ul//li//div[starts-with(@class, 'stops-list-id-wrapper__number')]")))
            html_page = WebDriverWait(self.driver, 10, 1, TimeoutException).until(
                EC.visibility_of_element_located(locator=(By.XPATH, "//ul//li")))
            return True
        except TimeoutException as e:
            page_source = self.driver.page_source
            page = BeautifulSoup(page_source, 'html.parser')
            heading_checking = page.find(
                'h2', {'class': 'andes-typography andes-technical-error__title andes-typography--type-title andes-typography--size-m andes-typography--color-primary andes-typography--weight-regular'})
            if heading_checking:
                self.driver.refresh()
            return False

    def isRouteDetailPageActive(self):
        try:
            html_page = WebDriverWait(self.driver, 10, 1, TimeoutException).until(
                EC.visibility_of_element_located(locator=(By.XPATH, '//*[@class="route-information-status"]/div/p[1]')))
            return True
        except TimeoutException as e:
            page_source = self.driver.page_source
            page = BeautifulSoup(page_source, 'html.parser')
            heading_checking = page.find(
                'h2', {'class': 'andes-typography andes-technical-error__title andes-typography--type-title andes-typography--size-m andes-typography--color-primary andes-typography--weight-regular'})
            if heading_checking:
                self.driver.refresh()
            return False

    def getRouteDetailSite(self):
        counter = 1
        while counter <= 3:
            try:
                html_page = WebDriverWait(self.driver, 30, 1, TimeoutException).until(
                    EC.visibility_of_element_located(locator=(By.XPATH, "//ul//li//div[starts-with(@class, 'stops-list-id-wrapper__number')]")))
                break
            except TimeoutException as e:
                counter += 1
        route_detail_page_content = self.driver.page_source
        return BeautifulSoup(
            route_detail_page_content, 'html.parser')

    def getRouteDetailInformationData(self):
        element = self.handle_element_not_found(
            lambda: self.getRouteDetailSite().find(
                'div', attrs={'class': 'route-information-block left'}))
        return element

    def getRouteStatus(self):
        attempts = 0
        checking = False
        continue_loop = True
        while checking == False and continue_loop == True:
            checking = self.isRouteDetailPageActive()
            attempts += 1
            if attempts == 5:
                self.closeWindow()
                return 'NULL'

        route_information_block = self.getRouteDetailInformationData()
        route_status = route_information_block.find(
            'div', attrs={'class': 'route-information-status'}).find_all('p')[0].text
        return f'"{route_status}"'

    def getRouteObservation(self):
        route_information_block = self.getRouteDetailInformationData()
        route_observation = route_information_block.find(
            'div', attrs={'class': 'route-information-status'}).find_all('p')[1].text

        if route_observation:
            return f'"{route_observation}"'
        return 'NULL'

    def getServiceCenter(self):
        # Add a wait element
        page = self.getHTML_bs()

        service_center = page.find(
            'div', attrs={'class': 'sc-header-container'}).find('strong').text

        if service_center:
            return f'"{service_center}"'
        return 'NULL'

    def getDriverName(self):
        # Add a wait element
        route_information_block = self.getRouteDetailInformationData()
        driver_name = route_information_block.find(
            'p', attrs={'class': 'route-information-item__info'}).text
        driver_name = driver_name.strip()

        if driver_name:
            return f'"{driver_name.upper()}"'
        return 'NULL'

    def getRouteNumber(self):
        # Add a wait element
        route_number = 'NULL'

        attempts = 0
        while attempts <= 30:
            route_information_block = self.getRouteDetailInformationData()
            try:
                route_number = route_information_block.find(
                    'div', attrs={'class': 'route-tooltip'}).find_all('span')[0].text
                route_number = route_number.split(sep=':')[1].strip()
                if route_number:
                    if route_number.isnumeric():
                        return int(route_number)

            except AttributeError as e:
                # Tratamento para quando o código não conseguiu obter o HTML completo por uma demora do servidor da página
                # Caso isso ocorra, o script chamará a função de obter o número da rota novamente até 30 vezes que equivale a 30 segundos
                sleep(1)

        return 'NULL'

    def getServiceType(self):
        # Add a wait element
        route_information_block = self.getRouteDetailInformationData()
        service_type = route_information_block.find(
            'div', attrs={'class': 'route-tooltip'}).find_all('span')[1].text
        service_type = service_type.split(sep='|')[0].strip()

        if service_type:
            return f'"{service_type}"'
        return 'NULL'

    def getLicensePlate(self):
        # Add a wait element
        route_information_block = self.getRouteDetailInformationData()
        service_type = route_information_block.find(
            'div', attrs={'class': 'route-tooltip'}).find_all('span')[1].text
        license_plate = service_type.split(sep='|')[1].strip()

        if not ("Error" in license_plate) and len(license_plate) == 7:
            return f'"{license_plate}"'
        return 'NULL'

    def getRouteDetailSummaryData(self):
        return self.handle_element_not_found(
            lambda: self.getRouteDetailSite().find_all(
                'div', attrs={'class': 'route-information-block'})[1])

    def getDeliveredPercent(self):
        route_information_block = self.getRouteDetailSummaryData()
        element = route_information_block.find(
            'div', attrs={'class': 'chart-details-data'})
        delivered_percent = element.find_all(
            'div', attrs={'class': 'chart-details-data__value-item'})[0].text
        delivered_percent = delivered_percent.split()[0].replace(',', '.')
        if delivered_percent.isnumeric:
            return float(delivered_percent)
        return 'NULL'

    def getDeliveryFailurePercent(self):
        route_information_block = self.getRouteDetailSummaryData()
        element = route_information_block.find(
            'div', attrs={'class': 'chart-details-data'})
        delivery_failure_percent = element.find_all(
            'div', attrs={'class': 'chart-details-data__value-item'})[1].text
        delivery_failure_percent = delivery_failure_percent.split()[
            0].replace(',', '.')
        if delivery_failure_percent.isnumeric:
            delivery_failure_percent = float(delivery_failure_percent)
            if delivery_failure_percent != 0.0:
                return delivery_failure_percent
        return 'NULL'

    def getPendingPercent(self):
        route_information_block = self.getRouteDetailSummaryData()
        element = route_information_block.find(
            'div', attrs={'class': 'chart-details-data'})
        pending_percent = element.find_all(
            'div', attrs={'class': 'chart-details-data__value-item'})[2].text
        pending_percent = pending_percent.split()[0].replace(',', '.')
        if pending_percent.isnumeric:
            pending_percent = float(pending_percent)
            if pending_percent != 0.0:
                return pending_percent
        return 'NULL'

    def getReceivePackages(self):
        route_information_block = self.getRouteDetailSummaryData()
        element = route_information_block.find('div', attrs='toggle-closed')
        receive_packages = element.find_all(
            'div', attrs={'class': 'metric-box'})[0].find_all('div')[1].text
        receive_packages = receive_packages.split()[0]
        if receive_packages.isnumeric():
            receive_packages = int(receive_packages)
            if receive_packages != 0:
                return receive_packages
        return 'NULL'

    def getTransferredPackages(self):
        route_information_block = self.getRouteDetailSummaryData()
        element = route_information_block.find('div', attrs='toggle-closed')
        transferred_packages = element.find_all(
            'div', attrs={'class': 'metric-box'})[1].find_all('div')[1].text
        transferred_packages = transferred_packages.split()[0]
        if transferred_packages.isnumeric:
            transferred_packages = int(transferred_packages)
            if transferred_packages != 0:
                return transferred_packages
        return 'NULL'

    def getOutOfAreaDelivery(self):
        route_information_block = self.getRouteDetailSummaryData()
        element = route_information_block.find('div', attrs='toggle-closed')
        out_of_area_packages = element.find_all(
            'div', attrs={'class': 'metric-box'})[2].find_all('div')[1].text
        out_of_area_packages = out_of_area_packages.split()[0]
        if out_of_area_packages.isnumeric:
            out_of_area_packages = int(out_of_area_packages)
            if out_of_area_packages != 0:
                return out_of_area_packages
        return 'NULL'

    def getRoutesClaim(self):
        route_information_block = self.getRouteDetailSummaryData()
        element = route_information_block.find('div', attrs='toggle-closed')
        routes_claim = element.find_all(
            'div', attrs={'class': 'metric-box'})[3].find_all('div')[1].text
        routes_claim = routes_claim.split()[0]
        if routes_claim.isnumeric:
            routes_claim = int(routes_claim)
            if routes_claim != 0:
                return routes_claim
        return 'NULL'

    def getRouteDate(self):
        metric_box_elements = self.getRouteDetailInformationData().find_all(
            'div', attrs={'class': 'metric-box'})
        date_str = metric_box_elements[3].find(
            'div', attrs={'class': 'metric-box__value'}).text
        datetime = self.getDateConverter(date=date_str, type='all')
        return datetime

    def getStartHour(self):
        metric_box_elements = self.getRouteDetailInformationData().find_all(
            'div', attrs={'class': 'metric-box'})
        date_str = metric_box_elements[3].find(
            'div', attrs={'class': 'metric-box__value'}).text
        start_hour = self.getDateConverter(date=date_str, type='hour')
        return start_hour

    def getHourOnDeliveryZone(self):
        metric_box_elements = self.getRouteDetailInformationData().find_all(
            'div', attrs={'class': 'metric-box'})
        date_str = metric_box_elements[2].find(
            'div', attrs={'class': 'metric-box__value'}).text
        time = date_str.replace('h', '')

        if time:
            return f'"{time}"'
        return 'NULL'

    def getHourToDeliveryArea(self):
        metric_box_elements = self.getRouteDetailInformationData().find_all(
            'div', attrs={'class': 'metric-box'})
        date_str = metric_box_elements[1].find(
            'div', attrs={'class': 'metric-box__value'}).text
        time = date_str.replace('h', '')

        if time:
            return f'"{time}"'
        return 'NULL'

    def getOnRouteHour(self):
        metric_box_elements = self.getRouteDetailInformationData().find_all(
            'div', attrs={'class': 'metric-box'})
        date_str = metric_box_elements[0].find(
            'div', attrs={'class': 'metric-box__value'}).text
        time = date_str.replace('h', '')

        if time:
            return f'"{time}"'
        return 'NULL'

    def getStopsNumber(self):
        number = self.getRouteDetailSummaryData().find_all(
            'p', attrs={'class': 'route-information__value'})[0].text
        if number.isnumeric():
            return int(number)
        return 'NULL'

    def getPointsNumber(self):
        number = self.getRouteDetailSummaryData().find_all(
            'p', attrs={'class': 'route-information__value'})[1].text
        if number.isnumeric():
            return int(number)
        return 'NULL'

    def getIndividualPackagesNumber(self):
        number = self.getRouteDetailSummaryData().find_all(
            'p', attrs={'class': 'route-information__value'})[2].text
        if number.isnumeric():
            return int(number)
        return 'NULL'

    def getIndividualBagsNumber(self):
        number = self.getRouteDetailSummaryData().find_all(
            'p', attrs={'class': 'route-information__value'})[3].text
        if number.isnumeric():
            number = int(number)
            if number != 0:
                return number
        return 'NULL'

    def getAdressElementList(self):
        return self.getRouteDetailSite().find(
            'ul', attrs={'class': 'andes-list andes-list--default andes-list--selectable'})

    def getStopElements(self):
        return self.getAdressElementList().find_all(
            'li', attrs={'class': 'andes-list__item stops__row andes-list__item--size-medium'})

    def getContainerElementsList(self):
        return self.getAdressElementList().find_all(
            'div', attrs={'class': 'order__container close'})

    def getStopNumber(self, element):
        number = element.select_one(
            'span[class^="stops-list-index-"]').text
        if number.isdigit():
            return int(number)  # ! Probably of return other values
        return 'NULL'

    def getStopAddress(self, element):
        address = element.find(
            'div', attrs={'class': 'stops-list-id-wrapper__number'}).text
        if '"' in address:
            address = address.replace('"', "")

        if address:
            return f'"{address}"'
        return 'NULL'

    def getStopPoints(self, element):
        number = element.find('div', attrs={'class': 'stops-list-id-wrapper__data'}).find_all(
            'span')[0].find('div').find('strong').get_text(strip=True)
        if number.isnumeric():
            return int(number)
        return 'NULL'

    def getStopPackages(self, element):
        number = element.find('div', attrs={
            'class': 'stops-list-id-wrapper__data'}).find_all('span')[1].find('div').find('strong').get_text(strip=True)
        if number.isnumeric():
            return int(number)
        return 'NULL'

    def getOrderLetter(self, element):
        order_letter = element.find(
            'div', attrs={'class': 'order__letter'}).text
        if order_letter:
            return f'"{order_letter}"'
        return 'NULL'

    def getOrderAddress(self, element):
        address = element.find(
            'p', attrs={'class': 'order__address'}).text
        if '"' in address:
            address = address.replace('"', "")
        if address:
            return f'"{address}"'
        return 'NULL'

    def getOrderAddressType(self, element):
        order_address_type = element.find(
            'p', attrs={'class': 'order__delivery'}).text
        if order_address_type:
            return f'"{order_address_type}"'
        return 'NULL'

    def getQuantityPackagesOnContainer(self, element):
        return len(element.find_all(
            'span', attrs={'class': 'transport-unit__data-id'}))

    def getPackageNumber(self, element, package):
        number = element.find_all(
            'span', attrs={'class': 'transport-unit__data-id'})[package].find('p').text.split()[1]
        if number.isdigit():
            return int(number)
        return 'NULL'

    def getPackageTag(self, element, package):
        try:
            tag = element.find_all(
                'span', attrs={'class': 'transport-unit__data-id'})[package].find('p').text.split()[4]
            if tag:
                return f'"{tag}"'
            return 'NULL'
        except IndexError as e:
            return 'NULL'
        except NoSuchElementException as e:
            print(f'Error: {e}')
            return 'NULL'

    def getPackageStatus(self, element, package):
        try:
            package_container = element.find_all(
                'span', attrs={'class': 'transport-unit__data-id'})[package].parent
            status = package_container.find(
                'span', attrs={'class': 'transport-unit__data-state'}).text
            if status:
                return f'"{status}"'
            return 'NULL'
        except NoSuchElementException as e:
            print(f'Error: {e}')
            return 'NULL'

    def getPackageFlag(self, element, package):
        try:
            package_container = element.find_all(
                'span', attrs={'class': 'transport-unit__data-id'})[package].parent
            flag = package_container.find(
                'span', attrs={'class': 'transport-unit__data--flag'}).text
            if flag:
                if flag != '':
                    return f'"{flag}"'
            return 'NULL'
        except NoSuchElementException as e:
            print(f'Error: {e}')
            return 'NULL'
