import sys
import signal
import urlparse
import gevent
from gevent.server import StreamServer
from gevent.socket import create_connection, gethostbyname

from gevent import monkey

monkey.patch_all()

#==========Self-defined lib===========
import load_balance
#=====================================

#==========for Develop================

import log
logger = log.getLogger()

B = load_balance.Back_end([
    
            "https://127.0.0.1:8087",
            "http://127.0.0.1:8087"

        ], ['http', 'https'], logger)

#=====================================



class ProxyServer(StreamServer):
    def __init__(self, listener, **kwargs):
        StreamServer.__init__(self, listener, **kwargs)

    def handle(self, client, address):
        log('%s:%s accepted', *address[:2])
        try:
            line1 = ''
            _data = client.recv(1)
            while _data :
                line1 += _data
                _data = client.recv(1)
                if _data == '\n':
                    line1 += '\n'
                    break
            
            if line1:
                remote_path, forw, back = B.Get_Backend(line1.split()[1])  #define forward and backward Tunnel
                # remote_path = ['127.0.0.1', '8087']
                remote = create_connection(remote_path)
                source_address = '%s:%s' % client.getpeername()[:2]
                dest_address = '%s:%s' % remote.getpeername()[:2]
                log("Starting port forwarder %s -> %s", source_address, dest_address)                 
                gevent.spawn(forw, client, remote)
                gevent.spawn(back, remote, client) 
                remote.sendall(line1)
            
            else:
                client.close()
                return  

            
        except Exception, ex:
            log('failed : %s', ex)
            import traceback
            traceback.print_exc()
            return


    def close(self):
        if self.closed:
            sys.exit('Multiple exit signals received - aborting.')
        else:
            log('Closing listener socket')
            StreamServer.close(self)


# def forward(source, dest):
#     source_address = '%s:%s' % source.getpeername()[:2]
#     dest_address = '%s:%s' % dest.getpeername()[:2]
#     Buff_size = 1024
#     try:
#         while True:
#             data = source.recv(Buff_size)
#             if not data:
#                 break
#             Buff_size = min(Buff_size*2, 65536) if len(data) >= Buff_size else Buff_size
#             log('%s->%s: %r bytes', source_address, dest_address, len(data))
#             dest.sendall(data)
#     finally:
#         source.close()
#         dest.close()


def main():
    server = ProxyServer(('0.0.0.0',8888))
    log('Starting proxy server %s:%s', *(server.address[:2]))
    gevent.signal(signal.SIGTERM, server.close)
    gevent.signal(signal.SIGINT, server.close)
    server.serve_forever()


def log(message, *args):
    message = message % args
    sys.stderr.write(message + '\n')


if __name__ == '__main__':
    main()
