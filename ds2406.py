def turn(ow, Rom, PinA=0, PinB=0):
    ow.reset()
    ow.select_rom(Rom)
    _sb = PinA * 64 + PinB * 32
    ow.write([85, 7, 0, _sb])
    for _n in range(1, 6):
        ow.readbyte()

