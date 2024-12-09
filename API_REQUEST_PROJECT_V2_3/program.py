import datetime
import sched
import time
import sys

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from entities.pages.login_page import LoginPage
from entities.pages.monitoring_page import MonitoringPage
from entities.pages.route_detail_page import RouteDetailPage
from core.driver_factory import DriverFactory
from database.database import Database
from database.updater import Updater
from database.reader import Reader
from database.recorder import Recorder

# from datetime import datetime, timedelta


class Program():
    def __init__(self) -> None:
        self.driver = None

    def is_logged(self):
        current_url = self.driver.current_url

        if current_url == 'https://envios.adminml.com/logistics/monitoring-distribution':
            return True
        return False

    def login_at_silos(self) -> bool:

        login_page = LoginPage()

        response = login_page.login(username='****',
                                    password='****', driver=self.driver)

        return response

    def wait_to_monitoring_page(self):
        try:
            current_url = self.driver.current_url
            html_page = WebDriverWait(self.driver, 10, 1, TimeoutException).until(
                EC.url_matches("https://envios.adminml.com/logistics/monitoring-distribution"))
            return True
        except TimeoutException as e:
            return False

    def is_monitoring_page(self):
        self.driver = DriverFactory().getDriver()

        self.driver.get(
            'https://envios.adminml.com/logistics/monitoring-distribution')
        # Agora, sempre que precisar carregar a sessão, carregue os cookies do arquivo
        # Exemplo de como carregar os cookies em uma nova instância do driver:
        try:
            # ! Analisar se é antes ou depois do login
            with open('cookies.txt', 'r') as file:
                cookies = eval(file.read())
            for cookie in cookies:
                if cookie['domain'] == 'envios.adminml.com':
                    continue
                self.driver.add_cookie(cookie)
        except FileNotFoundError:
            ...

        self.driver.get(
            'https://envios.adminml.com/logistics/monitoring-distribution')
        is_logged = self.is_logged()

        if not is_logged:
            response = self.login_at_silos()
            if not response:
                print("Having trouble to connect at Logistics")
                return False

        response = self.wait_to_monitoring_page()

        if response:
            # Após o login, obtenha todos os cookies da sessão atual
            cookies = self.driver.get_cookies()

            # Salve os cookies em um arquivo
            with open('cookies.txt', 'w') as file:
                file.write(str(cookies))

            return True
        else:
            return

    def getAllRouteInformations(self, service_center_list: list):
        try:
            print('Starting route search')
            if service_center_list != None:

                response = self.is_monitoring_page()

                if not response:
                    return

                database = Database()
                recorder = Recorder(database)
                reader = Reader(database)
                updater = Updater(database=database, reader=reader)
                monitoring_page = MonitoringPage(
                    updater=updater, reader=reader, recorder=recorder, driver=self.driver)

                main_window = self.driver.current_window_handle

                monitoring_page.getData(
                    service_center_list=service_center_list, main_window=main_window)
            else:
                print('Insira o código referente ao service center a ser pesquisado.')

            if self.driver:
                self.driver.quit()
                del self.driver
            print('End time', datetime.datetime.now())
            print('All routes was inserted')

        except SyntaxError as e:
            print('Error time', datetime.datetime.now())
            print(e.__class__.__name__)
            print(e.__cause__)
            print(e)

        except TimeoutException as e:
            print('Error time', datetime.datetime.now())
            print(e.__class__.__name__)
            print(e.__cause__)

    def updateRouteInformationsByRouteNumber(self, route_number_list: list):

        response = self.is_monitoring_page()

        if not response:
            return

        database = Database()
        recorder = Recorder(database)
        reader = Reader(database)
        updater = Updater(database=database, reader=reader)
        route_detail_page = RouteDetailPage(
            self.driver, reader=reader, updater=updater, recorder=recorder)
        route_detail_page.getDataByRouteNumber(
            route_number_list=route_number_list, webdriver=self.driver)
        if self.driver:
            self.driver.quit()
            del self.driver

    def updateRouteInformationsByDate(self, date: datetime = None):

        response = self.is_monitoring_page()

        if not response:
            return

        database = Database()
        reader = Reader(database)
        recorder = Recorder(database)
        updater = Updater(database=database, reader=reader)
        route_detail_page = RouteDetailPage(
            self.driver, reader=reader, updater=updater, recorder=recorder)
        route_detail_page.getDataByDate(date=date, webdriver=self.driver)
        if self.driver:
            self.driver.quit()
            del self.driver

        print('End time', datetime.datetime.now())


#! Change to variable from Move System Application Data
service_center_names = [
    # {'region': 'SPC', 'service_center': 'SSP5'},
    # {'region': 'SPC', 'service_center': 'SSP7'},
    {'region': 'SPISUL', 'service_center': 'SSP10'},
    {'region': 'SPISUL', 'service_center': 'SSP12'},
    {'region': 'SPC', 'service_center': 'SSP21'},
    {'region': 'SPC', 'service_center': 'SSP25'},
    {'region': 'MEGAS UTR', 'service_center': 'SSP30'},
    {'region': 'MEGAS UTR', 'service_center': 'SSP33'},
    {'region': 'SPC', 'service_center': 'SSP43'},
]

route_number_list = []



def getIsNewDate(date_str: str) -> datetime:
    date = datetime.datetime.strptime(date_str, '%d/%m/%Y')
    return date


def getAllRoutes():
    application = Program()
    application.getAllRouteInformations(service_center_names)


date = getIsNewDate('27/12/2023')


def updateAllRoutesFiveDaysAfter():
    date = datetime.datetime.now() - datetime.timedelta(days=5)
    while date <= datetime.datetime.now():
        print(date)
        application = Program()
        if application:
            application.updateRouteInformationsByDate(date=date)

            date = date + datetime.timedelta(days=1)

        else:
            print('Error')
    del application

# ! TORNAR ESSA FUNÇÃO ASSÍNCRONA PARA SE ELA ESTIVER SENDO EXECUTADA, CONSEGUIR CHAMAR ELA NOVAMENTE MESMO COM OUTRA EXECUÇÃO RODANDO
# ! TORNAR DEPOIS A LEITURA DAS BASES ASSÍNCRONAS, PARA BUSCAR DUAS OU TRÊS BASES AO MESMO TEMPO


def updateEmployeAndVehicleStatus():

    database = Database()
    reader = Reader(database)
    active_employees = reader.getAllEmployeeIsActive()
    active_vehicles = reader.getAllVehicleIsActive()

    update_script = []
    today = datetime.datetime.now()

    for employee in active_employees:
        if employee[1] is not None:
            last_route = datetime.datetime.strptime(employee[1], "%d/%m/%Y")

            total_days = (today - last_route).days
            if total_days >= 7:

                update_script.append(
                    f'UPDATE `move_smart`.`employee` SET `status` = NULL, license_plate = NULL, search_date = NULL WHERE id = "{employee[0]}";')

    for vehicle in active_vehicles:
        if vehicle[1] is not None:
            last_route = datetime.datetime.strptime(vehicle[1], "%d/%m/%Y")

            total_days = (today - last_route).days
            if total_days >= 7:

                update_script.append(
                    f'UPDATE `move_smart`.`vehicle` SET `status` = NULL, driver = NULL, search_date = NULL WHERE license_plate = "{vehicle[0]}";')

    Updater(database=database, reader=reader).updateVehicleAndEmployeeStatus(
        update_script)


def updateRouteDataAndVehicleAndEmployeeStatus():
    updateAllRoutesFiveDaysAfter()
    updateEmployeAndVehicleStatus()


getAllRoutesInThisHours = [
    datetime.time(8, 0),
    datetime.time(8, 30),
    datetime.time(9, 0),
    datetime.time(9, 30),
    datetime.time(10, 0),
    datetime.time(10, 30),
    datetime.time(11, 0),
    datetime.time(11, 30),
    datetime.time(12, 0),
    datetime.time(12, 30),
    datetime.time(13, 0),
    datetime.time(13, 30),
    datetime.time(14, 0),
    datetime.time(14, 30),
    datetime.time(15, 0),
    datetime.time(15, 30),
    datetime.time(16, 0),
    datetime.time(16, 30),
    datetime.time(17, 0),
    datetime.time(17, 30),
    datetime.time(18, 0),
    datetime.time(18, 30),
    datetime.time(19, 0),
    datetime.time(19, 30),
    datetime.time(20, 0),
    datetime.time(20, 30),
    datetime.time(21, 0),
    datetime.time(21, 30),
    datetime.time(22, 0),
    datetime.time(22, 30),
    datetime.time(23, 0),
    datetime.time(23, 30)
]

updateAllRoutesOfTheBeforeDay = datetime.time(5, 0)

schedule = sched.scheduler(time.time, time.sleep)

# When RPa is started is run all function

getAllRoutes()


def check_hours():
    now = datetime.datetime.now().time()
    if now.hour == updateAllRoutesOfTheBeforeDay.hour and now.minute == updateAllRoutesOfTheBeforeDay.minute:
        last_day = datetime.datetime.now() - datetime.timedelta(days=1)
        print('Updating last day routes')
        schedule.enter(0, 1, updateRouteDataAndVehicleAndEmployeeStatus,
                       argument=())

    for hour in getAllRoutesInThisHours:
        if now.hour == hour.hour and now.minute == hour.minute:

            # Agende a execução da função
            try:
                print('Start time', datetime.datetime.now())
                schedule.enter(0, 1, getAllRoutes,
                               argument=())
            except Exception as e:
                print('Error time', datetime.datetime.now())
                print(e)

    schedule.enter(60, 1, check_hours, ())


schedule.enter(0, 1, check_hours, ())

schedule.run()
