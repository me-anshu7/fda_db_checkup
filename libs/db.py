import psycopg2
from typing import Dict
from libs.logger import logger


class PostgresConnector:
    def __init__(self, connection_params: Dict):
        """Initialize PostgreSQL connector with connection parameters"""
        self.connection_params = connection_params
        self.conn = None
        self.cursor = None

    def connect(self):
        """Create database connection with detailed error logging"""
        try:
            logger.info(
                f"Attempting to connect to database at {self.connection_params['host']}:{self.connection_params['port']}"
            )

            # Try connection
            self.conn = psycopg2.connect(**self.connection_params)
            self.cursor = self.conn.cursor()

            # Test connection
            self.cursor.execute("SELECT version()")
            db_version = self.cursor.fetchone()
            logger.info(
                f"Successfully connected to PostgreSQL. Version: {db_version[0]}"
            )

            return True
        except psycopg2.OperationalError as e:
            logger.exception(f"Database connection error: {str(e)}")
            safe_params = {
                k: v for k, v in self.connection_params.items() if k != "password"
            }
            logger.exception(
                f"Connection parameters used (excluding password): \\n {str(safe_params)}"
            )
            return False
        except Exception as e:
            logger.exception(f"Unexpected error during database connection: {str(e)}")
            return False

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
