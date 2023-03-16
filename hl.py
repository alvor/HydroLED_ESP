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

class _ow():
    def __init__(self,ow,adr):
        self.ow,self.adr = ow,adr


class _ow_2406(_ow):
    def __init__(self, ow,adr):
        super().__init__(ow,adr)
        self.ch1,self.ch2=0,0
    def ch_set(self,n,val):
        if n!=0: self.ch1=val
        if n!=1: self.ch2=val
        ds2406.turn(self.pin,h2b(self.adr),self.ch1,self.ch2)

class _ow_18x20(_ow):
    def __init__(self, ow,adr):
        super().__init__(ow, adr)

class hl_2406_ch(hl):
    def __init__(self, name, p2406,n):
        super.__init__(self,name)
        self.p2406,self.n=p2406,n
    def turn(self,val):
        self.p2406.ch_set(self.n,val)
    def on(self):
        self.turn(self,0)
    def off(self):
        self.turn(self,1)
