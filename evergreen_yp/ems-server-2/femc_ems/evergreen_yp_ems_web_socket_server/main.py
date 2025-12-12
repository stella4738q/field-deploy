import asyncio
from src.components.websocket_server import WebSocketServer
from src.utility.config_parser import ConfigParser


if __name__ == '__main__':
    config_parser = ConfigParser()
    config = config_parser.parse('./config.ini', expend_vars=False)
    socker_server = WebSocketServer(config)
    asyncio.run(socker_server.start_server())
