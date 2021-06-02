import sys

from server import DNSServer

if __name__ == '__main__':
    ip = sys.argv[1]
    parent = sys.argv[2]
    filename = sys.argv[3]
    server = DNSServer(ip, parent, filename)
    server.run()
