from database.recorder import Recorder


class Updater():
    def __init__(self, database, reader: object) -> None:
        self.database = database
        self.reader = reader

    def setRouteDataUpdate(self, route_data: dict):
        result = self.reader.getRouteDataByRouteNumber(
            route_number=route_data['route_number'])

        if result:
            if result[8] == 'Concluída':
                #! Check if the route already completed and up to date
                print('Route already up to date')
                return True
            self.setUpdateInDatabase(route_data=route_data)
        else:
            recorder = Recorder(self.database)
            recorder.setRecordAllRoute(route_data=route_data)

    def setUpdateInDatabase(self, route_data: dict):
        try:
            self.database.connection.start_transaction()
            command = f'''
                        DELETE FROM move_smart.package
                        WHERE route_number = {route_data['route_number']};'''
            self.database.cursor.execute(command)

            command = f'''
                        DELETE FROM move_smart.point
                        WHERE route_number = {route_data['route_number']};
                    '''
            self.database.cursor.execute(command)

            command = f'''DELETE FROM move_smart.stop
                    WHERE route_number = {route_data['route_number']};'''
            self.database.cursor.execute(command)

            command = f'''DELETE FROM move_smart.route
                        WHERE route_number = {route_data['route_number']};'''
            self.database.cursor.execute(command)

            command = f"""
                    INSERT INTO move_smart.route (service_center, route_number, license_plate, driver_name, employee_type, delivered_packages, pending_delivery_packages, delivery_failure_packages,
                    route_status, route_observation, route_date, hourOnDeliveryZone, hourToDeliveryArea, onRouteHour, start_hour_route, service_type, stops_number, points_number,
                    individual_packages_number, individual_bags_number, delivered_percent, delivery_failure_percent, pending_percent, receive_packages, transferred_packages,
                    out_of_area_delivery, routes_claim, last_update)
                    VALUES ({route_data['service_center']}, {route_data['route_number']}, {route_data['license_plate']}, {route_data['driver_name']}, {route_data['employee_type']}, {route_data['delivered_packages']}, {route_data['pending_delivery_packages']}, {route_data['delivery_failure_packages']}, {route_data['route_status']}, {route_data['route_observation']}, {route_data['route_date']}, {route_data['hourOnDeliveryZone']}, {route_data['hourToDeliveryArea']}, {route_data['onRouteHour']}, {route_data['startHourRoute']}, {route_data['service_type']}, {route_data['stops_number']}, {route_data['points_number']}, {route_data['individual_packages_number']}, {route_data['individual_bags_number']}, {route_data['delivered_percent']}, {route_data['delivery_failure_percent']}, {route_data['pending_percent']}, {route_data['receive_packages']}, {route_data['transferred_packages']}, {route_data['out_of_area_delivery']}, {route_data['routes_claim']}, NOW());"""

            # TIMESTAMPADD(HOUR, -3, NOW()) to last_update when the TIMEZONE isn't america/Sao_paulo

            # ? Use try to check the command
            self.database.cursor.execute(command)

            for stop in route_data['stops_list']:
                command = f"""
                                INSERT INTO move_smart.stop (route_number, stop_address, stop_points, stop_packages, stop_number)
                                VALUES ({route_data['route_number']}, {stop['stop_address']}, {stop['stop_points']}, {stop['stop_packages']}, {stop['stop_number']});"""
                # ? Use try to check the command
                self.database.cursor.execute(command)

                for point in stop['individual_points_list']:
                    command = f"""
                                INSERT INTO move_smart.point (route_number, order_letter, order_address, order_address_type)
                                VALUES ({route_data['route_number']}, {point['order_letter']}, {point['order_address']}, {point['order_address_type']});"""
                    # ? Use try to check the command
                    self.database.cursor.execute(command)

                    for package in point['packages_list']:
                        if package:  # If package is None then continue
                            command = f"""
                                        INSERT INTO move_smart.package (route_number, package_number, package_address, package_tag, package_status, package_flag)
                                    VALUES ({route_data['route_number']}, {package['package_number']}, {point['order_address']}, {package['tag']}, {package['status']}, {package['flag']});"""
                            # ? Use try to check the command
                            self.database.cursor.execute(command)

            self.database.connection.commit()
            print('The route', route_data['route_number'], 'was updated!')

        except Exception as e:
            print(e.__class__.__name__)
            print(e)
            self.database.connection.rollback()

    def setUpdateDriverNumericData(self, field_to_insert: str, data_to_inserted: int, ID: str):

        self.database.connection.start_transaction()
        command = f'''
                        UPDATE move_smart.employee
                        SET {field_to_insert} = {data_to_inserted},
                        status = "Ativo"
                        WHERE ID = {ID};
                    '''
        self.database.cursor.execute(command)
        self.database.connection.commit()

    def setUpdateDriverStrData(self, field_to_insert: str, data_to_inserted: str, ID: int):

        self.database.connection.start_transaction()
        command = f'''
                        UPDATE move_smart.employee
                        SET {field_to_insert} = {data_to_inserted},
                        status = "Ativo"
                        WHERE ID = {ID};
                    '''
        self.database.cursor.execute(command)
        self.database.connection.commit()

    def setUpdateDriverLastRouteAndLicensePlate(self, last_route: str, license_plate: str, ID: int):
        # try:
        self.database.connection.start_transaction()
        command = f'''
                        UPDATE move_smart.employee
                        SET last_route = {last_route},
                        license_plate = {license_plate},
                        status = "Ativo"
                        WHERE ID = {ID};
                    '''
        self.database.cursor.execute(command)
        self.database.connection.commit()

    def setUpdateVehicleStrData(self, field_to_insert: str = 'NULL', data_to_insert: str = 'NULL', field_to_check: str = 'NULL',
                                data_to_check: str = 'NULL'):
        self.database.connection.start_transaction()
        command = f'''
                    UPDATE move_smart.vehicle
                    SET {field_to_insert} = {data_to_insert},
                    status = "Ativo"
                    WHERE {field_to_check} = {data_to_check}
                    '''
        self.database.cursor.execute(command)
        self.database.connection.commit()


    def setUpdateVehicleLastRoute(self, last_route: str = 'NULL',
                                  license_plate: str = 'NULL', status="'Ativo'"):
        self.database.connection.start_transaction()

        # Quando o status for None, deverá mudar para ativo
        status = "'Ativo'" if status == None else status

        command = f'''
                    UPDATE move_smart.vehicle
                    SET last_route = {last_route},
                    status = {"'Ativo'" if not "Reserva" in status and
                              status != None else f'"{status}"'}
                    WHERE license_plate = {license_plate}
                    '''
        self.database.cursor.execute(command)
        self.database.connection.commit()

    def setUpdateVehicleServiceType(self, service_type: str = 'NULL', license_plate_type: str = 'NULL', license_plate: str = 'NULL'):

        self.database.connection.start_transaction()
        command = f'''
                    UPDATE move_smart.vehicle
                    SET service_type = {service_type},
                    license_plate_type = {license_plate_type},
                    status = "Ativo"
                    WHERE license_plate = {license_plate}
                    '''
        self.database.cursor.execute(command)
        self.database.connection.commit()

    def updateVehicleAndEmployeeStatus(self, script_list):
        self.database.connection.start_transaction()
        for script in script_list:
            self.database.cursor.execute(script)
        self.database.connection.commit()
