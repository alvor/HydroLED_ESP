from ubinascii import hexlify as b2h
from ubinascii import unhexlify as h2b
import ds2406
class hl:
    def __init__(self,name):
        self.name=name
    def on(self):
        pass
    def off(self):
        pass

class hl_ow(hl):
    def __init__(self, name,pin,adr):
        super().__init__(name)
        self.pin,self.adr = pin,adr


class hl_ow_2406(hl_ow):
    def __init__(self, name,pin,adr):
        super().__init__(name,pin,adr)
        self.ch1,self.ch2=0,0
    def ch_set(self,n,val):
        if n!=0: self.ch1=val
        if n!=1: self.ch2=val
        ds2406.turn(self.pin,h2b(self.adr),self.ch1,self.ch2)

class hl_ow_2406_ch():
    def __init__(self,p2406,n):
        self.p2406,self.n=p2406,n

class hl_ow_18x20(hl_ow):
    def __init__(self, name,pin,adr):
        super().__init__(name, pin, adr)

