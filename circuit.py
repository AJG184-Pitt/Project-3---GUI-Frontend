from bundle import Bundle
from bus import Bus
from conductor import Conductor
from geometry import Geometry
from transformer import Transformer
from transmissionline import TransmissionLine

class Circuit:
    def __init__(self, name: str):
        self.name = name
        self.bundles = dict()
        self.buses = dict()
        self.conductors = dict()
        self.geometries = dict()
        self.transformers = dict()
        self.transmission_lines = dict()

    def add_bundle(self, name, num_conductors, spacing, conductor):
        bundle_obj = Bundle(name, num_conductors, spacing, self.conductors[conductor])
        self.bundles[name] = bundle_obj

    def add_bus(self, name, bas_kv):
        bus_obj = Bus(name, bas_kv)
        self.buses[name] = bus_obj
        
    def add_conductor(self, name, diam, GMR, resistance, ampacity):
        conductor_obj = Conductor(name, diam, GMR, resistance, ampacity)
        self.conductors[name] = conductor_obj
    
    def add_geometry(self, name, xa, ya, xb, yb, xc, yc):
        geometry_obj = Geometry(name, xa, ya, xb, yb, xc, yc)
        self.geometries[name] = geometry_obj
    
    def add_transformer(self, name, bus1, bus2, power_rating, impedance_percent, x_over_r_ratio):
        transformer_obj = Transformer(name, self.buses[bus1], self.buses[bus2], power_rating, impedance_percent, x_over_r_ratio)
        self.transformers[name] = transformer_obj
    
    def add_transmission_line(self, name, bus1, bus2, bundle, conductor, geometry, length):
        transmission_line_obj = TransmissionLine(name, self.buses[bus1], self.buses[bus2], self.bundles[bundle], self.conductors[conductor], self.geometries[geometry], length)
        self.transmission_lines[name] = transmission_line_obj
