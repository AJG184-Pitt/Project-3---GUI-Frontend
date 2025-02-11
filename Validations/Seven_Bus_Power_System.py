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

#adding the transformers
circuit1.add_transformer("T1", "Bus1", "Bus2", 125, 8.5, 10 )
circuit1.add_transformer("T2", "Bus6", "Bus7", 200, 10.5, 12 )

#adding the conductor
circuit1.add_conductor("C1",.642, .0217, .385, 460)
#adding the bundle
circuit1.add_bundle("B1",2, 1.5, "C1")
#adding the geometry
#geometry_obj = Geometry(name, xa, ya, xb, yb, xc, yc)
circuit1.add_geometry( "G1", )

#adding the transmission lines
#transmission_line_obj = TransmissionLine(name, bus1, bus2, bundle, conductor, geometry, length,f)

