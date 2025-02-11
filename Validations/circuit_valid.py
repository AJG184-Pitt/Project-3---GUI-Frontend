import unittest

# Import classes
import bus
from circuit import Circuit

class TestMethods(unittest.TestCase):
    def setUp(self):
        self.circuit = Circuit("Test Circuit")

    def test_circuit_buses(self):
        output1 = self.circuit.name
        expected1 = "Test Circuit"
        self.assertEqual(output1, expected1)

        output2 = type(self.circuit.name)
        expected2 = str
        self.assertEqual(output2, expected2)

        output3 = self.circuit.buses
        expected3 = {}
        self.assertEqual(output3, expected3)

        output4 = type(self.circuit.buses)
        expected4 = dict
        self.assertEqual(output4, expected4)

        output5 = self.circuit.bundles
        expected5 = {}
        self.assertEqual(output5, expected5)

        output6 = type(self.circuit.bundles)
        expected6 = dict
        self.assertEqual(output6, expected6)

        output7 = self.circuit.conductors
        expected7 = {}
        self.assertEqual(output7, expected7)

        output8 = type(self.circuit.conductors)
        expected8 = dict
        self.assertEqual(output8, expected8)

        output9 = self.circuit.geometries
        expected9 = {}
        self.assertEqual(output9, expected9)

        output10 = type(self.circuit.geometries)
        expected10 = dict
        self.assertEqual(output10, expected10)

        output11 = self.circuit.geometries
        expected11 = {}
        self.assertEqual(output11, expected11)

        output12 = type(self.circuit.geometries)
        expected12 = dict
        self.assertEqual(output12, expected12)

        output13 = self.circuit.transmission_lines
        expected13 = {}
        self.assertEqual(output13, expected13)

        output14 = type(self.circuit.transmission_lines)
        expected14 = dict
        self.assertEqual(output14, expected14)

    def test_bus_components(self):
        self.circuit.add_bus("Bus1", 230)

        output1 = type(self.circuit.buses["Bus1"])
        expected1 = bus.Bus
        self.assertEqual(output1, expected1)

        output2 = self.circuit.buses["Bus1"].name
        expected2 = "Bus1"
        self.assertEqual(output2, expected2)

        output3 = self.circuit.buses["Bus1"].base_kv
        expected3 = 230
        self.assertEqual(output3, expected3)

        output4 = list(self.circuit.buses.keys())
        expected4 = ["Bus1"]
        self.assertEqual(output4, expected4)

if __name__ == '__main__':
    unittest.main()
