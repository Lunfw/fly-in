from sys import exit, stderr
from pydantic import BaseModel, Field, ValidationError
from src.menu import Menu


class SimulationManager(BaseModel):
    '''
        Simulation Manager:
            ->  This will initiate a parser for the drones.
    '''
    nb_drones: int = Field(ge=1, default=5)
    start_hub: tuple = Field(default=(0, 0))
    end_hub: tuple = Field(default=(5, 5))


class Main(BaseModel):
    def main(self):
        '''
             Small main program.
        '''
        try:
            menu = Menu()
            menu.display()
        except ValidationError as ve:
            print(f'Caught: {ve[0]['msg']}', file=stderr)
            exit(1)
        finally:
            exit(0)


if (__name__ == '__main__'):
    Main().main()
