import argparse
import socket
import threading
import sys
import signal
import struct
from time import sleep


exit_flag = False
ip_list = []
multicast_group = ('239.255.224.127', 2000)

class Receiver(threading.Thread):
    def __init__(self, s):
        self.s = s
        super().__init__()

    def run(self):
        global ip_list

        while not exit_flag:
            try:
                data, addr = self.s.recvfrom(1024)
            except:
                break
            data = data.decode('utf-8')
            if data == '#init':
                if addr[0] not in ip_list:
                    print('<system>: new user enter in chatroom - %s' % (addr[0]))
                    ip_list.append(addr[0])
                    self.s.sendto(str('##init').encode('utf-8'), multicast_group)
            elif data == '##init':
                if addr[0] not in ip_list:
                    ip_list.append(addr[0])
            elif data == 'exit':
                if addr[0] in ip_list:
                    ip_list.remove(addr[0])
                    print('<system>: user %s leave the chatroom' % (addr[0]))
            else:
                if addr[0] not in ip_list:
                    ip_list.append(addr[0])
                if addr[0] != ip_list[0]:
                    print('[%s]: %s' % (addr[0], data))


class Sender(threading.Thread):
    def __init__(self, s):
        self.s = s
        super().__init__()

    def run(self):
        self.s.sendto(str('#init').encode('utf-8'), multicast_group)
        global ip_list
        global exit_flag

        while not exit_flag:
            msg = input()
            if msg == 'ls':
                print('<system>: users list')
                for a in ip_list:
                    print(' - %s' % (a))
            else:
                if msg == 'exit':
                    self.close_connection()
                    return
                else:
                    self.s.sendto(msg.encode('utf-8'), multicast_group)

        if exit_flag:
            self.close_connection()

    def close_connection(self):
        global exit_flag
        exit_flag = True
        self.s.sendto('exit'.encode('utf-8'), multicast_group)
                
        print('[System]: Good Bye')
        self.s.close()
        sleep(1)
        try:
            sys.exit(1)
        except:
            pass


def keyboard_interrupt_handler(signal, frame):
    global exit_flag
    exit_flag = True
    print("\nkeyboard interrupt. exiting")
    sleep(1)
    try:
        sys.exit(1)
    except:
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', dest='blocked_ip', action='store')
    args = parser.parse_args()
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    ttl = struct.pack('b', 1)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    
    
    group = socket.inet_aton(multicast_group[0])
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    if args.blocked_ip:
        if not hasattr(socket, 'IP_BLOCK_SOURCE'):
            setattr(socket, 'IP_BLOCK_SOURCE', 38)
        bls = socket.inet_aton(args.blocked_ip)
        block = struct.pack('4si4s', group, socket.INADDR_ANY, bls)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_BLOCK_SOURCE, block)

    s.bind(('', 2000))

    my_ip = socket.gethostbyname(socket.gethostname())
    global ip_list
    ip_list.append(my_ip)
    print('<system>: welcome to chat - %s' % my_ip)

    receiver = Receiver(s)
    receiver.start()
    sender = Sender(s)
    sender.start()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
    main()
