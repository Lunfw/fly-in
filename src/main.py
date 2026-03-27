from sys import exit
from pydantic import ValidationError
from src.menu import Menu


class Main:
    def main(self) -> None:
        '''
             Small main program.
        '''
        try:
            menu = Menu()
            menu.display()
        except ValidationError:
            exit(1)
        finally:
            exit(0)


if (__name__ == '__main__'):
    Main().main()
