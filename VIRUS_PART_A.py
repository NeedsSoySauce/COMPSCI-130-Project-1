# COMPSCI 130, Semester 012019
# Project Two - Virus
# Author: Feras Albaroudi
# UPI: falb418
# ID: 606316306


import turtle
import random
from math import ceil


class EfficientCollision:
    """Used to create a spatial hash table to perform collision detection."""

    def __init__(self, cell_size):
        """Initializes an empty spatial hash table with square cells using
        cell_size as their side length.
        """
        self.cell_size = cell_size
        self.cells = {}

    def hash(self, location):
        """Returns the cell location which contains the given location."""
        return [int(coord/self.cell_size) for coord in location]

    def get_bounding_box(self, person):
        """Returns the axis-aligned bounding box for the given person
        represented by the min and max coordinates along each plane.
        """
        x, y = person.location
        radius = person.radius

        xmin, xmax = int(x-radius), int(ceil(x+radius))
        ymin, ymax = int(y-radius), int(ceil(y+radius))

        return xmin, ymin, xmax, ymax

    def add(self, person):
        """Adds the given person to all cells within their radius."""
        xmin, ymin, xmax, ymax = self.hash(self.get_bounding_box(person))

        # Add this person to all cells within their axis-aligned bounding box
        for x in range(xmin, xmax+1):
            for y in range(ymin, ymax+1):
                if (x, y) in self.cells:
                    self.cells[(x, y)].append(person)
                else:
                    self.cells[(x, y)] = [person]

    def update(self, people):
        """Updates the collision table using the given people."""
        self.cells = {}
        for person in people:
            self.add(person)


class ColourGradient:
    """Used to contain functions related to generating a gradient between two
    or more colours."""

    @staticmethod
    def linear_sequence(colours, n):
        """Returns a list representing a linear colour gradient with n
        interpolated colours inbetween each colour in the given colours.
        """
        if len(colours) < 2:
            raise ValueError("Cannot create a gradient with < 2 colours.")

        gradient = [colours[0]]
        for colour in colours[1:]:
            gradient += ColourGradient.linear(gradient[-1], colour, n)

        return gradient

    @staticmethod
    def linear(start, end, n):
        """Returns a list representing a linear colour gradient with n
        interpolated colours inbetween the given start to end colours.
        """
        gradient = [start]

        # 1. Get the change between each colour channel from end to start
        # 2. Divide each change by n + 1 so that we can add it to each
        #    subsequent interpolated colour until we fall one addition short
        #    of the end colour (which we already have)
        step = [(e-s)/(n+1) for s, e in zip(start, end)]

        # 3. Repeatedly add our step to the start colour to get each subsequent
        #    interpolated colour
        interpolated = start[:]
        for _ in range(n):
            interpolated = [i+s for i, s in zip(interpolated, step)]
            gradient.append(interpolated)

        return gradient + [end]


class Virus:
    """A basic virus used to infect people."""

    def __init__(self, colour=(1, 0, 0), duration=7):
        """Creates a virus with the given colour and duration."""
        self.colour = colour
        self.duration = duration
        self.remaining_duration = duration

    def progress(self):
        """Reduces the remaining_duration of this virus."""
        self.remaining_duration -= 1

    def infect(self, person):
        """Infects the given person with a new instance of this virus."""
        person.infect(Virus())

    def resetDuration(self):
        """Sets the duration of this virus to it's initial value."""
        self.remaining_duration = self.duration

    def isCured(self):
        """Returns True if this virus has run out, otherwise returns False.'"""
        return self.remaining_duration == 0


class RainbowVirus(Virus):
    """This virus infects people using the colours of the rainbow."""

    # Colour values for red, orange, yellow, green, blue, purple, violet
    colours = [(1, 0, 0), (1, 127/255, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1),
               (75/255, 0, 130/255), (148/255, 0, 211/255)]
    colours = ColourGradient.linear_sequence(colours, 50)
    colours += colours[1:-1][::-1]  # Smooth the transition from violet to red
    colour_count = len(colours)
    colour_index = 0

    def __init__(self, duration=14):
        """Creates a new RainbowVirus using the current rainbow colour."""
        self.duration = duration
        self.remaining_duration = duration

    @property
    def colour(self):
        """Returns the current colour of the rainbow!"""
        return RainbowVirus.colours[RainbowVirus.colour_index]

    @classmethod
    def next_colour(cls):
        """Moves onto the next colour in the rainbow, starting again from the
        beginning once all the colours have been cycled through.
        """
        cls.colour_index = (cls.colour_index + 1) % cls.colour_count

    @classmethod
    def test(cls):
        """Moves onto the next colour in the rainbow, starting again from the
        beginning once all the colours have been cycled through.
        """
        cls.colour_index = (cls.colour_index + 1) % cls.colour_count

    def infect(self, person):
        """Infects the given person with a new instance of this virus if they
        haven't been infected by it yet, otherwise resets their virus' duration
        """
        if isinstance(person.virus, RainbowVirus):
            person.virus.resetDuration()
        else:
            person.infect(RainbowVirus())


class Person:
    """This class represents a person."""

    def __init__(self, world_size):
        """Creates a new person at a random location who will randomly roam
        within the given world size."""
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

        turtle.setpos(self.location)
        turtle.dot(self.radius * 2, person_colour)

    def collides(self, other):
        """Returns true if the distance between this person and the other person is
        less than this + the other person's radius, otherwise returns False.
        """
        if other is self:
            return False

        return distance_2d(self.location, other.location) <= \
            (self.radius + other.radius)

    def collision_list(self, list_of_others):
        """Returns a list of people from the given list who are in contact
        with this person.
        """
        return [person for person in list_of_others if self.collides(person)]

    def infect(self, virus):
        """Infects this person with the given virus"""
        self.virus = virus

    def reached_destination(self):
        """Returns True if location is within 1 radius of destination,
        otherwise returns False.
        """
        return distance_2d(self.location, self.destination) <= self.radius

    def progress_illness(self):
        """Progress this person's virus, curing them if it's run out."""
        self.virus.progress()
        if self.virus.isCured():
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
        """Creates a new world centered on (0, 0) containing n people."""
        self.size = (width, height)
        self.hours = 0
        self.people = []
        self.collision_table = EfficientCollision(28)
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
        new_virus = RainbowVirus()
        new_virus.infect(rand_person)

    def cure_all(self):
        """Cures all people in this world."""
        for person in self.people:
            person.cured()

    def update_infections_slow(self):
        """Infect anyone in contact with an infected person."""
        infected = (person for person in self.people if person.isInfected())
        to_infect = set() 

        # Anyone an infected person collides with will be infected
        for person in infected:
            to_infect.update(person.collision_list(self.people))

        # Infect anyone who collided with an infected person
        for person in to_infect:
            new_virus = RainbowVirus()
            new_virus.infect(person)

        # If anyone was infected, change the colour
        if len(to_infect):
            RainbowVirus.next_colour()

    def update_infections_fast(self):
        """Infect anyone in contact with an infected person."""
        self.collision_table.update(self.people)

        infected = (person for person in self.people if person.isInfected())
        to_infect = set()

        # Anyone an infected person collides with will be infected
        for person in infected:
            cell = tuple(self.collision_table.hash(person.location))
            nearby_people = self.collision_table.cells[cell]
            to_infect.update(person.collision_list(nearby_people))

        # Infect anyone who collided with an infected person
        for person in to_infect:
            new_virus = RainbowVirus()
            new_virus.infect(person)

        # If anyone was infected, change the colour
        if len(to_infect):
            RainbowVirus.next_colour()

    def simulate(self):
        """Simulates one hour in this world.
        - Updates all people
        - Updates all infection transmissions
        """
        self.hours += 1
        for person in self.people:
            person.update()
        self.update_infections_fast()

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
        draw_rect(x, y, width, height)
        draw_text(x, y, f'Hours: {self.hours}')
        draw_text(0, y, f'Infected: {self.count_infected()}', align='center')

    def count_infected(self):
        """Returns the number of infected people in this world."""
        return sum(True for person in self.people if person.isInfected())


def draw_text(x, y, text, align='left', colour='black'):
    """Writes the given text on the screen."""
    turtle.penup()  # Ensure nothing is drawn while moving
    turtle.color(colour)
    turtle.setpos(x, y)
    turtle.write(text, align=align)


def draw_rect(x, y, width, height):
    """Draws a rectangle starting from the top-left corner."""

    # Draw the top-left corner of the rectangle
    draw_line(x, y, width, orientation="horizontal")
    draw_line(x, y, height)

    # Draw the bottom-right corner of the rectangle
    x += width
    y -= height
    draw_line(x, y, width, orientation="horizontal", reverse=True)
    draw_line(x, y, height, reverse=True)


def draw_line(x, y, length, orientation="vertical", reverse=False,
              colour='black'):
    """Draws a line starting from the top/left."""
    if orientation == "vertical":
        turtle.setheading(180)  # South
    elif orientation == "horizontal":
        turtle.setheading(90)  # East

    if reverse:
        length *= -1

    turtle.color(colour)
    turtle.penup()  # Ensure nothing is drawn while moving
    turtle.setpos(x, y)
    turtle.pendown()
    turtle.forward(length)
    turtle.penup()


def distance_2d(a, b):
    """Returns the distance between two 2D points of the form (x, y)."""
    # Standard distance formula for two points in the form (x, y)
    return ((b[0] - a[0])**2 + (b[1] - a[1])**2)**0.5


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
