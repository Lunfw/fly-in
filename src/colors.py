from pydantic import BaseModel, Field
from shutil import get_terminal_size
from sys import stdout
from typing import Any, IO


class Format(BaseModel):
    '''
        Small lib for text formatting.
    '''
    def centered(self, text: (tuple | str), fd: IO = stdout) -> None:
        width = get_terminal_size().columns
        if (type(text) is str):
            print(text.center(width), file=fd)
            return (None)
        for line in text:
            print(line.center(width), file=fd)


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
