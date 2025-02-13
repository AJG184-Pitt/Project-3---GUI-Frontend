from circuit import Circuit

circuit1 = Circuit("Test Circuit")

#adding the 7 buses
circuit1.add_bus("Bus1", 20)
circuit1.add_bus("Bus2", 230)
circuit1.add_bus("Bus3", 230)
circuit1.add_bus("Bus4", 230)
circuit1.add_bus("Bus5", 230)
circuit1.add_bus("Bus6", 230)
circuit1.add_bus("Bus7", 18)

#adding the 2 transformers
circuit1.add_transformer("T1", "Bus1", "Bus2", 125, 8.5, 10 )
circuit1.add_transformer("T2", "Bus6", "Bus7", 200, 10.5, 12 )

#adding the conductor
circuit1.add_conductor("C1",.642, .0217, .385, 460)

#adding the bundle
circuit1.add_bundle("B1",2, 1.5, "C1")

#adding the geometry
circuit1.add_geometry( "G1", 0, 0, 18.5, 0, 37, 0) # ask about how to find x and y values

#adding the 6 transmission lines
circuit1.add_transmission_line("L1", "Bus2", "Bus4", "B1", "C1", "G1", 10)
circuit1.add_transmission_line("L2", "Bus2", "Bus3", "B1", "C1", "G1", 25)
circuit1.add_transmission_line("L3", "Bus3", "Bus5", "B1", "C1", "G1", 20)
circuit1.add_transmission_line("L4", "Bus4", "Bus6", "B1", "C1", "G1", 20)
circuit1.add_transmission_line("L5", "Bus5", "Bus6", "B1", "C1", "G1", 10)
circuit1.add_transmission_line("L6", "Bus4", "Bus5", "B1", "C1", "G1", 35)

