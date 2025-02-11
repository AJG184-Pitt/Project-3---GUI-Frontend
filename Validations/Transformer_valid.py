from transformer import Transformer

transformer1 = Transformer("T1", "bus1", "bus2", 125, 8.5, 10)

print(f"{transformer1.name} {transformer1.bus1}, {transformer1.bus2}, {transformer1.power_rating}, {transformer1.impedance_percent}, {transformer1.x_over_r_ratio}")
print(transformer1.calc_admittance())
print(transformer1.calc_impedance())
