# IP_BIND_ADDRESS_NO_PORT_tests

Used in a [discussion on the tor-relays mailing lists.](https://forum.torproject.net/t/tor-relays-inet-csk-bind-conflict/5757), to figure out what is going on with the interaction between bind() connect() and setsockopt(IP_BIND_ADDRESS_NO_PORT).

To run the tests, start the server, run the connect.py script and select a test.

The time it takes to exhaust the ephemeral ports can be reduced by making fewer ports available: 

`sysctl -w net.ipv4.ip_local_port_range="40000 40100"`

IP_BIND_ADDRESS_NO_PORT seems to work as it should, but calling bind without it enabled turns out to cause more damage than expected. Here's what we learned:

A successful bind() on a socket without IP_BIND_ADDRESS_NO_PORT enabled, with or without an explicit port configured, makes the assigned (or supplied) port unavailable for new connect()s (on different sockets), no matter the destination. I.e if you exhaust the entire net.ipv4.ip_local_port_range with bind() (no matter what IP you bind to!), connect() will stop working - no matter what IP you attempt to connect to. You can work around this by manually doing a bind() (with or without an explicit port, but without IP_BIND_ADDRESS_NO_PORT) on the socket before connect(). 

I.e 
```
$ uname -a
Linux laptop 5.15.0-56-generic #62-Ubuntu SMP Tue Nov 22 19:54:14 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux
# sysctl -w net.ipv4.ip_local_port_range="40000 40100"
$ ../connect.py
Raised RLIMIT_NOFILE softlimit from 1024 to 200000
Select test (1-6): 2
#### Test 2 ####
Error on bind: [Errno 98] Address already in use
Made 101 connections. Expected to be around 101.
Select test (1-6): 1
#### Test 1 ####
Error on connect: [Errno 99] Cannot assign requested address
Made 0 connections. Expected to be around 101.
Select test (1-6): 3
#### Test 3 ####
Error on bind: [Errno 98] Address already in use
Made 200 connections. Expected to be around 202.
```

For more information, see the discussion (linked in the top of this file) on the torproject relays mailing list.
