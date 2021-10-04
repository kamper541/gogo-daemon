import socket
import fcntl
import struct

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def get_ip_list(ifname):
    ipstring = ""
    try:
        ipstring = get_ip_address(ifname)
    except:
        pass

    ipList = None
    if len(ipstring) > 0:
        ipList = ipstring.split('.')

    return ipList

if __name__ == '__main__':
    print(get_ip_address('eth0'))

