import zmq

# Middleware connection constants

POLLIN = zmq.POLLIN
POLLOUT = zmq.POLLOUT

HB_TIME = 2
TIMEOUT = HB_TIME * 2

# Middleware channel types

REQ = zmq.REQ
REP = zmq.REP
PULL = zmq.PULL
PUSH = zmq.PUSH
PUB = zmq.PUB
SUB = zmq.SUB

ROUTER_RECONNECT_TRIAL = 0.5