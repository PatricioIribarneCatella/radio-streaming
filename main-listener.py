import sys
import json
import argparse
from os import path

sys.path.append(path.join(path.dirname(path.abspath(__file__)), 'src/'))

from rebroadcast.listener import Listener

config = {
    "routers_endpoints": ['127.0.0.1:5010', '127.0.0.1:5011', '127.0.0.1:5012']
}
l = Listener(config)

l.run()
