from src.main import SimulationManager
from typing import IO
from sys import exit


class Parser:
    def parse_args(self, args: IO):
        temp: SimulationManager = SimulationManager()

        with open(args, 'r') as file:
            print(file.read())
        return (0)
