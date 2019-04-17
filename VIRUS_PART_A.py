# COMPSCI 130, Semester 012019
# Project Two - Virus

# Author: Feras Albaroudi
# UPI: falb418
# ID: 606316306


import turtle
import random
from math import ceil
from collections import OrderedDict


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
    """Base class for all viruses used to infect people.

    This class implements a __hash__ and __eq__ method designed to help
    prevent a person from being infected by the same virus twice when stored
    in a set (all instances are considered equal).
    """

    def __init__(self, colour=(1, 0, 0), duration=7):
        """Creates a virus with the given colour and duration."""
        self.colour = colour
        self.duration = duration
        self.remaining_duration = duration

    def __hash__(self):
        """Returns a hash representing this class."""
        return hash(self.__class__.__name__)

    def __eq__(self, other):
        """Returns True when equating two instances of this class, otherwise
        returns False."""
        return isinstance(other, self.__class__)

    def __repr__(self):
        """Returns a string of this virus' name, id and remaining duration.

        Primarily for debugging.
        """
        return (f'<{self.__class__.__name__} '
                f'@ {id(self)} dur: '
                f'{self.remaining_duration}/{self.duration}'
                )

    def progress(self):
        """Reduces the remaining_duration of this virus."""
        self.remaining_duration -= 1

    def infect(self, person):
        """Infects the given person with a new instance of this virus."""
        person.infect(self.__class__())

    def reset_duration(self):
        """Sets the duration of this virus to it's initial value."""
        self.remaining_duration = self.duration

    def isCured(self):
        """Returns True if this virus has run out, otherwise returns False.'"""
        return self.remaining_duration == 0

    def cure(self, person):
        """Removes this virus from the given person."""
        person.viruses.discard(self)

    # @classmethod
    # def on_world_update(cls, world):
    #     """If defined, this classmethod will automatically be called at the
    #     end of every world update/simulation (i.e. every hour) and is passed
    #     the current world state.
    #     """
    #     pass


class RainbowVirus(Virus):
    """This virus infects people with a synchronised animation through the
    colours of a rainbow.
    """

    # Colour values for red, orange, yellow, green, blue, purple, violet
    colours = [(1, 0, 0), (1, 127/255, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1),
               (75/255, 0, 130/255), (148/255, 0, 211/255)]
    colours = ColourGradient.linear_sequence(colours, 20)
    colours += colours[1:-1][::-1]  # Smooth the transition from violet to red
    colour_count = len(colours)
    colour_index = 0

    def __init__(self, duration=14):
        """Creates a new RainbowVirus with the given duration."""
        self.duration = duration
        self.remaining_duration = duration

    @classmethod
    def on_world_update(cls, world):
        """Moves onto the next colour in the rainbow, starting again from the
        beginning once all the colours have been cycled through.
        """
        cls.colour_index = (cls.colour_index + 1) % cls.colour_count

    @property
    def colour(self):
        """Returns the current colour of the rainbow!

        This attribute is decorated so that it can be accessed in the same way
        as all other viruses.
        """
        return RainbowVirus.colours[RainbowVirus.colour_index]

    @colour.setter
    def colour(self, value):
        """Raises an AttributeError as instances of this virus cannot have
        their colour changed.
        """
        raise AttributeError("can't set the colour of RainbowVirus instances")


class ZebraVirus(Virus):
    """People infected with this virus individually alternate between black
    and white.
    """

    colours = [(0, 0, 0), (1, 1, 1)]  # Black and white
    colour_index = 0

    def __init__(self, duration=21):
        """Creates a new ZebraVirus with the given duration."""
        self.duration = duration
        self.remaining_duration = duration
        self.colour_index = ZebraVirus.colour_index

    @classmethod
    def on_world_update(cls, world):
        """Moves onto the next colour, starting again from the beginning once
        all the colours have been cycled through.
        """
        cls.colour_index = (cls.colour_index + 1) % 2

    @property
    def colour(self):
        """Returns the current colour.

        This attribute is decorated so that it can be accessed in the same way
        as all other viruses.
        """
        return ZebraVirus.colours[self.colour_index == ZebraVirus.colour_index]

    @colour.setter
    def colour(self, value):
        """Raises an AttributeError as instances of this virus cannot have
        their colour changed.
        """
        raise AttributeError("can't set the colour of ZebraVirus instances")


class ImmunisableVirus(Virus):
    """People who are cured of this virus cannot be infected by it again."""

    immune = set()

    def __init__(self, immune_colour=(0, 1, 0), infected_colour=(1, 0, 0),
                 duration=28): 
        """Creates a new ImmunisableVirus with the given attributes."""
        super().__init__(infected_colour, duration)
        self.immune_colour = immune_colour

    def infect(self, person):
        """Infects the given person with a new instance of this virus."""
        if person not in ImmunisableVirus.immune:
            person.infect(ImmunisableVirus())

    def cure(self, person):
        """Removes this virus from the given person, makes them immune to this
        virus and changes their colour to indicate.
        """
        person.viruses.discard(self)
        person.colour = self.immune_colour
        ImmunisableVirus.immune.add(person)


class ZombieVirus(Virus):
    """People infected by this virus will chase after people who aren't
    infected.
    """

    infected = {}  # Stores (person, virus) pairs
    healthy = []
    is_running = True

    def __init__(self, idle_colour=(0.5, 0, 0), chase_colour=(1, 0, 0),
                 duration=-1):
        """Creates a new ZombieVirus with the given attributes."""
        self.idle_colour = idle_colour
        self.chase_colour = chase_colour
        self.duration = duration
        self.remaining_duration = duration
        self.target = None

    @classmethod
    def on_world_update(cls, world):
        """Updates the list of healthy people for this class used to help
        locate targets for people infected by this virus, and assigns targets
        for people infected by this virus.
        """
        cls.healthy = [p for p in world.people if not p.is_infected()]

        # If everyone is infected then there's nothing left to target, so we:
        # - Clear all targets
        # - Give out new (random) destinations to prevent everyone from
        #   converging on the position of the last healthy person
        # - Prevent the rest of this method from executing until there
        #   are healthy people to target
        if not cls.healthy and cls.is_running:
            for person, virus in cls.infected.items():
                person.destination = person._get_random_location()
                virus.target = None
            cls.is_running = False
            return

        # If healthy people appear while this virus has stopped then this
        # virus can start up again and try to infect them
        elif cls.healthy and not cls.is_running:
            cls.is_running = True

        # There's nothing left to infect
        elif not cls.is_running:
            return

        # Assign targets and destinations to each infected person
        for person, virus in cls.infected.items():
            if virus.target is None or virus.target.is_infected():
                virus.target = random.choice(cls.healthy)
            person.destination = virus.target.location

    @property
    def colour(self):
        """Returns idle_colour if this virus isn't chasing anyone, otherwise
        returns chase_colour.
        """
        if self.target is None:
            return self.idle_colour
        return self.chase_colour

    @colour.setter
    def colour(self, value_dict):
        """Given a dict with keys idle_colour and chase_colour, assigns their
        values to this instances corresponding colours.
        """
        self.idle_colour = value_dict['idle_colour']
        self.chase_colour = value_dict['chase_colour']

    def infect(self, person):
        """Infects the given person with a new instance of this virus and adds
        them to ZombieVirus' list of infected people if they don't already have
        this virus.
        """
        if not person.has_virus(self):
            instance = self.__class__()
            person.infect(instance)
            ZombieVirus.infected[person] = instance

    def cure(self, person):
        """Removes this virus from the given person and removes them from this
        ZombieVirus' list of infected people.
        """
        person.viruses.discard(self)
        del ZombieVirus.infected[person]


class SnakeVirus(Virus):
    """This virus forms a snake with those infected by it that chases after
    people who aren't infected.
    """

    head_colour = (1, 0, 0)
    body_colour = (0, 0, 1)

    infected = OrderedDict()

    def __init__(self, duration=-1):
        self.duration = duration
        self.remaining_duration = duration
        self.target = None

    @classmethod
    def on_world_update(cls, world):
        """Updates the list of infected people used by this class to
        tell it's people where to go.
        """
        cls.healthy = [p for p in world.people if not p.is_infected()]

        people = list(cls.infected.keys())
        for i, person in enumerate(people):

            if i != 0:
                # Follow the person before them
                person.destination = people[i-1].location

            else:
                # Go after someone who isn't infected (if there are any
                # remaining)
                if not len(cls.healthy):
                    continue

                virus = cls.infected[person]
                if virus.target is None or virus.target.is_infected():
                    virus.target = random.choice(cls.healthy)
                person.destination = virus.target.location

    @property
    def colour(self):
        """Returns head_colour if this virus is the 'head' of the snake,
        otherwise returns body_colour.
        """

        # Get the first virus in SnakeVirus.infected
        for first in SnakeVirus.infected.values():
            if self is first:
                return self.head_colour
            return self.body_colour

    @colour.setter
    def colour(self, value_dict):
        """Given a dict with keys head_colour and body_colour, assigns their
        values to this instances corresponding colours.
        """
        SnakeVirus.head_colour = value_dict['head_colour']
        SnakeVirus.body_colour = value_dict['body_colour']

    def infect(self, person):
        """Infects the given person with a new instance of this virus and adds
        them to SnakeVirus' list of infected people if they don't already have
        this virus.
        """
        if not person.has_virus(self):
            instance = self.__class__()
            person.infect(instance)
            SnakeVirus.infected[person] = instance

    def cure(self, person):
        """Removes this virus from the given person and removes them from this
        SnakeVirus' list of infected people.
        """
        person.viruses.discard(self)
        del SnakeVirus.infected[person]


class Person:
    """This class represents a person."""

    def __init__(self, world_size, colour=(0, 0, 0)):
        """Creates a new person at a random location who will randomly roam
        within the given world size."""
        self.world_size = world_size
        self.radius = 7
        self.location = self._get_random_location()
        self.destination = self._get_random_location()
        self.viruses = set()
        self.colour = colour  # Defaults to black

    def _get_random_location(self):
        """Returns a random (x, y) position within this person's world size.

        The returned position will not be within 1 radius of the edge of this
        person's world.
        """

        # Adjust coordinates to start from the top-left corner of the world
        width, height = self.world_size
        x = 0 - (width // 2)
        y = height // 2

        # Generate a random (x, y) coordinate within the world's borders
        x += random.uniform(self.radius + 1, width - self.radius)
        y -= random.uniform(self.radius + 1, height - self.radius)

        return x, y

    def get_colour(self):
        """Returns the average of this person's viruses colours if they are
        infected, otherwise returns their default colour.
        """
        colour = self.colour

        # Calculate the average colour of this person's virus(es)
        if self.is_infected():
            n = len(self.viruses)
            colours = [virus.colour for virus in self.viruses]
            colour = (sum(channel)/n for channel in zip(*colours))

        return colour

    def draw(self):
        """Draws this person as a coloured dot at their current location."""

        turtle.penup()  # Ensure nothing is drawn while moving

        turtle.setpos(self.location)
        turtle.dot(self.radius * 2, self.get_colour())

    def collides(self, other):
        """Returns true if the distance between this person and the other
        person is less than this + the other person's radius, otherwise returns
        False.
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
        """Infects this person with the given virus if they aren't already
        infected by it, else refreshes the virus' duration on this person.
        """

        # Try and get the instance of the given virus on this person (if any),
        # otherwise add a new instance of the given virus to this person
        try:
            instance = (self.viruses - (self.viruses - set([virus]))).pop()
            instance.reset_duration()
        except:
            self.viruses.add(virus)

    def reached_destination(self):
        """Returns True if location is within 1 radius of destination,
        otherwise returns False.
        """
        return distance_2d(self.location, self.destination) <= self.radius

    def progress_illness(self):
        """Progress this person's virus, curing them if it's run out."""
        for virus in self.viruses.copy():
            virus.progress()
            if virus.isCured():
                self.cure(virus)

    def update(self):
        """Updates this person each hour.

        - Moves this person towards their destination
        - If the destination is reached then a new destination is set
        - Progresses any illness
        """
        self.move()
        if self.reached_destination():
            self.destination = self._get_random_location()
        self.progress_illness()

    def move(self):
        """Moves this person radius / 2 towards their destination."""
        turtle.penup()  # Ensure nothing is drawn while moving
        turtle.setpos(self.location)
        turtle.setheading(turtle.towards(self.destination))
        turtle.forward(self.radius/2)
        self.location = turtle.pos()

    def cure(self, virus=None):
        """Removes the given virus from this person, otherwise removes all
        viruses on this person.
        """
        if virus is None:
            for v in self.viruses.copy():
                v.cure(self)
        else:
            virus.cure(self)

    def is_infected(self):
        """Returns True if this person is infected, else False."""
        return bool(len(self.viruses))

    def has_virus(self, virus):
        """Returns True if this person has the given virus, else False."""
        # Returns True if we can find an instance of this virus on this person,
        # otherwise return False
        try:
            return bool((self.viruses - (self.viruses - set([virus]))).pop())
        except:
            return False


class World:
    """This class represents a simulated world."""

    def __init__(self, width, height, n,
                 viruses=[
                     RainbowVirus,
                     ZebraVirus,
                     ImmunisableVirus,
                     ZombieVirus,
                     SnakeVirus
                     ]
                 ):
        """Creates a new world centered on (0, 0) containing n people which
        simulates the spread of the given virus(es) through this world.
        """
        self.size = (width, height)
        self.hours = 0
        self.people = []
        self.viruses = viruses
        self.collision_table = EfficientCollision(28)
        for _ in range(n):
            self.add_person()

        # Add the on_world_update method for each virus if they have one
        self.on_update_methods = []
        for cls in self.viruses:
            if hasattr(cls, "on_world_update"):
                self.on_update_methods.append(getattr(cls, "on_world_update"))

    def add_person(self):
        """Adds a new person to this world."""
        self.people.append(Person(self.size))

    def infect_person(self):
        """Infects a random person in this world with a random virus.

        It is possible for the chosen person to already be infected
        with a virus.
        """

        # If this world has no viruses there's nothing to infect people with
        if not len(self.viruses):
            return

        rand_person = random.choice(self.people)
        rand_virus = random.choice(self.viruses)()
        rand_virus.infect(rand_person)

    def cure_all(self):
        """Cures all people in this world."""
        for person in self.people:
            person.cure()

    def update_infections_slow(self):
        """Infect anyone in contact with an infected person."""

        # Stores (key, value) pairs of the form (person, viruses), where:
        # person = a person object who has collided with an infected person
        # viruses = a set of the virus(es) to infect this person with
        to_infect = {}

        # Loop through each infected person
        for infected in (p for p in self.people if p.is_infected()):
            viruses = [v.__class__ for v in infected.viruses]

            # Add anyone who collided with this infected person to our dict of
            # people to infect along with the viruses to infect them with
            for person in infected.collision_list(self.people):
                if person in to_infect:
                    to_infect[person].update(viruses)
                else:
                    to_infect[person] = set(viruses)

        # Infect anyone who collided with an infected person with the virus(es)
        # of the people they collided with
        for person, viruses in to_infect.items():
            for virus in viruses:
                virus().infect(person)

    def update_infections_fast(self):
        """Infect anyone in contact with an infected person. Uses a spatial
        hash table to speed up collision detection.
        """
        self.collision_table.update(self.people)

        # Stores (key, value) pairs of the form (person, viruses), where:
        # person = a person object who has collided with an infected person
        # viruses = a set of the virus(es) to infect this person with
        to_infect = {}

        # Loop through each infected person
        for infected in (p for p in self.people if p.is_infected()):
            viruses = [v.__class__ for v in infected.viruses]
            cell = tuple(self.collision_table.hash(infected.location))
            nearby_people = self.collision_table.cells[cell]

            # Add anyone who collided with this infected person to our dict of
            # people to infect along with the viruses to infect them with
            for person in infected.collision_list(nearby_people):
                if person in to_infect:
                    to_infect[person].update(viruses)
                else:
                    to_infect[person] = set(viruses)

        # Infect anyone who collided with an infected person with the virus(es)
        # of the people they collided with
        for person, viruses in to_infect.items():
            for virus in viruses:
                virus().infect(person)

    def simulate(self):
        """Simulates one hour in this world.
        - Updates all people
        - Updates all infection transmissions
        - Calls any update method(s) from this world's virus(es)
        """
        self.hours += 1
        for person in self.people:
            person.update()
        self.update_infections_fast()
        for method in self.on_update_methods:
            method(self)

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
        return sum(True for person in self.people if person.is_infected())


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
