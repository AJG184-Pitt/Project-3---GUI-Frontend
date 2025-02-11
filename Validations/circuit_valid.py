import unittest

import bus
from circuit import Circuit
from bus import Bus

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
