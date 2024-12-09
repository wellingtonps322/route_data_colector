from datetime import datetime

from entities.pages.page import Page
from entities.pages.page_tools.route_detail_page_tools import RouteDetailPageTools
from entities.vehicle import Vehicle
from entities.driver import Driver
from entities.pages.login_page import LoginPage

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class RouteDetailPage(Page):
    def __init__(self, driver: object, reader: object, updater: object, recorder: object):
        super().__init__()
        self.driver = driver
        self.tools = RouteDetailPageTools(driver=driver)
        self.reader = reader
        self.updater = updater
        self.recorder = recorder

    def login_at_silos(self) -> bool:

        login_page = LoginPage()

        response = login_page.login(username='ext_wellwell',
                                    password='8905KASVwjfl-_..', driver=self.driver)

        return response

    def is_logged(self):
        CURRENT_URL = self.driver.current_url

        if 'https://envios.adminml.com/logistics/monitoring-distribution/detail/' in CURRENT_URL:
            return True
        return False

    def wait_to_route_detail_page(self):
        try:
            html_page = WebDriverWait(self.driver, 10, 1, TimeoutException).until(
                EC.title_contains('Detalhe de Rota'))
            return True
        except TimeoutException as e:
            return False

    def getRouteDetailData(self, service: str) -> dict:
        #!Check if it has more than one tab open to Change window focus
        self.tools.changeWindowFocus(1)

        # * Checando se a conta no silos está logada
        if not self.is_logged():
            self.login_at_silos()

            response = self.wait_to_route_detail_page()

            if not response:
                return 'Error'

        # * Checando se a página com os dados da rota foi carregada
        # ! Aprimorar essa checagem quando houver erro de carregamento e quando a página não existir
        attempts = 0
        checking = False
        continue_loop = True
        while checking == False and continue_loop == True:
            checking = self.tools.canExtractDataFromRouteDetailPage()
            attempts += 1
            if attempts == 4:
                self.tools.closeWindow()
                return 'Error'

        stop_dict = dict()
        individual_points_list = list()
        points_list = list()
        point_dict = dict()
        packages_list = list()
        package_data_dict = dict()
        stops_list = list()

        # Header data
        route_status = self.tools.getRouteStatus()
        service_center = self.tools.getServiceCenter()
        driver_name = self.tools.getDriverName()
        route_number = self.tools.getRouteNumber()
        license_plate = self.tools.getLicensePlate()
        route_date = f'"{self.tools.getRouteDate().strftime("%d/%m/%Y")}"'
        star_hour_route = f'"{self.tools.getStartHour().strftime("%H:%M:%S")}"'
        hourOnDeliveryZone = self.tools.getHourOnDeliveryZone()
        hourToDeliveryArea = self.tools.getHourToDeliveryArea()
        onRouteHour = self.tools.getOnRouteHour()
        service_type = self.tools.getServiceType()
        route_observation = self.tools.getRouteObservation()
        stops_number = self.tools.getStopsNumber()
        points_number = self.tools.getPointsNumber()
        individual_packages_number = self.tools.getIndividualPackagesNumber()
        individual_bags_number = self.tools.getIndividualBagsNumber()
        delivered_percent = self.tools.getDeliveredPercent()
        delivery_failure_percent = self.tools.getDeliveryFailurePercent()
        pending_percent = self.tools.getPendingPercent()
        receive_packages = self.tools.getReceivePackages()
        transferred_packages = self.tools.getTransferredPackages()
        out_of_area_delivery = self.tools.getOutOfAreaDelivery()
        routes_claim = self.tools.getRoutesClaim()

        position = 0
        for position, stop_element in enumerate(self.tools.getStopElements()):

            stop_number = self.tools.getStopNumber(
                stop_element)
            stop_address = self.tools.getStopAddress(
                stop_element)
            stop_points = self.tools.getStopPoints(
                stop_element)
            stop_packages = self.tools.getStopPackages(
                stop_element)
            stop_dict = {'stop_number': stop_number,
                         'stop_address': stop_address,
                         'stop_points': stop_points,
                         'stop_packages': stop_packages,
                         'individual_points_list': individual_points_list[:]}

            stops_list.append(stop_dict)

        position = 0
        point_dict.clear()
        for position, container_element in enumerate(self.tools.getContainerElementsList()):
            #! point_dict.clear() To clear and no add duplicated data
            order_letter = self.tools.getOrderLetter(
                container_element)
            order_address = self.tools.getOrderAddress(
                container_element)
            order_address_type = self.tools.getOrderAddressType(
                container_element)

            quantity_packages_on_container = self.tools.getQuantityPackagesOnContainer(
                container_element)

            init_package = 0  # Auxiliary variable to identify the current package to add
            packages_list.clear()
            for package in range(init_package, (quantity_packages_on_container)):

                package_data_dict.clear()

                package_data_dict['package_number'] = self.tools.getPackageNumber(
                    container_element, package)
                package_data_dict['tag'] = self.tools.getPackageTag(
                    container_element, package)
                package_data_dict['status'] = self.tools.getPackageStatus(
                    container_element, package)
                package_data_dict['flag'] = self.tools.getPackageFlag(
                    container_element, package)

                packages_list.append(package_data_dict.copy())

            point_dict = {'order_letter': order_letter,
                          'order_address': order_address,
                          'order_address_type': order_address_type,
                          'packages_list': packages_list[:]}
            points_list.append(point_dict)

        for stop_list in stops_list:  # ! The list transform yourself in a dictonary
            for point_list in points_list:  # ! The list transform yourself in a dictonary
                if point_list:
                    if point_list['order_address'] in stop_list['stop_address']:
                        stop_list['individual_points_list'].append(
                            point_list.copy())

        # last_update = datetime.now()
        #!Check if it has more than one tab open to close window
        self.tools.closeWindow()
        #!Check if it has more than one tab open to Change window focus

        # When request all service center data
        if service == 'search':
            return {
                'service_center': service_center,
                'driver_name': driver_name,
                'route_number': route_number,
                'license_plate': license_plate,
                'route_date': route_date,
                'hourOnDeliveryZone': hourOnDeliveryZone,
                'hourToDeliveryArea': hourToDeliveryArea,
                'onRouteHour': onRouteHour,
                'startHourRoute': star_hour_route,
                'service_type': service_type,
                'stops_number': stops_number,
                'points_number': points_number,
                'individual_packages_number': individual_packages_number,
                'individual_bags_number': individual_bags_number,
                'delivered_percent': delivered_percent,
                'delivery_failure_percent': delivery_failure_percent,
                'pending_percent': pending_percent,
                'receive_packages': receive_packages,
                'transferred_packages': transferred_packages,
                'out_of_area_delivery': out_of_area_delivery,
                'routes_claim': routes_claim,
                'stops_list': stops_list,
            }
        # When requests some routes
        if service == 'new':
            total_packages_route = (individual_packages_number if individual_packages_number != 'NULL' else 0) + (individual_bags_number if individual_bags_number !=
                                                                                                                  'NULL' else 0) + (receive_packages if receive_packages != 'NULL' else 0) - (transferred_packages if transferred_packages != 'NULL' else 0)

            return {
                'service_center': service_center,
                'driver_name': driver_name,
                'route_number': route_number,
                'license_plate': license_plate,
                'employee_type': '"Driver"',
                # * Checking
                'delivered_packages': round(total_packages_route * (delivered_percent / 100)),
                # * Checking
                'delivery_failure_packages': round(total_packages_route * ((delivery_failure_percent if delivery_failure_percent != 'NULL' else 0) / 100)),
                # * Checking
                'pending_delivery_packages': round(total_packages_route * ((pending_percent if pending_percent != 'NULL' else 0) / 100)),
                'route_date': route_date,
                'hourOnDeliveryZone': hourOnDeliveryZone,
                'hourToDeliveryArea': hourToDeliveryArea,
                'onRouteHour': onRouteHour,
                'startHourRoute': star_hour_route,
                'service_type': service_type,
                'route_status': route_status,
                'route_observation': route_observation,
                'stops_number': stops_number,
                'points_number': points_number,
                'individual_packages_number': individual_packages_number,
                'individual_bags_number': individual_bags_number,
                'delivered_percent': delivered_percent,
                'delivery_failure_percent': delivery_failure_percent,
                'pending_percent': pending_percent,
                'receive_packages': receive_packages,
                'transferred_packages': transferred_packages,
                'out_of_area_delivery': out_of_area_delivery,
                'routes_claim': routes_claim,
                'stops_list': stops_list,
            }

    def getDataByRouteNumber(self, route_number_list: list, webdriver: set) -> bool:
        if route_number_list != None:

            for route_number in route_number_list:
                route_data = self.reader.getRouteDataByRouteNumber(
                    route_number=route_number)

                if route_data and route_data:
                    if 'Concluída' in route_data[8]:
                        print(f'Route {route_number} already up to date')
                        continue

                webdriver.get(
                    f'https://envios.adminml.com/logistics/monitoring-distribution/detail/{route_number}?site=MLB')

                route_detail_data_dict = self.getRouteDetailData(
                    service='new')

                if route_detail_data_dict == 'Error':
                    print(f"Route {route_number} hasn't founded")
                    continue

                if route_detail_data_dict == None:
                    continue

                #! Check if data already exists and ask if you want to overwrite the data
                self.updater.setRouteDataUpdate(
                    route_data=route_detail_data_dict)

                # * Creating or updating vehicle data
                vehicle_data = {
                    'license_plate': route_detail_data_dict['license_plate'],
                    'service_center': route_detail_data_dict['service_center'],
                    'last_route': route_detail_data_dict['route_date'],
                    'service_type': route_detail_data_dict['service_type'],
                    'driver': route_detail_data_dict['driver_name']
                }

                if not ("Error" in vehicle_data['license_plate']) and len(vehicle_data['license_plate']) == 9:

                    vehicle = Vehicle(
                        vehicle_data=vehicle_data, recorder=self.recorder, reader=self.reader, updater=self.updater)
                    vehicle.isVehicleExists()

                # * Creating or updating employee data
                driver_data = {
                    'id_driver': 'NULL',
                    'driver_name': route_detail_data_dict['driver_name'],
                    'service_center': route_detail_data_dict['service_center'],
                    'license_plate': route_detail_data_dict['license_plate'],
                    'last_route': route_detail_data_dict['route_date'],
                    'service_type': route_detail_data_dict['service_type'],
                }
                if driver_data['driver_name'] != '"-"':

                    driver = Driver(
                        driver_data=driver_data, recorder=self.recorder, reader=self.reader, updater=self.updater)
                    driver.isDriverExists()

            # else:
            #     print(f'ERRO: O número de rota {route_number} é inválido!')
        else:
            print('Insira os números da rota')

    def getDataByDate(self, webdriver: set, date: datetime = None) -> bool:
        if date is not None:

            route_data = self.reader.getRouteDataByDate(
                date=date.strftime("%d/%m/%Y"))
            if route_data:
                route_number_list = [route[1] for route in route_data]
                self.getDataByRouteNumber(
                    route_number_list=route_number_list, webdriver=webdriver)
            else:
                print('Do not exist routes to this day')
