class Eraser():
    def __init__(self, database) -> None:
        self.database = database

    def setRemovePackagesData(self, route_number):
        self.database.connection.start_transaction()
        command = f'''DELETE FROM move_smart.package
                    WHERE route_number = {route_number};'''
        self.database.cursor.execute(command)
        self.database.connection.commit()

    def setRemovePointsData(self, route_number):
        self.database.connection.start_transaction()
        command = f'''
                    DELETE FROM move_smart.point
                    WHERE route_number = {route_number};
                    '''
        self.database.cursor.execute(command)
        self.database.connection.commit()

    def setRemoveStopedsData(self, route_number):
        self.database.connection.start_transaction()
        command = f'''DELETE FROM move_smart.stop
                    WHERE route_number = {route_number};'''
        self.database.cursor.execute(command)
        self.database.connection.commit()

    def setRemoveRoutesData(self, route_number):
        self.database.connection.start_transaction()
        command = f'''DELETE FROM move_smart.route
                    WHERE route_number = {route_number};'''
        self.database.cursor.execute(command)
        self.database.connection.commit()
