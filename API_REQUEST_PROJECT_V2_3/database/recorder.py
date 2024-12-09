class Recorder():
    def __init__(self, database) -> None:
        self.database = database

    def setRecordAllRoute(self, route_data: dict, status='new'):
        self.database.connection.start_transaction()
        command = f"""
                INSERT INTO move_smart.route (service_center, route_number, license_plate, driver_name, employee_type, delivered_packages, pending_delivery_packages, delivery_failure_packages,
                route_status, route_observation, route_date, hourOnDeliveryZone, hourToDeliveryArea, onRouteHour, start_hour_route, service_type, stops_number, points_number,
                individual_packages_number, individual_bags_number, delivered_percent, delivery_failure_percent, pending_percent, receive_packages, transferred_packages,
                out_of_area_delivery, routes_claim, last_update)
                VALUES ({route_data['service_center']}, {route_data['route_number']}, {route_data['license_plate']}, {route_data['driver_name']}, {route_data['employee_type']}, {route_data['delivered_packages']}, {route_data['pending_delivery_packages']}, {route_data['delivery_failure_packages']},
                {route_data['route_status']}, {route_data['route_observation']}, {
            route_data['route_date']}, {route_data['hourOnDeliveryZone']},
                {route_data['hourToDeliveryArea']}, {route_data['onRouteHour']}, {route_data['startHourRoute']}, {route_data['service_type']}, {route_data['stops_number']}, {route_data['points_number']}, {route_data['individual_packages_number']}, {route_data['individual_bags_number']}, {route_data['delivered_percent']}, {route_data['delivery_failure_percent']}, {route_data['pending_percent']}, {route_data['receive_packages']}, {route_data['transferred_packages']}, {route_data['out_of_area_delivery']}, {route_data['routes_claim']}, NOW());
                """

        # TIMESTAMPADD(HOUR, -3, NOW()) to last_update when the TIMEZONE isn't america/Sao_paulo
        # ? Use try to check the command
        self.database.cursor.execute(command)

        for stop in route_data['stops_list']:
            command = f"""
                            INSERT INTO move_smart.stop (route_number, stop_address, stop_points, stop_packages, stop_number)
                            VALUES ({route_data['route_number']}, {stop['stop_address']}, {stop['stop_points']}, {stop['stop_packages']},
                            {stop['stop_number']});"""
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
        if status == 'new':
            print('The route', route_data['route_number'], 'was inserted!')

    def setNewVehicle(self, license_plate: str, service_center: str, driver: str, last_route: str, license_plate_type: str, service_type: str):
        self.database.connection.start_transaction()
        command = f'''
                        INSERT INTO move_smart.vehicle (license_plate, service_center, driver, last_route, license_plate_type, service_type)
                        VALUES ({license_plate}, {service_center}, {driver}, {last_route}, {license_plate_type}, {service_type})'''
        self.database.cursor.execute(command)
        self.database.connection.commit()

    def setNewDriver(self, id_driver, driver_name, employee_sector, employee_function, service_center, license_plate, last_route):
        command = None

        if id_driver != 'NULL' and service_center != 'NULL':
            self.database.connection.start_transaction()
            command = f'''
                            INSERT INTO move_smart.employee (id, name, employee_sector, employee_function, status, service_center, license_plate, last_route)
                            VALUES({id_driver}, {driver_name}, {employee_sector}, {
                employee_function}, "Ativo", {service_center},{license_plate}, {last_route});
                        '''
            if command:
                self.database.cursor.execute(command)
                self.database.connection.commit()
        if id_driver == 'NULL' and service_center != 'NULL':
            self.database.connection.start_transaction()
            command = f'''
                            INSERT INTO move_smart.employee (name, employee_sector, employee_function, service_center, license_plate, last_route)
                            VALUES({driver_name}, {employee_sector}, {employee_function}, {
                service_center},{license_plate}, {last_route});
                        '''
            if command:
                self.database.cursor.execute(command)
                self.database.connection.commit()
        else:
            print('ATENÇÃO: ERRO NA INSERÇÃO DE DADOS DO MOTORISTA.')
            print(
                'Por falta de dados na pré-fatura, não foi possível realizar o cadastro automático do motorista')
            print('Por favor, faça o cadastro manualmente')
