import gc
import machine, ds2406, onewire, ds18x20
import network, ntptime
import uasyncio as asyncio
from ubinascii import hexlify as b2h
from ubinascii import unhexlify as h2b
import json
import time
import sys
import scheduler
from nanoweb import Nanoweb, send_file
from hx711 import HX711

H_OK = 'HTTP/1.1 200 OK\r\n'
MAXTEMP = 60
ssid = json.loads(open('wifipsw.psw').read()).get('ssid')
pswd = json.loads(open('wifipsw.psw').read()).get('pswd')

sta = network.WLAN(network.STA_IF)
sta.active(True)
hl_timezone = 7
ow_pin = 2
ds18_delay = 730

Ch1Time=((8,00),(20,00))
Ch2Time=((8,15),(19,45))

lmps = [b'128a9bb4000000fc']
tmps = [b'28ff300676200286']

ow = onewire.OneWire(machine.Pin(ow_pin))
ds18 = ds18x20.DS18X20(ow)
ds24 = ds2406.DS2406(ow, lmps)
naw = Nanoweb()
naw.assets_extensions += ('ico', 'png',)
_DIR = '/_web/'
naw.STATIC_DIR = _DIR

def get_time():
    _date = time.localtime()[0:4]
    _time = time.localtime()[3:6]
    uptime_s = int(time.ticks_ms() / 1000)
    uptime_h = int(uptime_s / 3600)
    uptime_m = int(uptime_s / 60)
    uptime_m = uptime_m % 60
    uptime_s = uptime_s % 60
    return (
        '{}-{:02d}-{:02d}'.format(*_date),
        '{:02d}:{:02d}:{:02d}'.format(*_time),
        '{:02d}h {:02d}:{:02d}'.format(uptime_h, uptime_m, uptime_s),
    )

async def api_ls(rq):
    gc.collect()
    try:
        uos.chdir(rq.url.split('?chdir=')[1])
    except:
        pass
    else:
        pass
    await rq.write(H_OK)
    await rq.write("Content-Type: application/json\r\n\r\n")
    await rq.write('{"files": [%s]}' % ', '.join(
        '"' + f + '"' for f in ['..']+sorted(uos.listdir())
    ))

#TODO добавить куррент дир
async def api_send_response(rq, code=200, message="OK"):
    await rq.write("HTTP/1.1 %i %s\r\n" % (code, message))
    await rq.write("Content-Type: application/json\r\n\r\n")
    await rq.write('{"status": true}')



async def api_status(rq):
    await rq.write(H_OK)
    await rq.write("Content-Type: application/json\r\n\r\n")
    mem_free = gc.mem_free()
    date_str, time_str, uptime_str = get_time()
    await rq.write(json.dumps({
        "date": date_str,
        "time": time_str,
        "mem_free": mem_free,
        "currdir": uos.getcwd()
    }))
async def api_scale(rq):
    sc711 = HX711(d_out=32, pd_sck=33)
    await rq.write(H_OK)
    await rq.write("Content-Type: application/json\r\n\r\n")
    hx711_raw=sc711.read()
    hx711_g=hx711_raw*0.5
    await rq.write(json.dumps({
        "hx711_raw": hx711_raw,
        "hx711_g": hx711_g
    }))
async def api_temps(rq):
    await rq.write(H_OK)
    await rq.write("Content-Type: application/json\r\n\r\n")


async def keep_connect():
    while True:
        if sta.active():
            if not sta.isconnected():
                try:
                    sta.connect(ssid, pswd)
                except:
                    print('Can not connected')
                else:
                    print("Connected")
                    print(sta.ifconfig())
            else:
                print(sta.ifconfig())
                try:
                    ntptime.NTP_DELTA = ntptime.NTP_DELTA - hl_timezone * 3600
                    ntptime.settime()
                except:
                    print('Time set errors')
                else:
                    print('Time : ', time.localtime())
        else:
            sta.active(False)
            sta.active(True)
        await asyncio.sleep(600)


async def system_loop():
    crcErLv = 0
    while True:
        try:
            ds18.convert_temp()
            await asyncio.sleep_ms(ds18_delay)
            max_tmp = 0
            for i in tmps:
                try:
                    tmp = ds18.read_temp(h2b(i))
                    max_tmp = max(max_tmp, tmp)
                except:
                    crcErLv += 1
                    print('CRC Er', crcErLv)
                    if crcErLv > 15: crcErLv = 15
                else:
                    print('Tmp ', i, ' : ', tmp)
                    crcErLv -= 2
                    if crcErLv < 0: crcErLv = 0
                if (max_tmp > MAXTEMP) or (crcErLv > 5):
                    for j in lmps:
                        ds24.turn((j), 1, 1)
                        print('Lmp {} off'.format(j))
                else:
                    print('All ok. Tmp ', i, ' : ', tmp)
                    print('Mem free:',gc.mem_free())
                    schedule()
            print("Max temp : ", max_tmp)
        except:
            print('DS18b20 Error')
        gc.collect()
        await asyncio.sleep(12)

def schedule():
    lt=time.localtime()[3:5]
    Ch1 = Ch1Time[0] < lt < Ch1Time[1]
    Ch2 = Ch2Time[0] < lt < Ch2Time[1]
    ds24.turn(lmps[0], int(Ch1), int(Ch2))

async def index(rq):
    await rq.write(H_OK + '\r\n')
    for i in ['header','index','footer']:
        print('/%s.html' % (_DIR+i))
        await send_file(rq, '/%s.html' % (_DIR+i), )

async def sys_info(rq):
    await rq.write(H_OK + '\r\n')
    for i in ['header','sys_info','footer']:
        await send_file(rq, '/%s.html' % (_DIR+i), )


async def assets(rq):
    await rq.write(H_OK)
    args = {}
    filename = rq.url.split('/')[-1]
    if filename.endswith('.png'):
        args = {'binary': True}
    await rq.write("\r\n")
    await send_file(
        rq,
        '/%s/%s' % (_DIR, filename),
        **args,
    )

async def files(rq):
    await rq.write(H_OK + '\r\n')
    for i in ['header','files','footer']:
        await send_file(rq, '/%s.html' % (_DIR+i), )

async def show_content(rq):
    await rq.write(H_OK + '\r\n')
    await send_file(rq, _DIR+'header.html' )
    await send_file(rq, _DIR+'show_content.html' )

    file_name = rq.url.split('?file_name=')[1]
    print("file_name: ", file_name)
    content =open(file_name).read()
    dd = f""" <script>  let tt = document.querySelector("textarea");
        tt.value=new String(`{content}`).toString()
    </script>"""
    await rq.write(dd)
    await send_file(rq, _DIR+'footer.html' )
    
    #for i in ['header','show_content','footer']:
        #await send_file(rq, '/%s.html' % (_DIR+i), )


async def scale(rq):
    await rq.write(H_OK + '\r\n')
    for i in ['header','scale','footer']:
        await send_file(rq, '/%s.html' % (_DIR+i), )


async def api_download(rq):
    await rq.write(H_OK)

    filename = rq.url[len(rq.route.rstrip("*")) - 1:].strip("/")
    await rq.write("Content-Type: application/octet-stream\r\n")
    await rq.write("Content-Disposition: attachment; filename=%s\r\n\r\n" % filename)
    await send_file(rq, filename)


async def upload(rq):
    if rq.method != "PUT":
        raise HttpError(rq, 501, "Not Implemented")

    bytesleft = int(rq.headers.get('Content-Length', 0))

    if not bytesleft:
        await rq.write("HTTP/1.1 204 No Content\r\n\r\n")
        return

    output_file = rq.url[len(rq.route.rstrip("*")) - 1:].strip("\/")
    tmp_file = output_file + '.tmp'

    try:
        with open(tmp_file, 'wb') as o:
            while bytesleft > 0:
                chunk = await rq.read(min(bytesleft, 64))
                o.write(chunk)
                bytesleft -= len(chunk)
            o.flush()
    except OSError as e:
        raise HttpError(rq, 500, "Internal error")

    try:
        uos.remove(output_file)
    except OSError as e:
        pass

    try:
        uos.rename(tmp_file, output_file)
    except OSError as e:
        raise HttpError(rq, 500, "Internal error")

    await api_send_response(rq, 201, "Created")


async def owscan(rq):
    await rq.write(H_OK+'\r\n')
    await send_file(rq,'/%s/header.html' % _DIR, )
    await rq.write('<h1>OW scan</h1>')
    body = '<ul>'
    fROMS = onewire.OneWire(machine.Pin(ow_pin)).scan()
    await asyncio.sleep_ms(ds18_delay)
    print(fROMS)
    for i in fROMS:
        body = body + '<li>' + '<a id="'+str(b2h(i,':'))+'" href="/ow' + '?r=' + str(b2h(i,':')) + '">' + str(b2h(i,':')) + ' </a>' + '</li>'
    body = body + '<ul>'
    await rq.write(body)
    await send_file(rq,'/%s/footer.html' % _DIR, )


async def ow_one(rq):

    try:
        rom = rq.url.split('=')[1][4:20]
        print(rom)
    except:
        print('Except >', rq.url)
    else:
        await send_file(rq,'/%s/header.html' % _DIR, )
        await rq.write('<h1> 1-Wire device </h1>')
        await rq.write('<h2>' + rom + ' </h2>')
        ow_class = ''
        if rom[0:2] == '12':
            ow_class = "Dual switch "
            ow_add = 'turn on/off'
        elif rom[0:2] == '28':
            ow_class = "temp meter ds18b20"
            ow_add = '<span dat="28ff300676200286" id="temp">{temp}</span> <script src="ow_temp.js"></script>'
        body = '<h3>' + ow_class + '</h3>'
        await rq.write(body + ow_add)
        await send_file(rq,'/%s/footer.html' % _DIR, )


async def ow18_api(rq):
    rom = rq.url.split('=')[1][4:20]
    await rq.write(H_OK)
    await rq.write("Content-Type: application/json\r\n\r\n")
    ds18.convert_temp()
    await asyncio.sleep_ms(ds18_delay)
    temp = ds18.read_temp(bytearray(h2b(rom)))
    await rq.write(json.dumps({"temp": temp}))

async def reset(rq):
    machine.reset()

naw.routes = {
    '/': index,
    '/sys_info': sys_info,
    '/assets/*': assets,
    '/ow*': ow_one,
    '/api/status': api_status,
    '/api/upload/*': upload,
    '/api/reset': reset,
    '/api/ls*': api_ls,
    '/api/scale': api_scale,
    '/scale': scale,
    '/api/download/*': api_download,
    '/files': files,
    '/show_content*': show_content,
    '/owscan': owscan,
    '/api/ow18_api*': ow18_api
}

loop = asyncio.get_event_loop()
loop.create_task(keep_connect())
loop.create_task(system_loop())
loop.create_task(naw.run())
loop.create_task(scheduler.proc())  
loop.run_forever()
