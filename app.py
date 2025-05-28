import asyncio
from libs.http_client import HTTPXClient
from libs.db import PostgresConnector

from config.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


async def main():
    await fetch_data()
    await connect_to_db()


async def connect_to_db():
    db_config = {
        "host": DB_HOST,
        "port": DB_PORT,
        "database": DB_NAME,
        "user": DB_USER,
        "password": DB_PASSWORD,
    }
    db_connector = PostgresConnector(db_config)
    db_connector.connect()


async def fetch_data():
    http_client = HTTPXClient()
    response = await http_client.async_get(
        "https://api.fda.gov/device/event.json?limit=1&search=device.device_report_product_code:FKX+AND+date_received:[2024-07-01+TO+2024-07-31]"
    )
    print(type(response))


if __name__ == "__main__":
    asyncio.run(main())


# Database Connection Pooling
# Pooling: Replace the single connection in PostgresConnector with a connection pool using psycopg2.pool.SimpleConnectionPool. This improves performance under load by reusing connections.
# Asynchronous Alternative: Since your app uses asyncio, consider switching to asyncpg for asynchronous database operations, aligning better with your async architecture.

# Documentation and Code Quality
# Documentation: Add a README.md with setup instructions, environment variable requirements, and usage details. Comment critical code sections (e.g., retry logic in HTTPXClient).
# Code Quality: Use flake8 for linting and black for formatting to maintain consistent, readable code.

# Graceful Shutdown and Resource Management
# Shutdown Handling: Add signal handlers (e.g., signal.SIGTERM) in app.py to close database connections and finish tasks cleanly during shutdown.
# Resource Limits: Set memory and CPU limits in your Docker container or hosting environment to prevent resource exhaustion.

# Scalability and Load Balancing
# Stateless Design: Ensure your app remains stateless (e.g., no in-memory state between runs) to support horizontal scaling with multiple instances.
# Rate Limiting: Add rate limiting to HTTPXClient or at the API level to respect the FDA API’s usage limits and prevent overload.

# Enhanced Error Handling
# HTTP Requests: The async_get method in HTTPXClient retries on connection and timeout errors, which is great. However, add specific handling for HTTP status codes (e.g., 400s vs. 500s) to differentiate between client errors (no retry) and server errors (retry). Log these errors for better debugging.
# Database Connection: In PostgresConnector, catch specific psycopg2 exceptions like OperationalError or IntegrityError instead of a broad Exception. This helps in diagnosing issues like connection failures or data conflicts.
# Application-Level: Wrap the main function in a try-except block to catch and log unexpected errors, ensuring the app fails gracefully.

# Logging and Monitoring
# Replace Print Statements: Use the logging library instead of print for all output (e.g., in app.py and libs/db.py). Configure log levels (DEBUG, INFO, ERROR) and output to a file or service like ELK Stack for persistence and analysis.
# Add Monitoring: Integrate tools like Prometheus and Grafana to track metrics such as API response times, database connection status, and error rates. This ensures you can detect and respond to issues proactively.
