from transmissionline import TransmissionLine
from bundle import Bundle
from conductor import Conductor

conductor1 = Conductor("Partridge", 0.642, 0.0217, 0.385, 460)
bundle1 = Bundle("Bundle 1", 2, 1.5, conductor1)
transmission1 = TransmissionLine("T1", "B1", "B2", 2, )

