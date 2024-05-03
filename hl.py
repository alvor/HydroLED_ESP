#from pumps impoort pump
from machine import Pin

#class Config:
#  pass

#hl connect
class Hlc:
    #config = Config()
    def __init__(self):
      pass

    def on(self):
        pass
    def off(self):
        pass

    def search(self):
        #raise OSError('Not implemented.')     
        pass

    @property
    def info(self):
        #raise OSError('Not implemented.')     
        pass

class Pump(Hlc):
    pins = []

    def __init__(self):
      for p in [2,4]:
        self.pins.append( Pin(p, Pin.OUT) )
      #self.pins = 

    def on(self, pin_nimber):
        print('lamp on: ', pin_nimber-1)
        self.pins[pin_nimber-1].value(1)

    def off(self, pin_nimber):
        print('lamp off: ', pin_nimber-1)
        self.pins[pin_nimber-1].value(0)

    def status(self, pin_nimber):
        print('status off: ', self.pins[pin_nimber-1].value())
        return self.pins[pin_nimber-1].value()

    @property
    def info(self):
      print('status off: ', self.pins)
      return super().__init__()


class Hl:
  def __init__(self):
    self.pump = Pump()


hl = Hl()
