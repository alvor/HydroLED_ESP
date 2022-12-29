from onewire import OneWire
from machine import Pin
onewire_pin = 2
signal_begin_pin = 0
def ba2hex(ba):
    return (''.join('{:02x}:'.format(x) for x in ba))[:-1]
def simple_scan():
    Pin(signal_begin_pin).init(Pin.OUT)
    Pin(signal_begin_pin).on()
    ow = OneWire(Pin(onewire_pin))
    roms = ow.scan()
    Pin(signal_begin_pin).off()
    for i in roms:
        print(ba2hex(i))
    print('Found :', len(roms),'roms')
    return (roms,len(roms))

def cicle_scan(cicles=100):
    Pin(signal_begin_pin).init(Pin.OUT)
    Pin(signal_begin_pin).on()
    ow = OneWire(Pin(onewire_pin))
    roms_dict = {}
    for i in range(0, cicles):
        roms = ow.scan()
        for j in roms:
            fr = roms_dict.get(ba2hex(j))
            if not fr:
               roms_dict.update({ba2hex(j):1})
            else:
                n=roms_dict.pop(ba2hex(j))
                roms_dict.update({ba2hex(j):(n+1)})
    Pin(signal_begin_pin).off()
    print('=== Test scan for {} cicles ==='.format(cicles))
    for keys, values in roms_dict.items():
        print(keys, values)
