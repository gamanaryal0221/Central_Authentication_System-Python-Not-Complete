import pymysql

from app.utils.constants import Config, Mysql

class Sql():

    def initialize(self, config):
        data_sources_key = Config.MYSQL_DATA_SOURCES
        
        if data_sources_key in config:
            print(f"\n---------- Initializing data source connection ----------")
            data_sources = config[data_sources_key]
            connections = {}

            resource_manager_key = Mysql.RESOURCE_MANAGER
            connections[resource_manager_key] = self.make_connection_with_data_source(resource_manager_key, data_sources)

            return connections
        else:
            raise ConnectionError(f"Missing '{data_sources_key}' configuration")


    def make_connection_with_data_source(self, data_source_key, data_sources):
        if data_source_key in data_sources:
            print(f'Connecting with \'{data_source_key}\' ...')
            connection = None
            try:
                data_source = data_sources[data_source_key]

                connection = pymysql.connect(
                    host=data_source[Mysql.HOSTNAME],
                    database=data_source[Mysql.DATABASE],
                    user=data_source[Mysql.USER],
                    password=data_source[Mysql.PASSWORD],
                    autocommit=True
                )
            except Exception as e:
                print(e)

            if connection:
                print(f"Successfully connected with '{data_source_key}'")
                return connection
            else:
                raise ConnectionError(f"Could not connect with '{data_source_key}'")
            
        else:
            raise ConnectionError(f"Missing datasource detail of '{data_source_key}'")