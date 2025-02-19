class Bus:
    bus_count = 0

    def __init__(self, name: str, base_kv: float):
        self.name = name
        self.base_kv = base_kv
        self.index = Bus.bus_count
        Bus.bus_count += 1
        self.s_sys = 100

if __name__ == '__main__':
    bus1 = Bus("Bus 1", 20)
    bus2 = Bus("Bus 2", 230)

    print(f"Bus 1: {bus1.name}, {bus1.base_kv}, {bus1.index}")
    print(f"Bus 2: {bus2.name}, {bus2.base_kv}, {bus2.index}")
    print(f"Bus count: {Bus.bus_count}")
