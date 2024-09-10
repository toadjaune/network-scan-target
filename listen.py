import argparse
import asyncio


class EchoServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        transport.write(b"Connection attempt OK\n")
        transport.close()


async def main():

    parser = argparse.ArgumentParser(description='Listen on many ports, to act as a scan target for black-box firewall testing')
    parser.add_argument('--port-min', type=int, default=1,     help='Lower bound of the port range to listen on')
    parser.add_argument('--port-max', type=int, default=65535, help='Upper bound of the port range to listen on')
    args = parser.parse_args()

    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: EchoServerProtocol(),
        '', # listen on all available interfaces
        8888)

    async with server:
        await server.serve_forever()


asyncio.run(main())
