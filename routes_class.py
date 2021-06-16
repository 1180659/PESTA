class routes:

    def __init__(self, address, mask, gw, id):
        self.address = address
        self.mask = mask
        self.gw = gw
        self.id = id


class network:

    def __init__(self, ip, gw, name):
        self.ip = ip
        self.gw = gw
        self.name = name
