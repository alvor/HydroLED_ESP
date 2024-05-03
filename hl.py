#from pumps impoort pump

from machine import Pin

import time

import uasyncio as asyncio



#class Config:

#  pass

class PumpConfig:

    work_sec = 110

    period_min = 4

    pin = Pin(4, Pin.OUT)





#hl connect

class Hlc:

    #config = Config()

    def __init__(self):

      asyncio.get_event_loop().create_task(self.run())



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



    async def run(self):

        pass



class Pump(Hlc, PumpConfig ):

    #pins = []

    state = 0

    #work_min = 2

    #sleep_min = 5

    back_timer = 100



    def __init__2(self):

      #for p in [2,4]:

        #self.pins.append( Pin(p, Pin.OUT) )

      #self.pins = 

      #asyncio.get_event_loop().create_task(self.run())

      #return super().__init__()

      pass



    def on(self):

        self.pin.value(1)

        self.state=1

        #self.back_timer =0

        #print('lamp on: ', pin_number-1)

        #self.pins[pin_number-1].value(1)



    def off(self):

        self.pin.value(0)

        self.state=0

        #self.back_timer =0

        #print('lamp off: ', pin_number-1)

        #self.pins[pin_number-1].value(0)



    def status(self):

        #print('status off: ', self.pins[pin_number-1].value())

        return self.status #self.pins[pin_number-1].value()



    async def run(self):

      #ticks = time.ticks_ms()

      #state = self.state

      while True:

        state = int(time.ticks_ms() /1000) % (self.period_min*60) < self.work_sec



        #if self.status and int(time.ticks_ms() /1000) % (self.work_sec+self.sleep_min*60) == 0:

        if self.state != state and not state:

           #self.state = state

           self.off()

           print('dev off: ', self.period_min)

        #elif self.status==0 and int(time.ticks_ms() /1000) % (self.work_sec+self.sleep_min*60) == 0:

        elif self.state != state and state:

           #self.state = state

           self.on()

           print('dev on: ', self.work_sec)





        #self.back_timer +=  1

        await asyncio.sleep(1)

        #self.back_timer +=  int((time.ticks_ms() - ticks) /1000)

        #ticks = time.ticks_ms() 





    @property

    def info(self):

      print('status: ', self.status)

      return super().__init__()





class Hl:

  def __init__(self):

    self.pump = Pump()

  #async def run(self):

    #while True:

      #await asyncio.sleep(1)





hl = Hl()

#loop = asyncio.get_event_loop()

##loop.create_task(hl.pump.run())

#loop.run_forever()











