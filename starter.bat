start cmd /k python main.py 0 localhost:20000 localhost:20001 localhost:20002
start cmd /k python main.py 1 localhost:20001 localhost:20002 localhost:20003
start cmd /k python main.py 2 localhost:20002 localhost:20003 localhost:20004
start cmd /k python main.py 3 localhost:20003 localhost:20004 localhost:20005
start cmd /k python main.py 4 localhost:20004 localhost:20005 localhost:20000
start cmd /k python main.py 5 localhost:20005 localhost:20000 localhost:20001