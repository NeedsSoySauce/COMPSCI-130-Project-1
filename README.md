![image](https://user-images.githubusercontent.com/30617834/67611212-82336d00-f7f4-11e9-9d87-1b1150405b73.png)

# Virus Simulator

This is a simple Python application that simulates the spread of a virus within a population.

## Features

Beyond the given specifications for this assignment, a few things were added:

* A spatial hash table to improve the performance of collision detection
* A static class to generate color gradients between a given start and end color
* A base Virus class which can be subclassed to create viruses compatible with this application, and which was used to add the following:
    * RainbowVirus, a virus which infects people with a synchronised animation through the colours of a rainbow
    * ZebraVirus, people infected with this virus individually alternate between black and white
    * ImmunisableVirus, people who are cured of this virus cannot be infected by it again
    * ZombieVirus, people infected by this virus will chase after people who aren't infected by any virus
    * SnakeVirus, a virus which forms a snake with those infected by it that chases after people who aren't infected by any virus
