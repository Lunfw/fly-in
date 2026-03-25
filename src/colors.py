from pydantic import BaseModel, Field


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
