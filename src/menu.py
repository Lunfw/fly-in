from src.colors import Colors, Format
from src.simulation import SimulationDisplay
from pydantic import BaseModel, Field
from os import listdir, path
from termios import tcgetattr, tcsetattr, TCSADRAIN
from tty import setraw
from sys import stderr, stdin, stdout
from typing import Generator, List, Any


class Maps(BaseModel):
    colors: Colors = Field(default=Colors())
    form: Format = Field(default=Format())

    def get_diffs(self) -> Generator[str]:
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

    def get_map(self, folder: str) -> Generator[str]:
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
    sim: SimulationDisplay = Field(default=SimulationDisplay())
    first_draw: bool = Field(default=True)
    nav_lines: int = Field(default=0)
    last_folder: int = Field(default=0)
    is_txt: bool = Field(default=False)
    dirpath: str = Field(default='')

    def display(self) -> None:
        body: List[str] = list(maps for maps in self.maps.get_diffs())
        selected = 0
        self.navigate(body, selected)
        while (True):
            key: str = self.get_key()

            if (key == '\x1b[A'):
                if (selected == 0):
                    selected = 0
                else:
                    selected = selected - 1
            elif (key == '\x1b[B'):
                if (selected == len(body) - 1):
                    selected = len(body) - 1
                else:
                    selected = selected + 1
            elif (body[selected] == '..' and key == '\r'):
                body = list(maps for maps in self.maps.get_diffs())
                selected = self.last_folder
            elif ('txt' in body[selected] and key == '\r'):
                self.is_txt = True
                self.sim.prompt(self.dirpath + '/' + body[selected])
                self.nav_lines += 7
                self.is_txt = False
            elif (key == '\r'):
                self.dirpath = body[selected]
                body = list(self.maps.get_map(body[selected]))
                self.last_folder = selected
                selected = 0
            elif (key == '\x03'):
                break
            if (not self.is_txt):
                self.navigate(body, selected)

    def reset(self) -> None:
        self.first_draw = True
        self.nav_lines = 0

    def get_key(self) -> str:
        fd: int = stdin.fileno()
        old: List[Any] = tcgetattr(fd)
        try:
            setraw(fd)
            char = stdin.read(1)
            if (char == '\x1b'):
                char += stdin.read(2)
            return (char)
        finally:
            tcsetattr(fd, TCSADRAIN, old)

    def navigate(self, items: List[str], selected: int) -> None:
        if (self.first_draw):
            self.first_draw = False
        else:
            stdout.write(f'\x1b[{self.nav_lines}A')
            stdout.write('\x1b[J')
            stdout.flush()

        head: List[str] = [
            self.colors.CYAN,
            'Welcome!',
            'This is a drone simulation program.',
            self.colors.RESET,
            'omg get_next_line reference!!\n',
            ]
        self.form.centered(head)
        self.form.centered('V Available maps V')
        self.form.centered('----------------')

        print(self.colors.GREEN)
        max_len: int = max(len(item) for item in items)
        temp: List[str] = []
        for i, item in enumerate(items):
            if (i == selected):
                marker = '#'
            else:
                marker = ' '
            padded: str = item.ljust(max_len)
            temp.append(f'[{marker}]    ->| {padded}')
        self.form.centered(temp)
        print(self.colors.RESET)

        self.nav_lines = len(head) + (len(items) * 2 + 6)
        self.form.draw_margin()
