from scapy.all import *
from contextlib import redirect_stdout
from threading import Thread
from argparse import ArgumentParser
from netifaces import ifaddresses, AF_INET
from datetime import datetime
from random import randint
import os

class MyThread(Thread):
    
    def __init__(self, ip, src = ifaddresses('wlp4s0')[AF_INET][0]['addr']):
        """Инициализация потока"""
        Thread.__init__(self)
        self.ip = ip
        self.hops_max = 20
        self.src = src
        self.attack = 1 if self.src!=ifaddresses('wlp4s0')[AF_INET][0]['addr'] else None
    
    def run(self):
        """Запуск потока"""
        if self.attack:
            for i in range(10):
                answer = sr1(IP(dst=self.ip, src=self.src, ttl=i)/ICMP(), verbose=0, timeout=1)
            return
        result = '' 
        for i in range(1, self.hops_max):
            answer = sr1(IP(dst=self.ip, src=self.src, ttl=i)/ICMP(reserved=int(datetime.now().microsecond)), verbose=0, timeout=20)
            current_time = datetime.now().microsecond
            received_time = int(answer.reserved)
            time = current_time-received_time if current_time>received_time else received_time-current_time
            result += str(i) + ' ' + answer.src +'     ' + str(time/1000) + ' ms' + '\n'
            if answer.type == 0:
                print(result)
            if answer.type == 3:
                print('Хост недостижим')
            if answer.type != 11:
                break
        else:
            print('Время жизни пакета истекло')
        
        
          
def main():
    parser = ArgumentParser()
    parser.add_argument('hosts', nargs='+', type=str, help='hosts for pinging or for future attack')
    parser.add_argument('-v', dest='victim', action='store', help='attack victim')
    args = parser.parse_args()
    for i in args.hosts:
        if args.victim:
            host = MyThread(i, args.victim)
        else:
            host = MyThread(i)
        host.start()


if __name__=='__main__':
    main()
