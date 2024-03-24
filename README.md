
![Logo](https://github.com/Kokolekion/CounterProject/assets/65463088/809f1cec-fc3e-4fdc-9e2a-1b24375147c1)


# Project Counter Overflow

Silly willy spamming for silly willy people from [okayxairen Community](https://discord.com/invite/cTyWY42Ycb)

[WHATHOW Website](https://whathow.neocities.org/) is the website and the counter is in it.

The goal in life is a very simple one, its not about money.. men.. or anything in between!

Its to make this counter above go to 999,999,999 and see what happens.. maybe we get choco and who doesn't like choco!

## Installation + Running
```bash
$ git clone https://github.com/astoko/CounterProject.git
$ cd CounterProject
$ ulimit -n 8192
$ ./run.sh
```

ulimit -n will need to be above ~7000 for this to work.
It uses ~20gb of ram, but each individual process is only about 20-30mb of usage.

## Dependencies
 - Python
 - Linux/MacOS (WSL also works)

## Contributors

#### @jased (le funny dood)  
#### @crhbo (the whathow owner)  
#### @urufusan (he Kewl)  

and everyone running this code for some reason XD

## FAQ

#### Is this fastest way possible to complete this project?

Most probably not but ~~i sure hope someday we get better and faster ways of doing this!~~ the new python version is faster than the js one, but could still be faster XD

#### Why is there both `run.sh` and `main.py`?
`main.py` does not deal with SIGINT, and will therefore leave orphans running.

#### Is this safe, Will i get in trouble of sending so many requests?

Yes, the owner of the site has said that its okay, From the owner: "break this :3"

#### Is the code AI generated?
Only run.sh.

## Licenses Used

[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
