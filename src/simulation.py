from src.colors import Colors, Format
from src.generator import Generator
from sys import stdin, stdout
from tty import setraw
from termios import tcgetattr, tcsetattr, TCSADRAIN
from pydantic import BaseModel, Field
from typing import List
from time import sleep


class SimulationDisplay(BaseModel):
    colors: Colors = Field(default=Colors())
    form: Format = Field(default=Format())
    first_draw: bool = Field(default=True)
    nav_lines: int = Field(default=0)
    options: List[str] = Field(default=['Open', 'Generate', 'Close'])
    popped: int = Field(default=0)
    generator: Generator = Field(default=Generator())

    def prompt(self, filename: str) -> None:
        selected: int = 0
        self.prompt_options(self.options, selected, filename)
        while (True):
            key: str = self.get_key()

            if (key == '\x1b[A'):
                if (selected == 0):
                    selected = 0
                else:
                    selected = selected - 1
            elif (key == '\x1b[B'):
                if (selected == len(self.options) - 1):
                    selected = len(self.options) - 1
                else:
                    selected = selected + 1
            elif (self.options[selected] == 'Open' and key == '\r'):
                self.options.pop(selected)
                self.popped += 1
                self.get_content(f'maps/{filename}')
            elif (self.options[selected] == 'Generate' and key == '\r'):
                self.options.pop(selected)
                self.first_draw = True
                self.generator.receive(f'maps/{filename}')
                self.popped += 1
            elif (self.options[selected] == 'Close' and key == '\r'):
                self.options = ['Open', 'Generate', 'Close']
                self.first_draw = True
                break
            elif (key == '\x03'):
                exit(0)
            self.prompt_options(self.options, selected, filename)
        self.popped = 0

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

    def prompt_options(self, items: List[str],
                       selected: int,
                       filename: str) -> None:
        if (self.first_draw):
            self.first_draw = False
        else:
            stdout.write(f'\x1b[{self.nav_lines}A')
            stdout.write('\x1b[J')
            stdout.flush()

        print(self.colors.WHITE)
        print('#   What to do with ', end='')
        print(self.colors.CYAN, end='')
        print(f'{filename}?')
        print(self.colors.RESET)

        max_len: int = max(len(item) for item in items)
        temp: List[str] = []
        for i, item in enumerate(items):
            if (i == selected):
                marker = self.colors.GREEN + 'X' + self.colors.RESET
            else:
                marker = ' '
            padded: str = item.ljust(max_len)
            temp.append(f'[{marker}]    ->| {padded}')
        self.form.putstr(temp)

        self.nav_lines = len(temp) * 2 + self.popped

    def get_content(self, filename: str) -> None:
        with open(filename, 'r') as file:
            buffer: str = file.read()
        file.close()
        lines: int = buffer.count('\n')
        print('\n' + buffer)
        sleep(2)
        print(f'[{self.colors.RED}R{self.colors.RESET}]eturn    -   ', end='')
        print(f'[{self.colors.CYAN}E{self.colors.RESET}]dit')
        while (True):
            key: str = self.get_key()
            if (key == 'R' or key == 'r'):
                break
            elif (key == 'E' or key == 'e'):
                pass
            elif (key == '\x03'):
                exit(0)
        self.nav_lines = lines + 9
