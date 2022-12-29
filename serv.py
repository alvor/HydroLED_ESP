import onewire,machine,ds18x20,time,json
import ubinascii as b2h
def temp_all():
    ow=onewire.OneWire(machine.Pin(2))
    f=open('temps.cfg','r')
    TT=json.load(f)
    print(TT)
    ds18 = ds18x20.DS18X20(ow)
    while True:
        print('========')
        ds18.convert_temp()
        time.sleep_ms(750)
        for i in TT:
            print(i, ds18.read_temp(bytearray(b2h.unhexlify(i))))

def monitor_temp(ow,temps):
    ds18=ds18x20.DS18X20(ow)
    while True:
        ds18.convert_temp()
        time.sleep_ms(750)
        print('===================')
        for i in temps:
            try:
                print(i, ds18.read_temp(bytearray(b2h.unhexlify(i))))
            except:
                print('CRC error')



def list_temp(ow,temp):
    print('=========')
    ds18=ds18x20.DS18X20(ow)
    ds18.convert_temp()
    time.sleep_ms(750)
    n=0
    for i in temp:
        try:
            t=ds18.read_temp(bytearray(b2h.unhexlify(i)))
        except:
            print('CRC error')
            t=-1
            pass
        print(n,t)
        n=n+1
