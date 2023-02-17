import gc
import machine, ds2406, onewire, ds18x20
import network, ntptime
import uasyncio as asyncio
import ubinascii as b2h
import json
import time
import sys
from nanoweb import Nanoweb, send_file

H_OK = 'HTTP/1.1 200 OK\r\n'
MAXTEMP = 60
ssid = json.loads(open('wifipsw.psw').read()).get('ssid')
pswd = json.loads(open('wifipsw.psw').read()).get('pswd')

sta = network.WLAN(network.STA_IF)

hl_timezone = 7
ow_pin = 2
ds18_delay = 730

Ch1Time=((8,00),(20,00))
Ch2Time=((8,15),(19,45))

#lmps = [b'128a9bb4000000fc', b'1294e7b8000000ea']
lmps=[b'121b79d6000000b4']
#tmps = [b'28ff0c207620025a']
tmps=[b'28ff7a16762002ea']

ow = onewire.OneWire(machine.Pin(ow_pin))
ds18 = ds18x20.DS18X20(ow)
ds24 = ds2406.DS2406(ow, lmps)
naw = Nanoweb()
naw.assets_extensions += ('ico', 'png',)
_DIR = './_web/'
naw.STATIC_DIR = _DIR


def get_ow():
    ow = onewire.OneWire(machine.Pin(ow_pin))
    roms = ow.scan()
    return roms


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


async def api_ls(request):
    gc.collect()
    await request.write(H_OK)
    await request.write("Content-Type: application/json\r\n\r\n")
    await request.write('{"files": [%s]}' % ', '.join(
        '"' + f + '"' for f in sorted(uos.listdir('.'))
    ))


async def api_status(request):
    """API status endpoint"""
    await request.write(H_OK)
    await request.write("Content-Type: application/json\r\n\r\n")
    mem_free = gc.mem_free()
    date_str, time_str, uptime_str = get_time()
    await request.write(json.dumps({
        "date": date_str,
        "time": time_str,
        "mem_free": mem_free,
        "uptime": uptime_str,
        'python': '{} {} {}'.format(
            sys.implementation.name,
            '.'.join(
                str(s) for s in sys.implementation.version
            ),
            sys.implementation.mpy
        ),
        'platform': str(sys.platform),
    }))


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
                    tmp = ds18.read_temp(b2h.unhexlify(i))
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
        await asyncio.sleep(5)

def schedule():
    lt=time.localtime()[3:5]
    Ch1 = Ch1Time[0] < lt < Ch1Time[1]
    Ch2 = Ch2Time[0] < lt < Ch2Time[1]
    ds24.turn(lmps[0], int(Ch1), int(Ch2))

async def index(request):
    await request.write(H_OK + '\r\n')
    for i in ['header','index','footer']:
        await send_file(request, './%s.html' % (_DIR+i), )

async def sys_info(request):
    await request.write(H_OK + '\r\n')
    for i in ['header','sys_info','footer']:
        await send_file(request, './%s.html' % (_DIR+i), )

async def assets(request):
    await request.write(H_OK)
    args = {}
    filename = request.url.split('/')[-1]
    if filename.endswith('.png'):
        args = {'binary': True}
    await request.write("\r\n")
    await send_file(
        request,
        './%s/%s' % (_DIR, filename),
        **args,
    )


async def test_req(request):
    await request.write(H_OK + '\r\n')
    await send_file(
        request,
        './%s/test_req.html' % _DIR,
    )


async def files(request):
    await request.write(H_OK + '\r\n')
    for i in ['header','files','footer']:
        await send_file(request, './%s.html' % (_DIR+i), )


async def api_download(request):
    await request.write(H_OK)

    filename = request.url[len(request.route.rstrip("*")) - 1:].strip("/")
    await request.write("Content-Type: application/octet-stream\r\n")
    await request.write("Content-Disposition: attachment; filename=%s\r\n\r\n" % filename)
    await send_file(request, filename)


async def upload(request):
    if request.method != "PUT":
        raise HttpError(request, 501, "Not Implemented")

    bytesleft = int(request.headers.get('Content-Length', 0))

    if not bytesleft:
        await request.write("HTTP/1.1 204 No Content\r\n\r\n")
        return

    output_file = request.url[len(request.route.rstrip("*")) - 1:].strip("\/")
    tmp_file = output_file + '.tmp'

    try:
        with open(tmp_file, 'wb') as o:
            while bytesleft > 0:
                chunk = await request.read(min(bytesleft, 64))
                o.write(chunk)
                bytesleft -= len(chunk)
            o.flush()
    except OSError as e:
        raise HttpError(request, 500, "Internal error")

    try:
        uos.remove(output_file)
    except OSError as e:
        pass

    try:
        uos.rename(tmp_file, output_file)
    except OSError as e:
        raise HttpError(request, 500, "Internal error")

    await api_send_response(request, 201, "Created")


async def control(request):
    await request.write(H_OK)
    await send_file(
        request,
        './%s/header.html' % _DIR, )
    await request.write('<h1> 1-Wire devices scan </h1>')
    body = '<ul>'
    fROMS = get_ow()
    await asyncio.sleep_ms(ds18_delay)
    print(fROMS)
    for i in fROMS:
        body = body + '<li>' + '<a href="/onewire' + '?r=' + str(b2h.hexlify(i)) + '">' + str(
            b2h.hexlify(i)) + ' </a>' + '</li>'
    body = body + '<ul>'
    await request.write(body)
    await send_file(
        request,
        './%s/footer.html' % _DIR, )


async def ow18_one(request):
    # await send_file(request, './%s/ow18.html' % _DIR,)
    # return
    try:
        rom = request.url.split('=')[1][4:20]
        print(rom)
    except:
        print('Except >', request.url)
    else:
        await send_file(
            request,
            './%s/header.html' % _DIR, )
        await request.write('<h1> 1-Wire device </h1>')
        await request.write('<h2>' + rom + ' </h2>')
        ow_class = ''
        if rom[0:2] == '12':
            ow_class = "Dual switch "
            ow_add = 'turn on/off'
        elif rom[0:2] == '28':
            ow_class = "temp meter ds18b20"
            ow_add = '<span dat="28ff300676200286" id="temp">{temp}</span> <script src="ow_temp.js"></script>'
        body = '<h3>' + ow_class + '</h3>'
        await request.write(body + ow_add)
        await send_file(
            request,
            './%s/footer.html' % _DIR, )


async def ow18_api(request):
    print(request.url)
    rom = request.url.split('=')[1][4:20]
    await request.write(H_OK)
    await request.write("Content-Type: application/json\r\n\r\n")
    ds18.convert_temp()
    await asyncio.sleep_ms(ds18_delay)
    temp = ds18.read_temp(bytearray(b2h.unhexlify(rom)))
    await request.write(json.dumps({"temp": temp}))
    print('*********************')


naw.routes = {
    '/': index,
    '/sys_info': sys_info,
    '/assets/*': assets,
    '/ow18*': ow18_one,
    '/api/status': api_status,
    '/api/upload/*': upload,
    '/api/ls': api_ls,
    '/api/download/*': api_download,
    '/test_req': test_req,
    '/files': files,
    '/control': control,
    '/api/ow18_api*': ow18_api
}

loop = asyncio.get_event_loop()
loop.create_task(keep_connect())
loop.create_task(system_loop())
loop.create_task(naw.run())
loop.run_forever()
