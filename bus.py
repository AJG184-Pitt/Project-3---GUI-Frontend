class Bus:
    bus_count = 0

    def __init__(self, name: str, base_kv: float):
        self.name = name
        self.base_kv = base_kv
        self.index = Bus.bus_count
        Bus.bus_count += 1
