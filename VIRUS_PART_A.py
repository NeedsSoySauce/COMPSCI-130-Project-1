### COMPSCI 130, Semester 012019
### Project Two - Virus
import turtle
import random

#used to infect 
class Virus:
    def __init__(self, colour, duration):
        self.colour = colour
        self.duration = duration
        
## This class represents a person
class Person:
    def __init__(self, world_size):
        self.world_size = world_size
        self.radius = 7
        self.location = (0, 0)
        self.destination = (0,0)
        pass
        
    #random locations are used to assign a destination for the person
    #the possible locations should not be closer than 1 radius to the edge of the world 
    def _get_random_location(self):
        pass
 
    #draw a person using a dot.  Use colour if implementing Viruses 
    def draw(self):
        pass

    #PART C returns true if the distance between self and other is less than the diameter
    def collides(self, other):
        pass

    #PART C given a list of people, return a list containing only
    #those people who are in contact with self
    def collision_list(self, list_of_others):
        pass

    #infect a person with the given virus
    def infect(self, virus):
        pass

    #returns true if within 1 radius
    def reached_destination(self):
        pass

    #increase hours of sickness, check if duration of virus is reached.  If the
    #duration is reached then the person is cured
    def progress_illness(self):
        pass     

    #Updates the person each hour.
    #- moves each person by calling the move method
    #- if the destination is reached then set a new destination
    #- progress any illness
    def update(self):
        pass
        
    #moves person towards the destination
    def move(self):
        pass

    #cures the person of infection   
    def cured(self):
        pass 
      
class World:
    def __init__(self, width, height, n):
        self.size = (width, height)
        self.hours = 0
        self.people = []
    
    #add a person to the list
    def add_person(self):
        pass

    #choose a random person to infect and infect with a Virus
    def infect_person(self):
        pass

    #remove all infections from all people
    def cure_all(self):
        pass

    #Part C check for collisions and pass infection to other people
    def update_infections_slow(self):
        pass
                    
                    
    #Part D make the collision detection faster
    def update_infections_fast(self):
        pass
                    
    #simulate one hour in the world.
    #- increase hours passed.
    #- update all people
    #- update all infection transmissions
    def simulate(self):
        pass

    #Draw the world.  Perform the following tasks:
    #   - clear the current screen
    #   - draw all the people
    #   - draw the box that frames the world
    #   - write the number of hours and number of people infected at the top of the frame
    def draw(self):
        turtle.clear()
        pass
        
    #Count the number of infected people
    def count_infected(self):
        pass
    
#---------------------------------------------------------
#Should not need to alter any of the code below this line
#---------------------------------------------------------
class GraphicalWorld:
    """ Handles the user interface for the simulation

    space - starts and stops the simulation
    'z' - resets the application to the initial state
    'x' - infects a random person
    'c' - cures all the people
    """
    def __init__(self):
        self.WIDTH = 800
        self.HEIGHT = 600
        self.TITLE = 'COMPSCI 130 Project One'
        self.MARGIN = 50 #gap around each side
        self.PEOPLE = 200 #number of people in the simulation
        self.framework = AnimationFramework(self.WIDTH, self.HEIGHT, self.TITLE)
        
        self.framework.add_key_action(self.setup, 'z') 
        self.framework.add_key_action(self.infect, 'x')
        self.framework.add_key_action(self.cure, 'c')
        self.framework.add_key_action(self.toggle_simulation, ' ') 
        self.framework.add_tick_action(self.next_turn)
        
        self.world = None

    def setup(self):
        """ Reset the simulation to the initial state """
        print('resetting the world')        
        self.framework.stop_simulation()
        self.world = World(self.WIDTH - self.MARGIN * 2, self.HEIGHT - self.MARGIN * 2, self.PEOPLE)
        self.world.draw()
        
    def infect(self):
        """ Infect a person, and update the drawing """
        print('infecting a person')
        self.world.infect_person()
        self.world.draw()

    def cure(self):
        """ Remove infections from all the people """
        print('cured all people')
        self.world.cure_all()
        self.world.draw()

    def toggle_simulation(self):
        """ Starts and stops the simulation """
        if self.framework.simulation_is_running():
            self.framework.stop_simulation()
        else:
            self.framework.start_simulation()           

    def next_turn(self):
        """ Perform the tasks needed for the next animation cycle """
        self.world.simulate()
        self.world.draw()
        
## This is the animation framework
## Do not edit this framework
class AnimationFramework:
    """This framework is used to provide support for animation of
       interactive applications using the turtle library.  There is
       no need to edit any of the code in this framework.
    """
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        self.simulation_running = False
        self.tick = None #function to call for each animation cycle
        self.delay = 1 #smallest delay is 1 millisecond      
        turtle.title(title) #title for the window
        turtle.setup(width, height) #set window display
        turtle.hideturtle() #prevent turtle appearance
        turtle.tracer(0, 0) #prevent turtle animation
        turtle.listen() #set window focus to the turtle window
        turtle.mode('logo') #set 0 direction as straight up
        turtle.penup() #don't draw anything
        turtle.setundobuffer(None)
        self.__animation_loop()

    def start_simulation(self):
        self.simulation_running = True
        
    def stop_simulation(self):
        self.simulation_running = False

    def simulation_is_running(self):
        return self.simulation_running
    
    def add_key_action(self, func, key):
        turtle.onkeypress(func, key)

    def add_tick_action(self, func):
        self.tick = func

    def __animation_loop(self):
        try:
            if self.simulation_running:
                self.tick()
            turtle.ontimer(self.__animation_loop, self.delay)
        except turtle.Terminator:
            pass


gw = GraphicalWorld()
gw.setup()
turtle.mainloop() #Need this at the end to ensure events handled properly
