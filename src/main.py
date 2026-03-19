from sys import exit, stderr
from pydantic import BaseModel, Field
from src.colors import Colors


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


def sim_lib() -> SimulationManager:
    '''
        Library for inputs and such.
    '''
    return (SimulationManager(
        nb_drones=input("nb_drones: "),
        start_hub=input("start_hub: "),
        end_hub=input("end_hub: ")
        )
    )


def main():
    '''
        Small main program.
    '''
    try:
        simulation = sim_lib()
    except ValidationError as ve:
        print(f'Caught: {ve[0]['msg']}', stderr) 
        exit(1)
    finally:
        exit(0)


if (__name__ == '__main__'):
    main()
