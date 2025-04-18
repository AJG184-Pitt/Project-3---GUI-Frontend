from bus import Bus

class Generator:

    def __init__(self, name: str, bus: Bus, voltage_setpoint: float, mw_setpoint: float):
        self.name = name
        self.bus = bus
        self.voltage_setpoint = voltage_setpoint
        self.mw_setpoint = mw_setpoint

if __name__ == '__main__':
    bus = Bus("Bus 1", 20, "PV Bus")
    generator = Generator("gen1", bus, 10, 20)

    print(generator.name, generator.bus, generator.voltage_setpoint, generator.mw_setpoint)
