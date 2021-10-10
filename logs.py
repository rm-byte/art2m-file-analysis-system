from datetime import datetime
from json import dumps
from os import environ


def write_logs(error: str) -> None:
    """Event logging"""
    file = open('logs/' + str(datetime.now().date()) + '.txt', 'a+')
    file.write(dumps({'error': error, 'datetime': str(datetime.now()), 'user': environ.get("USERNAME")}) + '\n')
    file.close()
    file = open('logs/' + str(datetime.now().date()) + '.txt', 'r')
    file.close()
