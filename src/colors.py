from pydantic import BaseModel, Field
from shutil import get_terminal_size
from sys import stdout
from typing import IO, List


class Colors(BaseModel):
    '''
        A small library for color codes and such.
    '''
    BLACK: str = Field(default='\033[1;30m')
    RED: str = Field(default='\033[1;31m')
    GREEN: str = Field(default='\033[1;32m')
    YELLOW: str = Field(default='\033[1;33m')
    BLUE: str = Field(default='\033[1;34m')
    PURPLE: str = Field(default='\033[1;35m')
    CYAN: str = Field(default='\033[1;36m')
    WHITE: str = Field(default='\033[1;37m')
    GREY: str = Field(default='\033[1;90m')
    RESET: str = Field(default='\033[0m')


class Format(BaseModel):
    colors: Colors = Field(default=Colors())
    '''
        Small lib for text formatting.
    '''
    def centered(self, text: (List[str] | str), fd: IO[str] = stdout) -> None:
        width = get_terminal_size().columns
        if (type(text) is str):
            print(text.center(width), file=fd, flush=True)
            return (None)
        for line in text:
            print(line.center(width), file=fd, flush=True)

    def listing(self, text: (List[str] | str),
                marker: str = ' ') -> str | List[str]:
        temp: List[str] = []
        if (type(text) is str):
            return (f'[{marker}]    -> ' + text)
        max_len: int = len(text[0])
        for line in text:
            if (max_len < len(line)):
                max_len = len(line)
        for line in text:
            while (len(line) < max_len):
                line += ' '
            temp.append(f'[{marker}]    ->  ' + line)
        return (temp)

    def ls(self, text: (List[str] | str)) -> str | List[str]:
        temp: List[str] = []
        if (type(text) is str):
            return (text)
        for line in range(len(text)):
            if (line < len(text)):
                temp.append(text[line])
            else:
                temp.append(text[line])
        return (temp)

    def putstr(self, text: (List[str] | str)) -> None:
        if (type(text) is str):
            print(text)
            return
        for word in text:
            print(word)

    def draw_margin(self) -> None:
        width = get_terminal_size().columns
        margin = self.colors.WHITE + '|< '
        for i in range(width - 6):
            margin += '='
        margin += ' >|' + self.colors.RESET
        self.centered(margin)
