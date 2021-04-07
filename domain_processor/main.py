import zmq
from core import echo, dot
from tornado import ioloop

if __name__ == '__main__':
    print('Initialazing..')
    ctx = zmq.Context.instance()
    s = ctx.socket(zmq.PULL)
    s.bind('tcp://127.0.0.1:43001')
    print('port 43001 binded...')
    loop = ioloop.IOLoop.current()
    loop.add_handler(s, echo, loop.READ)
    loop.add_callback(dot)
    loop.start()