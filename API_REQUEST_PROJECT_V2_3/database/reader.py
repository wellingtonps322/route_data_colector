class Reader():
    def __init__(self, database) -> None:
        self.database = database

    def getRouteDataByRouteNumber(self, route_number: int):
        self.database.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.route
                    WHERE route_number = {route_number};
                    '''
        self.database.cursor.execute(command)
        result = self.database.cursor.fetchone()  # Read the database
        self.database.connection.commit()
        return result

    def getRouteDataByDate(self, date):
        self.database.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.route
                    WHERE route_date = "{date}";
                    '''
        self.database.cursor.execute(command)
        result = self.database.cursor.fetchall()  # Read the database
        self.database.connection.commit()
        return result

    def getDriverDataByServiceCenter(self, driver_name: str, service_center: str):
        self.database.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.employee;
                    WHERE name = {driver_name} AND service_center = {service_center};
                '''
        self.database.cursor.execute(command)
        result = self.database.cursor.fetchall()
        self.database.connection.commit()
        return result

    def getDriverDataByName(self, driver_name: str):
        self.database.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.employee;
                    WHERE name = {driver_name};
                '''
        self.database.cursor.execute(command)
        result = self.database.cursor.fetchall()
        self.database.connection.commit()
        return result

    def getSearchVehicleData(self, license_plate: str):
        self.database.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.vehicle
                    WHERE license_plate = {license_plate};
                '''
        self.database.cursor.execute(command)
        result = self.database.cursor.fetchone()
        self.database.connection.commit()
        return result

    def getSearchDriverDataByName(self, driver_name: str):
        command = ''
        if driver_name:
            self.database.connection.start_transaction()
            command = f'''
                        SELECT * FROM move_smart.employee
                        WHERE name = {driver_name};
                    '''
        if command:
            self.database.cursor.execute(command)
            result = self.database.cursor.fetchone()
            self.database.connection.commit()
            return result

    def getSearchDriverDataByServiceCenter(self, driver_name: str, service_center: str):
        command = ''
        if service_center == 'NULL':
            ...

        if not service_center == 'NULL':
            self.database.connection.start_transaction()
            command = f'''
                        SELECT * FROM move_smart.employee
                        WHERE driver_name = {driver_name} AND service_center = {service_center};
                    '''
        if command:
            self.database.cursor.execute(command)
            # print(command)
            result = self.database.cursor.fetchall()
            self.database.connection.commit()
            return result

    def getSearchHubFromRouteData(self, route_number: int):
        command = ''
        if route_number:
            self.database.connection.start_transaction()
            command = f'''
                        SELECT service_center FROM move_smart.invoice_payment
                        WHERE ID_route = {route_number};
                    '''
            self.database.cursor.execute(command)
            result = self.database.cursor.fetchall()
            self.database.connection.commit()
            if result:
                return result[0][0]

    def getRouteData(self, route_number: int):
        command = ''
        if route_number:
            self.database.connection.start_transaction()
            command = f'''
                        SELECT * FROM move_smart.route
                        WHERE route_number = {route_number};
                    '''
            self.database.cursor.execute(command)
            result = self.database.cursor.fetchone()
            self.database.connection.commit()
            if result:
                return result

    def getAllEmployeeIsActive(self):
        self.database.connection.start_transaction()
        command = f'''
                    SELECT id, last_route FROM move_smart.employee
                    WHERE status = "Ativo";
                    '''
        self.database.cursor.execute(command)
        self.result = self.database.cursor.fetchall()  # Read the database
        self.database.connection.commit()
        return self.result

    def getAllVehicleIsActive(self):
        self.database.connection.start_transaction()
        command = f'''
                    SELECT license_plate, last_route FROM move_smart.vehicle
                    WHERE status = "Ativo";
                    '''
        self.database.cursor.execute(command)
        self.result = self.database.cursor.fetchall()  # Read the database
        self.database.connection.commit()
        return self.result
