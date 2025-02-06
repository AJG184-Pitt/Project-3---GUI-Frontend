from transmissionline import TransmissionLine

line1 = TransmissionLine("Line 1", "bus1","bus2", TransmissionLine.bundle, TransmissionLine.geometry, 10)


print(line1.name, line1.bus1.name, line1.bus2.name, line1.length)
print(line1.zseries, line1.bseries, line1.yseries)
