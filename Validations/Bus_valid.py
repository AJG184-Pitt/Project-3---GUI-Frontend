from bus import Bus

bus1 = Bus("Bus 1", 20)
bus2 = Bus("Bus 2", 230)

print(f"Bus 1: {bus1.name}, {bus1.base_kv}, {bus1.index}")
print(f"Bus 2: {bus2.name}, {bus2.base_kv}, {bus2.index}")

if Bus.bus_count == 2:
    print("Bus count is correct = 2")
else:
    print("Bus count is wrong")
