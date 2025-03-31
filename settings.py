

class Settings:

    def __init__(self, ):
        self.frequency = 60
        self.base_power = 100
        #self.name = name
        #self.buses = dict()
        #self.s_injection = self.power_injection()


  #  def power_injection(self):
        #everything i did was for a single bus connection make it so it itterates through every bus connection
       # Yij = circuit.ybus.loc[self.bus1, self.bus2] #take the y bus values for a certain bus combination

        # Aidan please put a check to make sure that the YIJ actually has values in it

       # Vi = Bus.bus1.base_kv #i need you to figure out how to get the base kv values for the first bus
       # Vj = Bus.bus2.base_kv # same thing but for the second

       # self.s_injection = Vi * np.conj(Yij * Vj)

      #  P = self.s_injection.real
       # Q = self.s_injection.imag

       # return self.s_injection

s = Settings()
if __name__ == '__main__':

    settings = Settings()
    print(settings.frequency, settings.base_power)

    settings_mod = Settings()
    print(settings_mod.frequency, settings_mod.base_power)
