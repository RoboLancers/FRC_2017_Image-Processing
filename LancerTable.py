from networktables import NetworkTable


class LancerTable():

    def __init__(self):
        NetworkTable.setIPAddress('10.51.15.2')
        NetworkTable.setClientMode()
        NetworkTable.initialize()

        self.nt = NetworkTable.getTable('jetson')


def get_network_table(self):
    return self.nt
