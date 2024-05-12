import uasyncio as asyncio
import json
import time
import hl

todo_function = None # callback function if need

async def proc():
  _time = None
  todo_list = json.loads(open('sched_list.json').read()).get('todo_list')

  while True:
    #try:
    if _time == time.localtime()[3:5]:
      await asyncio.sleep(20)
      continue
    _time = time.localtime()[3:5]
    _day_w = time.localtime()[7]
    _time2 = '{:01d}:{:02d}'.format(*_time)

    for todo in todo_list:
      #print('scheduler: ', _time2 , _day_w, todo)
      if todo['time'] == _time2 and ( not todo.get('day_w') or _day_w in todo.get('day_w')):
        print('scheduler: ', _time2 , _day_w)
        event_function(todo)
      await asyncio.sleep(1)

    #except Exception as e:
      #print(e, " in " todo_list)

def event_function(todo ):
    print('scheduler todo: ', "on" if todo['cmd'] else "off")
    eval("hl."+todo["expr"])
    if todo_function:
      todo_function(todo)

