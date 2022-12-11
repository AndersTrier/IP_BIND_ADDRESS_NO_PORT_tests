#!/usr/bin/env python3
import socket
import os
import resource

RLIMIT_NOFILE = 200000

# From /usr/include/linux/in.h
IP_BIND_ADDRESS_NO_PORT = 24

def do_connect(bindaddr, target, IP_BIND_ADDRESS_NO_PORT_enable):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if IP_BIND_ADDRESS_NO_PORT_enable:
        try:
            s.setsockopt(socket.IPPROTO_IP, IP_BIND_ADDRESS_NO_PORT, 1)
        except OSError as e:
            print(f"Error on setsockopt: {e}")
            raise

    if bindaddr:
        try:
            s.bind(bindaddr)
        except OSError as e:
            print(f"Error on bind: {e}")
            raise

    try:
        s.connect(target)
    except OSError as e:
        print(f"Error on connect: {e}")
        raise

    return s


nofile_soft, nofile_hard= resource.getrlimit(resource.RLIMIT_NOFILE)
nofile_soft_new = min(RLIMIT_NOFILE, nofile_hard)
resource.setrlimit(resource.RLIMIT_NOFILE, (nofile_soft_new, nofile_hard))
print(f"Raised RLIMIT_NOFILE softlimit from {nofile_soft} to {nofile_soft_new}")

with open('/proc/sys/net/ipv4/ip_local_port_range') as f:
    minport, maxport = map(int, f.readline().split())
    nports = (maxport - minport) + 1


def main():
    while True:
        idx = input("Select test (1-6): ")
        globals()[f"test{idx}"]()


def test1():
    print("#### Test 1 ####")
    connections = []
    while True:
        try:
            connections.append(do_connect(None, ("127.0.0.1", 1337), False))
        except OSError as e:
            break
    map(socket.close, connections)
    print(f"Made {len(connections)} connections. Expected to be around {nports}.")

def test2():
    print("#### Test 2 ####")
    connections = []
    while True:
        try:
            connections.append(do_connect(("127.0.0.2", 0), ("127.0.0.2", 1337), False))
        except OSError as e:
            break
    map(socket.close, connections)
    print(f"Made {len(connections)} connections. Expected to be around {nports}.")

def test3():
    print("#### Test 3 ####")
    connections = []
    while True:
        try:
            connections.append(do_connect(("127.0.0.31", 0), ("127.0.0.3", 1337), False))
            connections.append(do_connect(("127.0.0.32", 0), ("127.0.0.3", 1337), False))
        except OSError as e:
            break
    map(socket.close, connections)
    print(f"Made {len(connections)} connections. Expected to be around {nports * 2}.")

def test4():
    print("#### Test 4 ####")
    connections = []
    while True:
        try:
            connections.append(do_connect(("127.0.0.4", 0), ("127.0.0.41", 1337), False))
            connections.append(do_connect(("127.0.0.4", 0), ("127.0.0.42", 1337), False))
        except OSError as e:
            break
    map(socket.close, connections)
    print(f"Made {len(connections)} connections. Expected to be around {nports}.")

def test5():
    print("#### Test 5 ####")
    connections = []
    while True:
        try:
            connections.append(do_connect(("127.0.0.5", 0), ("127.0.0.5", 1337), True))
        except OSError as e:
            break
    map(socket.close, connections)
    print(f"Made {len(connections)} connections. Expected to be around {nports}.")

def test6():
    print("#### Test 6 ####")
    connections = []
    while True:
        try:
            connections.append(do_connect(("127.0.0.6", 0), ("127.0.0.61", 1337), True))
            connections.append(do_connect(("127.0.0.6", 0), ("127.0.0.62", 1337), True))
        except OSError as e:
            break
    map(socket.close, connections)
    print(f"Made {len(connections)} connections. Expected to be around {nports * 2}.")


if __name__ == "__main__":
    main()

