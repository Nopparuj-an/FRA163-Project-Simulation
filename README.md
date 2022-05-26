# FRA163 Project Simulation

By FRAB8 G.6

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies.

```bash
pip install pygame playsound
git clone https://github.com/Nopparuj-an/FRA163-Project-Simulation.git
cd .\FRA163-Project-Simulation
python3 main.py
```

## Usage

#### Enter the values by left clicking on one of the text boxes, when it is blue the box is highlighted and you can type in the value. Once you finish typing, click anywhere to leave.

| Value Name | Info |
| ------------ | ------------ |
| Spring Retraction  | Spring Retraction, in meters.  |
|  X Offset | The horizontal distance of the ball behind the starting point.  |
| Y Offset  | The vertical distance of the ball from the ground.  |
|  X Distance | The horizontal distance of the goal from the starting point.  |
| Y Distance | The vertical distance of the goal from the ground.  |


#### Additionally, you can right click a text box to select it and clear its value.

![Text box is highlighted](https://github.com/Nopparuj-an/FRA163-Project-Simulation/blob/main/images/textbox.png?raw=true)

#### Click on the Start button, the program will plot a graph of the ball's trajectory. Additional data such as maximum height, distance and whether the ball hit the goal are also shown.
#### The graph is scaled based on the horizontal distance between the ball and the goal.

![Data shown on the screen](https://github.com/Nopparuj-an/FRA163-Project-Simulation/blob/main/images/start.png?raw=true)

#### You can click on any of the ball trajectory and the program will show the ball's position in (X,Y) coordinates.

![coordinates](https://github.com/Nopparuj-an/FRA163-Project-Simulation/blob/main/images/coords.png?raw=true)

#### Leave the spring retraction text box empty and the program will automatically solve for it.

![Spring Retraction empty](https://github.com/Nopparuj-an/FRA163-Project-Simulation/blob/main/images/solver1.png?raw=true)

![The program successfully solved](https://github.com/Nopparuj-an/FRA163-Project-Simulation/blob/main/images/solver2.png?raw=true)

#### Click on the Reset button and the program will clear the graph and reset all values to the default.

![Reset](https://github.com/Nopparuj-an/FRA163-Project-Simulation/blob/main/images/reset.png?raw=true)

#### The About button shows the team behind this project.

![About menu](https://github.com/Nopparuj-an/FRA163-Project-Simulation/blob/main/images/about.png?raw=true)

#### The Save button will save the graph and values into a PNG file, along with the backend value such as the spring constant, the shooting angle and the gantry mass.
The file is saved in the Exports folder, with the current date and time as its name. It is then automatically opened in the respective program for the user to share.

![Output PNG](https://github.com/Nopparuj-an/FRA163-Project-Simulation/blob/main/images/output.png?raw=true)

#### The program can detect errors and warn the user about it.

![Error](https://github.com/Nopparuj-an/FRA163-Project-Simulation/blob/main/images/error1.png?raw=true)

![Error](https://github.com/Nopparuj-an/FRA163-Project-Simulation/blob/main/images/error2.png?raw=true)

![Error](https://github.com/Nopparuj-an/FRA163-Project-Simulation/blob/main/images/error3.png?raw=true)

![Error](https://github.com/Nopparuj-an/FRA163-Project-Simulation/blob/main/images/error4.png?raw=true)

![Error](https://github.com/Nopparuj-an/FRA163-Project-Simulation/blob/main/images/error5.png?raw=true)
