## To run the code from this repository you should have the following installed:
- [git](https://git-scm.com/install/windows)
- [python 3.13](https://www.python.org/downloads/release/python-3130/)
- [uv environment manager](https://docs.astral.sh/uv/getting-started/installation/)
- IDE (VS code, Pycharm etc.)

## Once you have installed these you can open the folder where you want to have the project repository in your IDE. And then run the following command in your terminal:
```bash
git clone https://github.com/satvik007vk/bike_route_planner.git`  
```
Yay! you have the repository cloned now!
 
Now in your terminal, make sure you are in the project folder: path_to_project_folder/bike_route_planner
If not, you can just run the command `cd path_to_project_folder/bike_route_planner` 

Next you need to run the command  
```bash
uv sync
```
Every package will be installed automatically once you run the command.

Finally run the command:
```bash
uv run python visualise_data.py
```
You should be now able to see a message in your terminal.


