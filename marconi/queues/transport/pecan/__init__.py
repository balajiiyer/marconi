"""WSGI Transport Driver"""

from marconi.queues.transport.pecan import driver

# Hoist into package namespace
Driver = driver.DriverBase
