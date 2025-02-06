from transformer import Transformer

transformer1 = Transformer("T1", "B1", "B2", 125, 8.5, 10)

print(f"{transformer1.name} {transformer1.bus1}, {transformer1.bus2}, {transformer1.power_rating}, {transformer1.impedance_percent}, {transformer1.x_over_r_ratio}")
