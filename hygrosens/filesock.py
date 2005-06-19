#!/usr/bin/python
import time,select
from socket import *

class filesock(socket):
    """
    A class to make a socket look enough like a file that you can use
    read, readline, readlines, write on it.
    """
    def __init__(self, (host,port), timeout=0.1):
        self.sock = socket(AF_INET,SOCK_STREAM)
        self.timeout = timeout        
        try:
            self.sock.connect((host,port))
            self.sock.setblocking(0)
        except:
            raise
            
        self.fp = self.sock.makefile('rb+')
        
    def read(self,size=None):
        """"
        Implement read available bytes
        """
        rtr, rtw, err = select.select([self.sock],[],[],self.timeout)
        if len(rtr)>0:
            return self.sock.recv(size)
        
    def readline(self,size=None):
        """
        Implement read a single line
        """
        now = time.time()
        str = ""
        while time.time() < now+self.timeout:
            rtr, rtw, err = select.select([self.sock],[],[],self.timeout)
            if len(rtr)>0:
                c = 0
                while c != '\n':
                    try:
                        c = self.sock.recv(1)
                        str += c
                    except:
                        break
        if len(str) > 0:
            return str
        else:
            return None
            
    def readlines(self,size=None):
        """
        Implement read multiple lines
        """
        try:
            str = self.fp.readlines(size)
        except:
            str = None
        return str
        
    def write(self,str):
        """
        Implement write bytes
        """
        self.fp.write(str)
        self.fp.flush()
        