#!/usr/bin/env python3

import argparse
import asyncio
import logging
import errno


# This code is heavily inspired by the examples at https://docs.python.org/3/library/asyncio-protocol.html


class TCPServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        """Gets called whenever a client connects (TCP handshake)"""
        peername = transport.get_extra_info("peername")
        logging.info("Connection from {}".format(peername))
        transport.write(b"Connection attempt OK\n")
        transport.close()


class UDPServerProtocol:
    def connection_made(self, transport):
        """Gets called when the socket is opened"""
        self.transport = transport

    def datagram_received(self, data, addr):
        """Gets called whenever a new datagram is received on the socket"""
        message = f"Received probe from {addr}"
        data = str.encode(message)
        logging.info(message)
        self.transport.sendto(data, addr)


def parse_args():
    loglevels = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warn": logging.WARNING,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG,
    }
    parser = argparse.ArgumentParser(
        description="Listen on many ports on TCP and UDP, to act as a scan target for black-box firewall testing"
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
    parser.add_argument(
        "--loglevel",
        choices=loglevels.keys(),
        action="store",
        default="warning",
        help="Provide logging level. default=warning",
    )
    parsed_arguments = parser.parse_args()
    logging.basicConfig(level=loglevels[parsed_arguments.loglevel])
    return parsed_arguments


async def open_tcp_socket_on_port(port: int):
    # Get a reference to the event loop as we plan to use low-level APIs.
    loop = asyncio.get_running_loop()
    try:
        server = await loop.create_server(
            lambda: TCPServerProtocol(),
            "",  # listen on all available interfaces, with both IPv4 and IPv6
            port,
        )
        logging.debug(f"Opened TCP port {port}")
        await server.serve_forever()
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            logging.warning(f"Could not listen on TCP port {port}, already in use")
        else:
            raise e


async def open_udp_socket_on_port(port: int):
    # Get a reference to the event loop as we plan to use low-level APIs.
    loop = asyncio.get_running_loop()
    try:
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPServerProtocol(),
            local_addr=("::", port),
        )
        logging.debug(f"Opened UDP port {port}")
        await asyncio.sleep(3600)
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            logging.warning(f"Could not listen on UDP port {port}, already in use")
        else:
            raise e


async def main():
    cli_args = parse_args()

    coroutines = []

    for port in range(cli_args.port_min, cli_args.port_max + 1):
        coroutines.append(open_tcp_socket_on_port(port))
        coroutines.append(open_udp_socket_on_port(port))

    await asyncio.gather(*coroutines)


asyncio.run(main())
