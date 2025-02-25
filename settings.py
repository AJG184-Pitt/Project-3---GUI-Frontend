class Settings:

    def __init__(self, frequency=60, base_power=100):
        self.frequency = frequency
        self.base_power = base_power

if __name__ == '__main__':

    settings = Settings()
    print(settings.frequency, settings.base_power)

    settings_mod = Settings(30, 50)
    print(settings_mod.frequency, settings_mod.base_power)
