from sys import exit, stderr
from pydantic import BaseModel, Field, ValidationError
from src.menu import Menu


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
