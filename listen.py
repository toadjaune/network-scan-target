import argparse
import asyncio
import logging
import errno


logger = logging.getLogger()


class EchoServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info("peername")
        print("Connection from {}".format(peername))
        transport.write(b"Connection attempt OK\n")
        transport.close()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Listen on many ports, to act as a scan target for black-box firewall testing"
    )
    parser.add_argument(
        "--port-min",
        type=int,
        default=1,
        help="Lower bound of the port range to listen on",
    )
    parser.add_argument(
        "--port-max",
        type=int,
        default=65535,
        help="Upper bound of the port range to listen on",
    )
    return parser.parse_args()


async def start_server_on_port(port: int):
    # Get a reference to the event loop as we plan to use low-level APIs.
    loop = asyncio.get_running_loop()
    try:
        server = await loop.create_server(
            lambda: EchoServerProtocol(),
            "",  # listen on all available interfaces
            port,
        )
        await server.serve_forever()
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            logger.warning(f"Could not listen on port {port}, already in use")
        else:
            raise e


async def main():
    args = parse_args()

    coroutines = []

    for port in range(args.port_min, args.port_max):
        coroutines.append(start_server_on_port(port))

    await asyncio.gather(*coroutines)


asyncio.run(main())
