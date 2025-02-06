from transmissionline import TransmissionLine
from bus import Bus
from bundle import Bundle
from conductor import Conductor
from geometry import Geometry

bus1 = Bus("Bus_1", 180)
bus2 = Bus("Bus_2", 230)
conductor1 = Conductor("Partridge", 0.642, 0.0217, 0.385, 460)
bundle1 = Bundle("Bundle 1", 2, 1.5, conductor1)
geometry1 = Geometry("Geometry 1", 0, 0, 18.5, 0,37, 0)

line1 = TransmissionLine("Line 1", bus1, bus2, bundle1, geometry1, 10)

print(f"Line: {line1.name}, bus1: , bus2: , bundle1 : geometry1: {line1.geometry}, geometry: {line1.length}")
