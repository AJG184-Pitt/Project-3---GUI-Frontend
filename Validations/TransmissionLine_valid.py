from transmissionline import TransmissionLine

line1 = TransmissionLine("Line 1", TransmissionLine.bus1, TransmissionLine.bus2, TransmissionLine.bundle, TransmissionLine.geometry, 10)


print(line1.name, line1.bus1.name, line1.bus2.name, line1.length)
print(line1.zbase, line1.ybase)
print(line1.xseries, line1.yshunt, line1.yseries)

if Bus.bus_count == 2:
    print("Bus count is correct = 2")
else:
    print("Bus count is wrong")