def turn(self, Rom, PinA=0, PinB=0):
    self.ow.reset()
    self.ow.select_rom(Rom)
    _sb = PinA * 64 + PinB * 32
    self.ow.write([85, 7, 0, _sb])
    for _n in range(1, 6):
        self.ow.readbyte()

