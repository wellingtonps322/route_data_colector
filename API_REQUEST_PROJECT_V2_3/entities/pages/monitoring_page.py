from entities.pages.page import Page
from entities.pages.page_tools.monitoring_page_tools import MonitoringPageTools
from entities.pages.route_detail_page import RouteDetailPage
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, TimeoutException

from entities.vehicle import Vehicle
from entities.driver import Driver


class MonitoringPage(Page):

    def __init__(self, updater: object, reader: object, recorder: object, driver: dict = None) -> None:
        super().__init__()
        if driver:
            self.driver = driver
        self.tools = MonitoringPageTools(driver=self.driver)
        self.reader = reader
        self.updater = updater
        self.recorder = recorder
        self.route_detail_page = RouteDetailPage(
            driver=self.driver, reader=self.reader, updater=self.updater, recorder=self.recorder)

    def getData(self, service_center_list: list, main_window: str):
        for service_center in service_center_list:

            self.driver.switch_to.window(main_window)

            attempts = 0
            while True:
                # Tentar alterar a página duas vezes, se não conseguir finalizar a execução da busca de rotas
                try:
                    if not self.tools.serviceCenterChecking(service_center=service_center):
                        self.tools.setWindowServiceCenter(
                            service_center=service_center)
                    break
                except (ElementClickInterceptedException, TimeoutError, TimeoutException):
                    if attempts > 2:
                        # Se já tiver excedido o número de tentativas, o script irá parar e retornar no próximo horário agendado
                        return
                    self.driver.refresh()
                    attempts += 1

            route_data_dict = {
                'service_center': None,
                'employee_type': 'driver',
                'delivered_packages': None,
                'pending_delivery_packages': None,
                'delivery_failure_packages': None,
                'route_status': None,
                'route_observation': None
            }

            current_window = self.driver.current_window_handle

            if self.tools.getRouteRowElement():

                route_number_list = self.tools.getAllRouteNumbers()

                for route_number in route_number_list:
                    if route_number != "NULL":

                        self.driver.switch_to.window(current_window)

                        # ? Check if the route already finished
                        result = self.reader.getRouteDataByRouteNumber(
                            route_number=route_number)
                        if result and result[8] == 'Concluída':
                            print(f'Route {result[1]} already up to date')
                            continue

                        # ? Searching route element by route number
                        try:
                            row_element = self.tools.find_element_by_text(
                                "p", route_number)
                        except NoSuchElementException as e:
                            print(
                                f"PROBABLY ROUTE {route_number} WAS DELETED, CHECK IT")
                            continue

                        monitoring_row_element = self.tools.get_parent_element(
                            element=row_element, parent_class="monitoring-row", tag="li")

                        route_data_dict.clear()

                        # * Route data
                        route_data_dict['service_center'] = f'"{
                            service_center["service_center"]}"'
                        route_data_dict['route_number'] = route_number
                        route_data_dict['license_plate'] = self.tools.getLicensePlate(
                            monitoring_row_element)
                        route_data_dict['driver_name'] = self.tools.getDriverName(
                            monitoring_row_element)
                        route_data_dict['employee_type'] = self.tools.getWorkerType(
                            monitoring_row_element)
                        route_data_dict['delivered_packages'] = self.tools.getDeliveredPackages(
                            monitoring_row_element)
                        route_data_dict['delivery_failure_packages'] = self.tools.getDeliveryFailurePackages(
                            monitoring_row_element)
                        route_data_dict['pending_delivery_packages'] = self.tools.getPendingDeliveryPackages(
                            monitoring_row_element)
                        route_data_dict['route_status'] = self.tools.getRouteStatus(
                            monitoring_row_element)
                        route_data_dict['route_observation'] = self.tools.getRouteObservation(
                            monitoring_row_element)

                        monitoring_rows = self.tools.getRowElementList()  # Find the rotes list

                        try:
                            # Clicking in the rote
                            row_element.click()
                        except IndexError as e:
                            print(f'{e.__class__.__name__}')
                            print(f'{e}')
                            continue
                        except ElementClickInterceptedException as e:
                            try:
                                # Se houver algum problema de pop-up de cookies e o selenium nào conseguir enxergar o elemento, ele irá rolar a página até o mesmo
                                self.driver.execute_script(
                                    "arguments[0].scrollIntoView(true);", row_element)

                                # Clicking in the rote
                                row_element.click()
                            except ElementClickInterceptedException as e:
                                print(f'{e.__class__.__name__}')
                                print(f'{e}')
                                print(f'{e.__cause__}')
                                continue

                        try:
                            # ? ROUTE DETAIL PAGE
                            route_detail_data_dict = self.route_detail_page.getRouteDetailData(
                                service='search')
                            if route_detail_data_dict == 'Error':
                                print(
                                    f"Route {route_data_dict['route_number']} hasn't founded")
                                continue
                            if route_detail_data_dict == None:
                                print('Route already up to date')
                                continue

                        except TimeoutError as e:
                            print(f'{e.__class__.__name__}')
                            print(f'{e}')
                            continue

                        route_data_dict['route_date'] = route_detail_data_dict['route_date']
                        route_data_dict['hourOnDeliveryZone'] = route_detail_data_dict['hourOnDeliveryZone']
                        route_data_dict['hourToDeliveryArea'] = route_detail_data_dict['hourToDeliveryArea']
                        route_data_dict['onRouteHour'] = route_detail_data_dict['onRouteHour']
                        route_data_dict['startHourRoute'] = route_detail_data_dict['startHourRoute']
                        route_data_dict['service_type'] = route_detail_data_dict['service_type']
                        route_data_dict['stops_number'] = route_detail_data_dict['stops_number']
                        route_data_dict['points_number'] = route_detail_data_dict['points_number']
                        route_data_dict['individual_packages_number'] = route_detail_data_dict['individual_packages_number']
                        route_data_dict['individual_bags_number'] = route_detail_data_dict['individual_bags_number']
                        route_data_dict['stops_list'] = route_detail_data_dict['stops_list']
                        route_data_dict['delivered_percent'] = route_detail_data_dict['delivered_percent']
                        route_data_dict['delivery_failure_percent'] = route_detail_data_dict['delivery_failure_percent']
                        route_data_dict['pending_percent'] = route_detail_data_dict['pending_percent']
                        route_data_dict['receive_packages'] = route_detail_data_dict['receive_packages']
                        route_data_dict['transferred_packages'] = route_detail_data_dict['transferred_packages']
                        route_data_dict['out_of_area_delivery'] = route_detail_data_dict['out_of_area_delivery']
                        route_data_dict['routes_claim'] = route_detail_data_dict['routes_claim']

                        self.updater.setRouteDataUpdate(
                            route_data=route_data_dict)

                        # * Creating or updating vehicle data
                        vehicle_data = {
                            'license_plate': route_data_dict['license_plate'],
                            'service_center': route_data_dict['service_center'],
                            'last_route': route_data_dict['route_date'],
                            'service_type': route_data_dict['service_type'],
                            'driver': route_data_dict['driver_name']
                        }

                        if not ("Error" in vehicle_data['license_plate']) and len(vehicle_data['license_plate']) == 9:

                            vehicle = Vehicle(
                                vehicle_data=vehicle_data, recorder=self.recorder, reader=self.reader, updater=self.updater)
                            vehicle.isVehicleExists()

                        # * Creating or updating employee data
                        driver_data = {
                            'id_driver': 'NULL',
                            'driver_name': route_data_dict['driver_name'],
                            'service_center': route_data_dict['service_center'],
                            'license_plate': route_data_dict['license_plate'],
                            'last_route': route_data_dict['route_date'],
                            'service_type': route_data_dict['service_type'],
                        }
                        if driver_data['driver_name'] != '"-"':
                            driver = Driver(
                                driver_data=driver_data, recorder=self.recorder, reader=self.reader, updater=self.updater)
                            driver.isDriverExists()

            print('NEXT SERVICE CENTER')
