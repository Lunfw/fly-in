from src.colors import Colors, Format
from pydantic import BaseModel, Field
from os import listdir, path
from termios import tcgetattr, tcsetattr, TCSADRAIN
from tty import setraw
from sys import stderr, stdin, stdout
from typing import Generator, List


class Maps(BaseModel):
    colors: Colors = Field(default=Colors())
    form: Format = Field(default=Format())

    def get_diffs(self) -> Generator:
        temp: List[str] = []
        try:
            for entity in listdir('maps'):
                if (path.isdir(f'maps/{entity}')):
                    temp.append(entity)
                else:
                    pass
            for i in sorted(temp):
                yield i
        except FileNotFoundError:
            print(self.colors.RED)
            self.form.centered('No maps found.', stderr)
            for files in listdir('.'):
                if ('maps' in files):
                    self.form.centered('Did you forget to extract this?')
                    self.form.centered(files)
                    break
            print(self.colors.RESET)
            exit(1)

    def get_map(self, folder: str) -> Generator:
        temp: List[str] = []
        temp.append('..')
        try:
            for entity in listdir(f'maps/{folder}'):
                temp.append(entity)
            else:
                pass
            for i in sorted(temp):
                yield i
        except FileNotFoundError:
            print(self.colors.RED)
            self.form.centered("This isn't supposed to happen...", stderr)
            print(self.colors.RESET)
            exit(1)


class Menu(BaseModel):
    colors: Colors = Field(default=Colors())
    form: Format = Field(default=Format())
    maps: Maps = Field(default=Maps())
    first_draw: bool = Field(default=True)
    nav_lines: int = Field(default=0)

    def display(self) -> None:
        body: List = list(maps for maps in self.maps.get_diffs())
        selected = 0
        self.navigate(body, selected)
        while (True):
            key: str = self.get_key()

            if (key == '\x1b[A'):
                selected = (selected - 1) % len(body)
            elif (key == '\x1b[B'):
                selected = (selected + 1) % len(body)
            elif (body[selected] == '..' and key == '\r'):
                    body = list(maps for maps in self.maps.get_diffs())
            elif (key == '\r'):
                selected = selected % len(body)
                body = list(self.maps.get_map(body[selected]))
            elif (key == '\x03'):
                break
            self.navigate(body, selected)

    def get_key(self) -> str:
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

    def navigate(self, items, selection):
        if (self.first_draw):
            self.first_draw = False
        else:
            stdout.write(f'\x1b[{self.nav_lines}A')
            stdout.write('\x1b[J')
            stdout.flush()

        head: List = [
            self.colors.CYAN,
            'Welcome!',
            'This is a drone simulation program.',
            self.colors.RESET,
            'omg get_next_line reference!!\n',
            ]
        self.form.centered(head)
        self.form.centered('V Available maps V')
        self.form.centered('----------------')
        self.form.centered(self.form.ls(items))

        print(self.colors.GREEN)
        max_len: int = max(len(item) for item in items)
        temp: List[str] = []
        for i, item in enumerate(items):
            if (i == selection):
                if (i == selection):
                    marker = '#'
                else:
                    marker = ' '
                padded: str = item.ljust(max_len)
                temp.append(f'[{marker}]    ->| {padded}')
        self.form.centered(temp)
        print(self.colors.RESET)

        self.nav_lines = len(head) + (len(items) * 2 + 5)
        self.form.draw_margin()
