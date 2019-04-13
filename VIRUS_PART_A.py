# COMPSCI 130, Semester 012019
# Project Two - Virus


import turtle
import random


class Virus:
    """Used to infect."""

    def __init__(self, colour=(1, 0, 0), duration=7):
        self.colour = colour
        self.duration = duration

    def progress(self):
        self.duration -= 1
        self.colour = tuple([val*0.9 for val in self.colour])


class Person:
    """This class represents a person."""

    def __init__(self, world_size):
        self.world_size = world_size
        self.radius = 7
        self.location = self._get_random_location()
        self.destination = self._get_random_location()
        self.virus = None

    def _get_random_location(self):
        """Returns a random (x, y) position within this person's world size.

        The returned position will not be within 1 radius of the edge of this
        person'sworld.
        """

        # Adjust coordinates to start from the top-left corner of the world
        width, height = self.world_size
        x = 0 - (width // 2)
        y = height // 2

        # Generate a random (x, y) coordinate within the world's borders
        x += random.uniform(self.radius + 1, width - self.radius)
        y -= random.uniform(self.radius + 1, height - self.radius)

        return x, y

    def draw(self):
        """Draws this person as a coloured dot at their current location.

        The person will be drawn in their virus' colour if they are infected, 
        otherwise they will be drawn in black.
        """

        turtle.penup()  # Ensure nothing is drawn while moving

        person_colour = (0, 0, 0)  # Black
        if self.isInfected():
            person_colour = self.virus.colour

        turtle.color(person_colour)
        turtle.setpos(self.location)
        turtle.dot(self.radius * 2)

    def collides(self, other):
        """Returns true if the distance between this person and the other person is
        less than this + the other person's radius, otherwise returns False.
        """
        if other is self:
            return False

        turtle.penup()  # Ensure nothing is drawn while moving
        turtle.setpos(self.location)
        return turtle.distance(other.location) <= (self.radius + other.radius)

    def collision_list(self, list_of_others):
        """Returns a list of people from the given list who are in contact
        with this person.
        """
        return [person for person in list_of_others if self.collides(person)]

    def infect(self, virus):
        """Infects this person with the given virus"""
        self.virus = virus

    def reached_destination(self):
        """Returns true if location is within 1 radius of destination,
        otherwise returns False.
        """
        turtle.penup()  # Ensure nothing is drawn while moving
        turtle.setpos(self.location)
        return turtle.distance(self.destination) <= self.radius

    def progress_illness(self):
        """Progress this person's virus, curing them if it's duration is 0."""
        self.virus.progress()
        if self.virus.duration == 0:
            self.cured()

    def update(self):
        """Updates this person each hour.

        - Moves this person towards their destination
        - If the destination is reached then a new destination is set
        - Progresses any illness
        """
        self.move()
        if self.reached_destination():
            self.destination = self._get_random_location()
        if self.isInfected():
            self.progress_illness()

    def move(self):
        """Moves this person radius / 2 towards their destination."""
        turtle.penup()  # Ensure nothing is drawn while moving
        turtle.setpos(self.location)
        turtle.setheading(turtle.towards(self.destination))
        turtle.forward(self.radius/2)
        self.location = turtle.pos()

    def cured(self):
        """Removes this person's virus."""
        self.virus = None

    def isInfected(self):
        """Returns True if this person is infected, else False."""
        return self.virus is not None


class World:
    """This class represents a simulated world."""

    def __init__(self, width, height, n):
        self.size = (width, height)
        self.hours = 0
        self.people = []
        for i in range(n):
            self.add_person()

    def add_person(self):
        """Adds a new person to this world."""
        self.people.append(Person(self.size))

    def infect_person(self):
        """Infects a random person in this world with a virus.

        It is possible for the chosen person to already be infected
        with a virus.
        """

        rand_person = random.choice(self.people)
        rand_person.infect(Virus())

    def cure_all(self):
        """Cures all people in this world."""
        for person in self.people:
            person.cured()

    def update_infections_slow(self):
        """Infect anyone in contact with an infected person."""
        infected = (person for person in self.people if person.isInfected())
        to_infect = set()

        for person in infected:
            to_infect.update(person.collision_list(self.people))

        for person in to_infect:
            person.infect(Virus())

    # Part D make the collision detection faster
    def update_infections_fast(self):
        pass

    def simulate(self):
        """Simulates one hour in this world.
        - Updates all people
        - Updates all infection transmissions
        """
        self.hours += 1
        for person in self.people:
            person.update()
        self.update_infections_slow()

    def draw(self):
        """Draws this world.

        - Clears the current screen
        - Draws all the people in this world
        - Draw the box that frames this world
        - Writes the number of hours and number of people infected at the top
        of the frame
        """

        # Top-left corner of the world
        width, height = self.size
        x = 0 - width // 2
        y = height // 2

        turtle.clear()
        for person in self.people:
            person.draw()
        self.draw_rect(x, y, width, height)
        self.draw_text(x, y, f'Hours: {self.hours}')
        self.draw_text(0, y, f'Infected: {self.count_infected()}',
                       align='center')

    def draw_text(self, x, y, text, align='left'):
        """Writes the given text on the screen."""
        turtle.penup()  # Ensure nothing is drawn while moving
        turtle.color('black')
        turtle.setpos(x, y)
        turtle.write(text, align=align)

    def draw_rect(self, x, y, width, height):
        """Draws a rectangle starting from the top-left corner."""

        # Draw the top-left corner of the rectangle
        self.draw_line(x, y, width, orientation="horizontal")
        self.draw_line(x, y, height)

        # Draw the bottom-right corner of the rectangle
        x += width
        y -= height
        self.draw_line(x, y, width, orientation="horizontal", reverse=True)
        self.draw_line(x, y, height, reverse=True)

    def draw_line(self, x, y, length, orientation="vertical", reverse=False):
        """Draws a line starting from the top/left."""
        if orientation == "vertical":
            turtle.setheading(180)  # South
        elif orientation == "horizontal":
            turtle.setheading(90)  # East

        if reverse:
            length *= -1

        turtle.color('black')
        turtle.penup()  # Ensure nothing is drawn while moving
        turtle.setpos(x, y)
        turtle.pendown()
        turtle.forward(length)
        turtle.penup()

    def count_infected(self):
        """Returns the number of infected people in this world."""
        return sum(True for person in self.people if person.isInfected())

# ---------------------------------------------------------
# Should not need to alter any of the code below this line
# ---------------------------------------------------------


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
        self.MARGIN = 50  # gap around each side
        self.PEOPLE = 200  # number of people in the simulation
        self.framework = AnimationFramework(
            self.WIDTH, self.HEIGHT, self.TITLE)

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
        self.world = World(
            self.WIDTH - self.MARGIN * 2,
            self.HEIGHT - self.MARGIN * 2,
            self.PEOPLE)
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
        # self.framework.stop_simulation()  # To advance one hour at a time


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
        self.tick = None  # function to call for each animation cycle
        self.delay = 1  # smallest delay is 1 millisecond
        turtle.title(title)  # title for the window
        turtle.setup(width, height)  # set window display
        turtle.hideturtle()  # prevent turtle appearance
        turtle.tracer(0, 0)  # prevent turtle animation
        turtle.listen()  # set window focus to the turtle window
        turtle.mode('logo')  # set 0 direction as straight up
        turtle.penup()  # don't draw anything
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
turtle.mainloop()  # Need this at the end to ensure events handled properly