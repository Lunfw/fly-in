from src.colors import Colors, Format
from pydantic import BaseModel, Field
from os import listdir
from termios import tcgetattr, tcsetattr, TCSADRAIN
from tty import setraw
from sys import stderr, stdin
from typing import Generator, List


class Maps(BaseModel):
    colors: Colors = Field(default=Colors())
    form: Format = Field(default=Format())

    def get_maps(self) -> Generator:
        try:
            for entity in listdir('maps'):
                yield entity
        except FileNotFoundError:
            print(self.colors.RED)
            self.form.centered('No maps found.', stderr)
            print(self.colors.RESET)
            for files in listdir('.'):
                if ('maps' in files):
                    self.form.centered('Maybe if you unarchived this:')
                    self.form.centered(files)
                    break
            exit(1)


class Menu(BaseModel):
    colors: Colors = Field(default=Colors())
    form: Format = Field(default=Format())
    maps: Maps = Field(default=Maps())

    def display(self) -> None:
        head: List = [
                    self.colors.CYAN,
                    'Welcome!',
                    'This is a drone simulation program.',
                    self.colors.WHITE,
                    'omg get_next_line reference!!\n',
                    ]
        self.form.centered(head)
        body: List = list(maps for maps in self.maps.get_maps())
        self.form.centered(self.form.listing(body))
        navigate.first_draw = True
        while (True):
            key = get_key()

            if (key == '\x1b[A'):
                selected = (selected - 1) % len(body)
            elif (key == '\x1b[B'):
                selected = (selected + 1) % len(body)
            elif (key == '\x03'):
                break
            navigate(body, selected)


    def get_key(self):
        fd = stdin.fileno()
        old = tcgetattr(fd)
        try:
            setraw(fd)
            char = stdin.read(1)
            if (char == '\x1b'):
                char += stdin.read(2)
            return (char)
        finally:
            tcsetattr(fd, TCSADRAIN, old)

    def navigate(items, selection):
        if (navigate.first_draw):
            navigate.first_draw = False
        else:
            stdout.write('\x1b[{len(items)}A')

        for i, item in enumerate(items):
            if (i == selected):
                marker = 'x'
            else:
                marker = ' '
            self.form.centered(self.form.listing(item))
