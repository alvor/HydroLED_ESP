class DS2406:
    st_tab = {}

    def __init__(self, _ow, roms):
        self.ow = _ow
        for i in roms:
            self.st_tab.update({i: [1, 1]})

    def turn(self, Rom, PinA=0, PinB=0):

        self.ow.reset()
        self.ow.select_rom(Rom)
        _sb = PinA * 64 + PinB * 32
        self.ow.write([85, 7, 0, _sb])
        for _n in range(1, 6):
            self.ow.readbyte()

    def set(self, Rom, Ch, Value):
        try:
            self.st_tab[Rom][Ch] = Value
            self.turn(h2b(Rom), self.st_tab[Rom][0], self.st_tab[Rom][1])
        except:
            print('Not found rom:', Rom)

    def is_its_off(self, Roms):
        iio = True
        for i in Roms:
            try:
                iio = (self.st_tab[i][0] == 1 and self.st_tab[i][1] == 1) and iio
            except:
                print('Error is_its_off')
        return iio
