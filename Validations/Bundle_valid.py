from bundle import Bundle
from conductor import Conductor


conductor1 = Conductor("Partridge", 0.642, 0.0217,0.385, 460)
bundle1 = Bundle("Bundle 1", 2, 1.5, conductor1)

print(bundle1.name, bundle1.num_conductors, bundle1.spacing, bundle1.conductor)
