from byte_parser import parse_dns_query, get_dns_response
from storage import CacheStorage
import socket


class DNSServer:
    def __init__(self, ip, parent_dns, cache_filename):
        self.ip = ip
        self.parent_server = parent_dns
        self.cache = CacheStorage(cache_filename)

    def run(self):
        print('run')
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                sock.bind((self.ip, 53))
                data, addr = sock.recvfrom(512)
                print('received')
                if not data:
                    break
                parsed_data = parse_dns_query(data)
                entities = self.cache.get_entity(parsed_data)
                print(entities)
                if entities is None:
                    response = self.request_from_parent(data)
                    if response is not None:
                        parsed_response = parse_dns_query(response)
                        self.cache.put_entity(parsed_response)
                    else:
                        print('timeout')
                        response = get_dns_response(parsed_data[0],
                                                    parsed_data[1], [], [], [])
                else:
                    response = get_dns_response(parsed_data[0],
                                                parsed_data[1], entities,
                                                [], [])
                print('sending response')
                sock.sendto(response, addr)
            finally:
                sock.close()
                self.cache.save()

    def request_from_parent(self, data):
        print('asking parent')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5.0)
        try:
            sock.bind(('', 0))
            sock.sendto(data, (self.parent_server, 53))
            return sock.recvfrom(512)[0]
        except socket.timeout:
            return None
        finally:
            sock.close()
