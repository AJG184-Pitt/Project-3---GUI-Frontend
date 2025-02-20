import warnings

class Bus:
    bus_count = 0

    def __init__(self, name: str, base_kv: float, bus_type, vpu=1.0, delta=0.0):
        self.name = name
        self.base_kv = base_kv
        self.index = Bus.bus_count
        Bus.bus_count += 1
        self.s_sys = 100
        self.vpu = vpu
        self.delta = delta

        if bus_type == "Slack Bus" or bus_type == "PQ Bus" or bus_type == "PV Bus":
            self.bus_type = bus_type
        else:
            warnings.warn("bus_type not specified to 'Slack Bus', 'PQ Bus', or 'PV Bus'. Defaulting to 'Slack Bus'")
            self.bus_type = "Slack Bus"

if __name__ == '__main__':
    bus1 = Bus("Bus 1", 20, "PV Bus")
    bus2 = Bus("Bus 2", 230, "PQ Bus")

    print(f"Bus 1: {bus1.name}, {bus1.base_kv}, {bus1.index}")
    print(f"Bus 2: {bus2.name}, {bus2.base_kv}, {bus2.index}")
    print(f"Bus count: {Bus.bus_count}")
