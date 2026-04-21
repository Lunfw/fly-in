*This project has been created as part of the 42 curriculum by frasomal.*

**## Description**
> | `fly-in` is a drone simulation program about moving drones from A to B. It's a straight-forward project that teaches about pathfinding algorithms.

**## Instructions**
> | You can use the following commands to view the `Makefile` commands:

```sh

make
make help

```

> | You can use the following commands to install requirements on a virtual environment:

```sh

make install
source .venv/bin/activate   # you may change '.venv' by the name of the virtual environment pointed to by the Makefile

```


> | You can use the following commands to run linters:

```sh

make lint
make lint-strict

```

> | You can use the following command to run mandatory tests:

```sh

make run

```

> | Once in the program, use keys `arrow-up` and `arrow-down` to move in the `maps` dir. The program will automatically detect whether `maps` dir exists.
> | If it doesn't, exits with code 1.
> | Use keys `enter` to select and `<ctrl-c>`to exit the program. Additionally, selecting `open` in a file will cat to stdout. Use key `R` to return.

> | You can use the following commands to clean the workspace:

```sh

make clean
deactivate

```

**## Resources**

> | man termios
> | AI has been used for the making of this project, precisely for the complex algorithm. However, code structure, code lint and lint-strict, dir tree, terminal control were entirely made by me.
> | The algorithm is A\*, which I already knew about back in high school.
> | Initially, Dijkstra's algorithm was used but exceeded turn limits for the bonuses. A\* reduced the count significantly and was only a few lines more.

**## Additional Information**

> | As mentioned above, the algorithm is A\*. It's a more complex algorithm than Dijkstra's but allowed the program to be done in a significantly reduced amount of turns. It is just efficient.
> | Logs are the only way to view the drones move. They are printed to stdout, but the user has the option to write them to a log file in a newly-made `logs` dir, files ported as `_.log.txt` files.
