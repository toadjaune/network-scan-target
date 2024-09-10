import argparse
import asyncio
import logging
import errno


logger = logging.getLogger()


# This code is heavily inspired by the examples at https://docs.python.org/3/library/asyncio-protocol.html


class TCPServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        """Gets called whenever a client connects (TCP handshake)"""
        peername = transport.get_extra_info("peername")
        print("Connection from {}".format(peername))
        transport.write(b"Connection attempt OK\n")
        transport.close()


class UDPServerProtocol:
    def connection_made(self, transport):
        """Gets called when the socket is opened"""
        self.transport = transport

    def datagram_received(self, data, addr):
        """Gets called whenever a new datagram is received on the socket"""
        message = data.decode()
        print("Received %r from %s" % (message, addr))
        print("Send %r to %s" % (message, addr))
        self.transport.sendto(data, addr)


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


async def open_tcp_socket_on_port(port: int):
    # Get a reference to the event loop as we plan to use low-level APIs.
    loop = asyncio.get_running_loop()
    try:
        server = await loop.create_server(
            lambda: TCPServerProtocol(),
            "",  # listen on all available interfaces
            port,
        )
        await server.serve_forever()
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            logger.warning(f"Could not listen on port {port}, already in use")
        else:
            raise e


async def open_udp_socket_on_port(port: int):
    # Get a reference to the event loop as we plan to use low-level APIs.
    loop = asyncio.get_running_loop()
    try:
        transport, protocol = await loop.create_datagram_endpoint(
            # TODO : address family
            lambda: UDPServerProtocol(),
            local_addr=("127.0.0.1", port),
        )
        await asyncio.sleep(3600)
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            logger.warning(f"Could not listen on port {port}, already in use")
        else:
            raise e


async def main():
    args = parse_args()

    coroutines = []

    for port in range(args.port_min, args.port_max):
        coroutines.append(open_tcp_socket_on_port(port))
        coroutines.append(open_udp_socket_on_port(port))

    await asyncio.gather(*coroutines)


asyncio.run(main())
