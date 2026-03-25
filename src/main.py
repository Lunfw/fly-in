from sys import exit, stderr, argv
from pydantic import BaseModel, Field, ValidationError
from src.colors import Colors
from typing import IO


class GeneralErrors(Exception):
    pass


class InputErrors(GeneralErrors):
    pass


class SimulationManager(BaseModel):
    '''
        Simulation Manager:
            ->  This will initiate a parser for the drones.
    '''
    nb_drones: int = Field(ge=1, default=5)
    start_hub: tuple = Field(default=(0, 0))
    end_hub: tuple = Field(default=(5, 5))


class Main(BaseModel):
    def sim_lib(self, file: IO[str]) -> SimulationManager:
        '''
        Library for inputs and such.
    '''
        from src.parser import Parser
        return Parser().parse_args(file)

    def main(self, file: IO):
        '''
            Small main program.
        '''
        try:
            simulation = self.sim_lib(file)
        except ValidationError as ve:
            print(f'Caught: {ve[0]['msg']}', file=stderr)
            exit(1)
        finally:
            exit(0)


if (__name__ == '__main__'):
    if (len(argv) != 2):
        print('Usage: python3 main.py <file>', file=stderr)
        exit(1)
    Main().main(argv[1])
