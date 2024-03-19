# до реализации mem free 60k - 85k
import uasyncio as asyncio
import json
import time
from machine import Pin

led = Pin(4, Pin.OUT)

async def proc():
  #del sys.modules['']
  cou =1
  _time = None

  while True:
    if _time == time.localtime()[3:5]:
      continue
    _time = time.localtime()[3:5]

    _day_w = time.localtime()[7]
    _time2 = '{:01d}:{:02d}'.format(*_time)

    #print('scheduler: ', _time2, _day_w, cou)

    todo_list = json.loads(open('sched_list.json').read()).get('todo_list')
    #TODO вынести за цикл в начало

    #led.value(not led.value())
    #for todo in todo_list:
      #await asyncio.sleep(100)

    for todo in todo_list:
      #print('scheduler: ', _time2 , _day_w)
      if todo['time'] == _time2 and (todo.get('day_w') == _day_w or not todo.get('day_w')):
        print('scheduler: ', _time2 , _day_w)
        check_time(todo['cmd'])
      #else:
        #check_time(todo['on'])
      await asyncio.sleep(1)

    await asyncio.sleep(20)


def check_time(cmd = 1):

  #while True:

    #led.value(not led.value())
    print('scheduler todo: ', "on" if cmd else "off")
    led.value(cmd)

