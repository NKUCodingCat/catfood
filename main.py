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
import bg_db
#=====================================

#==========for Develop================

import log
logger = log.getLogger()

B = load_balance.Back_end([
    
            # "https://127.0.0.1:8087",
            "http://127.0.0.1:8087"

        ], ['http', 'https'], logger)

DB = bg_db.Connection_Status()

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
                
                try:
                    # raise
                    remote_path, host = parse_address(line1.split()[1])
                    remote = create_connection(remote_path, timeout=2)
                    
                    if line1.split()[0] == 'CONNECT':
                        while True:
                            _d = client.recv(65536)
                            if _d:
                                break
                            else:
                                line1 += _d
                        forw, back = B.https_wrapper,  B.https_wrapper
                        client.sendall('HTTP/1.1 200 \r\n\r\n')

                    else:
                        forw, back = B.http_wrapper, B.http_wrapper
                        remote.sendall(line1)

                    DB.insDomain(host, True)

                except:
                    import traceback
                    traceback.print_exc()
                    remote_path, remote_type, forw, back = B.Get_Backend(line1.split()[1])  #define forward and backward Tunnel
                    remote = create_connection(remote_path)
                    remote.sendall(line1)
                    DB.insDomain(host, True)

                source_address = '%s:%s' % client.getpeername()[:2]
                dest_address = '%s:%s' % remote.getpeername()[:2]
                log("Starting port forwarder %s -> %s", source_address, dest_address)                 
                gevent.spawn(forw, client, remote)
                gevent.spawn(back, remote, client)
                
                
            
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

def parse_address(address):
    try:
        urls = urlparse.urlparse(address)
        address = urls.netloc or urls.path
        _addr = address.split(':')
        hostname, port = len(_addr) == 2 and  _addr or (_addr[0],80)
        port = int(port)
    except ValueError:
        sys.exit('Expected HOST:PORT: %r' % address)
    return (gethostbyname(hostname), port), hostname

def main():
    server = ProxyServer(('0.0.0.0',6666))
    log('Starting proxy server %s:%s', *(server.address[:2]))
    gevent.signal(signal.SIGTERM, server.close)
    gevent.signal(signal.SIGINT, server.close)
    server.serve_forever()


def log(message, *args):
    message = message % args
    sys.stderr.write(message + '\n')


if __name__ == '__main__':
    main()
