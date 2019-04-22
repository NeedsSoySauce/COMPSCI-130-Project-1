# COMPSCI 130, Semester 012019
# Project Two - Virus

# Author: Feras Albaroudi
# UPI: falb418
# ID: 606316306

import turtle
import random
from math import ceil, copysign
from collections import OrderedDict


class EfficientCollision:
    """Implements a spatial hash table to perform collision detection."""

    def __init__(self, cell_size):
        """Initializes an empty spatial hash table with square cells using
        cell_size as their side length.
        """
        self.cell_size = cell_size
        self.cells = {}

    def hash(self, location):
        """Returns the cell location of each coordinate in the given location.

        Args:
            location (list/tuple): coordinates along each dimensions
        """
        return [int(coord / self.cell_size) for coord in location]

    def get_bounding_box(self, person):
        """Returns the axis-aligned bounding box for the given person
        represented by the min and max coordinates along the x and y axes.
        """
        x, y = person.location
        radius = person.radius

        xmin, xmax = int(x - radius), int(ceil(x + radius))
        ymin, ymax = int(y - radius), int(ceil(y + radius))

        return xmin, ymin, xmax, ymax

    def add(self, person):
        """Adds the given person to all cells within their axis-aligned bounding box.
        """
        xmin, ymin, xmax, ymax = self.hash(self.get_bounding_box(person))

        for x in range(xmin, xmax + 1):
            for y in range(ymin, ymax + 1):
                if (x, y) in self.cells:
                    self.cells[(x, y)].append(person)
                else:
                    self.cells[(x, y)] = [person]

    def update(self, people):
        """Clears the hash table and then adds the given people to it."""
        self.cells.clear()
        for person in people:
            self.add(person)


class ColourGradient:
    """Contains functions related to generating a gradient between two
    or more colours.
    """

    @staticmethod
    def linear_sequence(colours, n):
        """Returns a list representing a linear colour gradient with n
        interpolated colours in between each colour in the given ordered
        list of colours.

        Each colour in colours should should be a list or tuple of colour
        channel values weighted in the same way. e.g. (1.0, 0.0, 0.0) for red

        Raises:
            ValueError: cannot create a gradient with < 2 colours."
        """
        if len(colours) < 2:
            raise ValueError("cannot create a gradient with < 2 colours.")

        gradient = [colours[0]]
        for colour in colours[1:]:
            gradient += ColourGradient.linear(gradient[-1], colour, n)

        return gradient

    @staticmethod
    def linear(start, end, n):
        """Returns a list representing a linear colour gradient with n
        interpolated colours in between the given start to end colours.

        The start and end colours should be a list or tuple of colour channel
        values weighted in the same way. e.g. (1.0, 0.0, 0.0) for red

        """
        gradient = [start]

        # 1. Get the change between each colour channel from end to start
        # 2. Divide each change by n + 1 so that we can add it to each
        #    subsequent interpolated colour until we fall one addition short
        #    of the end colour (which we already have)
        step = [(e - s) / (n + 1) for s, e in zip(start, end)]

        # 3. Repeatedly add our step to the start colour to get each subsequent
        #    interpolated colour
        interpolated = start[:]
        for _ in range(n):
            interpolated = [i + s for i, s in zip(interpolated, step)]
            gradient.append(interpolated)

        return gradient + [end]


class Virus:
    """Base class for all viruses used to infect people."""

    def __init__(self, colour=(1, 0, 0), duration=7):
        """Creates a virus with the given colour and duration.

        Args:
            colour (tuple): RGB colour with each colour channel expressed in
                the range 0.0 and 1.0 (1.0 for most intense)
            duration (int): how long this virus will last in hours
        """
        self.colour = colour
        self.duration = duration
        self.remaining_duration = duration

    # @classmethod
    # def on_world_update(cls, world):
    #     """If defined, this classmethod will automatically be called at the
    #     end of every world update/simulation (i.e. every hour) and is passed
    #     the current world state.
    #     """
    #     pass

    @classmethod
    def reset_class(cls):
        """This method is called when a virus is added to a world and is used
        to ensure it is correctly reset to it's initial state.
        """
        pass

    def __repr__(self):
        """Returns a string of this virus' name, id and remaining duration.

        Primarily for debugging.
        """
        return (f'<{self.__class__.__name__} '
                f'@ {id(self)} dur: '
                f'{self.remaining_duration}/{self.duration}>')

    def progress(self):
        """Reduces the remaining duration of this virus by 1."""
        self.remaining_duration -= 1

    def infect(self, person):
        """Infects the given person with a new instance of this virus."""
        person.infect(self.__class__())

    def reset_duration(self):
        """Sets the remaining duration of this virus to it's initial value."""
        self.remaining_duration = self.duration

    def is_cured(self):
        """Returns True if this virus has run out, otherwise returns False."""
        return self.remaining_duration == 0

    def cure(self, person):
        """Removes this virus from the given person."""
        person.remove_virus(self)


class RainbowVirus(Virus):
    """This virus infects people with a synchronised animation through the
    colours of a rainbow.

    Private attributes:
        colours (tuple): RGB colour values (red, orange, yellow, green, blue,
            indigo, violet, indigo, blue, green, yellow, orange) interpolated n
            times (see interpolations) between each colour
        interpolations (int): number of interpolated colours inserted in
            between each colour in colours
        colour_count (int): length of colours (including interpolated colours)
        colour_index (int): current colour in colours that is being displayed
    """

    __colours = ((1, 0, 0), (1, 127 / 255, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1),
                 (75 / 255, 0, 130 / 255), (148 / 255, 0, 211 / 255))

    # Smooth the transition between colours
    __interpolations = 20
    __colours = ColourGradient.linear_sequence(__colours, __interpolations)
    __colours += __colours[1:-1][::-1]

    __colour_count = len(__colours)
    __colour_index = 0

    def __init__(self, duration=14):
        """Creates a new RainbowVirus with the given duration."""
        self.duration = duration
        self.remaining_duration = duration

    @classmethod
    def on_world_update(cls, world):
        """Moves onto the next colour in the rainbow, starting again from the
        beginning once all the colours have been cycled through.
        """
        cls.__colour_index = (cls.__colour_index + 1) % cls.__colour_count

    @property
    def colour(self):
        """Returns the current colour of the rainbow!

        This attribute is decorated so that it can be accessed in the same way
        as all other viruses.
        """
        return RainbowVirus.__colours[RainbowVirus.__colour_index]

    @colour.setter
    def colour(self, value):
        """Raises an AttributeError as instances of this virus cannot have
        their colour changed.
        """
        raise AttributeError("can't set the colour of RainbowVirus instances")


class ZebraVirus(Virus):
    """People infected with this virus individually alternate between black
    and white.

    Private attributes:
        colours (tuple): RGB colour values for black and white
        colour_index (int): current colour in colours that is being displayed
    """

    __colours = [(0, 0, 0), (1, 1, 1)]
    __colour_index = 0

    def __init__(self, duration=21):
        """Creates a new ZebraVirus with the given duration."""
        self.duration = duration
        self.remaining_duration = duration
        self.__colour_index = ZebraVirus.__colour_index

    @classmethod
    def on_world_update(cls, world):
        """Moves onto the next colour, starting again from the beginning once
        all the colours have been cycled through.
        """
        cls.__colour_index = not cls.__colour_index

    @property
    def colour(self):
        """Returns the current colour.

        This attribute is decorated so that it can be accessed in the same way
        as all other viruses.
        """
        return ZebraVirus.__colours[self.__colour_index ==
                                    ZebraVirus.__colour_index]

    @colour.setter
    def colour(self, value):
        """Raises an AttributeError as instances of this virus cannot have
        their colour changed.
        """
        raise AttributeError("can't set the colour of ZebraVirus instances")


class ImmunisableVirus(Virus):
    """People who are cured of this virus cannot be infected by it again.

    Public attributes:
        immune (set): people in this set cannot be infected by this virus
    """

    immune = set()

    def __init__(self,
                 immune_colour=(0, 1, 0),
                 infected_colour=(1, 0, 0),
                 duration=28):
        """Creates a new ImmunisableVirus with the given attributes.

        Args:
            immune_colour (tuple): RGB colour to set people cured of this virus
                to where each channel is expressed in the range 0.0 to 1.0
            infected_colour (tuple): same as immune_colour, but used for people
                infected by this virus
            duration (int): how long this virus lasts in hours
        """
        super().__init__(infected_colour, duration)
        self.immune_colour = immune_colour

    @classmethod
    def reset_class(cls):
        """Clear's this classes set of immune people."""
        cls.immune.clear()

    def infect(self, person):
        """Infects the given person with a new instance of this virus."""
        if person not in ImmunisableVirus.immune:
            person.infect(ImmunisableVirus())

    def cure(self, person):
        """Removes this virus from the given person, makes them immune to this
        virus and changes their colour to indicate.
        """
        person.remove_virus(self)
        person.colour = self.immune_colour
        ImmunisableVirus.immune.add(person)


class ZombieVirus(Virus):
    """People infected by this virus will chase after people who aren't
    infected by any virus.

    Public attributes:
        idle_colour (tuple): RGB colour of people infected by this virus who
            aren't chasing anyone
        chase_colour (tuple): same as idle_colour, but for people who are
            chasing someone
        infected (dict): stores (person, virus) pairs, where person is a Person
            instance and the key to the corresponding ZombieVirus instance they
            are infected by
        healthy (list): stores Person instances who aren't infected by anything

    Private attributes:
        is_running (bool): determines whether people infected by this virus
            will be assigned new targets to chase. True if there are people in
            healthy, False otherwise
    """

    idle_colour = (0.5, 0, 0)
    chase_colour = (1, 0, 0)
    infected = {}
    healthy = []
    __is_running = True

    def __init__(self, duration=-1):
        """Creates a new ZombieVirus with the given attributes."""
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
        if not cls.healthy and cls.__is_running:
            for person, virus in cls.infected.items():
                person.destination = person._get_random_location()
                virus.target = None
            cls.__is_running = False
            return

        # If healthy people appear while this virus has stopped then this
        # virus can start up again and try to infect them
        elif cls.healthy and not cls.__is_running:
            cls.__is_running = True

        # There's nothing left to infect
        elif not cls.__is_running:
            return

        # Assign targets and destinations to each infected person
        for person, virus in cls.infected.items():
            if virus.target is None or virus.target.is_infected():
                virus.target = random.choice(cls.healthy)
            person.destination = virus.target.location

    @classmethod
    def reset_class(cls):
        """Clears this class' dict of infected people and list of healthy
        people and set's it's running state to True.
        """
        cls.infected.clear()
        cls.healthy.clear()
        cls.__is_running = True

    @property
    def colour(self):
        """Returns idle_colour if this virus isn't chasing anyone, otherwise
        returns chase_colour.
        """
        if self.target is None:
            return ZombieVirus.idle_colour
        return ZombieVirus.chase_colour

    @colour.setter
    def colour(self, value):
        """Raises an AttributeError as instances of this virus cannot have
        their colour changed.
        """
        raise AttributeError("can't set the colour of ZombieVirus instances")

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
        """Removes this virus from the given person and removes them from
        ZombieVirus' list of infected people.
        """
        person.remove_virus(self)
        del ZombieVirus.infected[person]


class SnakeVirus(Virus):
    """This virus forms a snake with those infected by it that chases after
    people who aren't infected by any virus.

    In addition, the snake's head only moves along one axis at a time.

    Public attributes:
        head_colour (tuple): RGB colour of the person at the head of the snake
            formed by this virus
        body_colour (tuple): same as head_colour, but for everyone that isn't
            at the head of the snake formed by this virus
        infected (odict): stores (person, virus) pairs, where person is a
            Person instance and the key to the corresponding SnakeVirus
            instance they are infected by
        target (Person): Person instance which will be chased after by the head
            of the snake formed by this virus until that person is infected.
            If this is None, the snake will find another random target if
            possible, otherwise it will roam around randomly
    """

    head_colour = (1, 0, 0)
    body_colour = (0, 0, 1)
    infected = OrderedDict()
    target = None

    def __init__(self):
        """Creates a new SnakeVirus."""
        self.duration = -1
        self.remaining_duration = -1

    @classmethod
    def on_world_update(cls, world):
        """Updates the list of infected people used by this class to
        tell it's people where to go and issues orders to everyone
        infected by this virus.
        """
        cls.healthy = [p for p in world.people if not p.is_infected()]

        people = list(cls.infected.keys())
        for i, person in enumerate(people):

            if i != 0:
                # Follow the person before them
                person.destination = people[i - 1].location
                continue

            # Assign a new target if needed, otherwise, if there are no more
            # healthy people to target, just wander around randomly
            if cls.healthy:
                if (cls.target is None or cls.target.is_infected()):
                    cls.target = random.choice(cls.healthy)
                vector = cls.get_destination_vector(person.location,
                                                    cls.target.location)
            else:
                vector = cls.get_destination_vector(person.location,
                                                    person.destination)

            vector = list(vector)

            # Keep only the component which has the greatest magnitude
            if abs(vector[0]) > abs(vector[1]):
                vector[1] = 0
            else:
                vector[0] = 0

            # Construct the vector for the next snake head destination
            destination = []
            for pos, component in zip(person.location, vector):
                destination.append(pos + component)

            person.destination = tuple(destination)

    @classmethod
    def reset_class(cls):
        """Clears this class' target and list of infected people."""
        cls.infected.clear()
        cls.target = None

    @staticmethod
    def get_destination_vector(origin, destination):
        """Returns a tuple representing a vector from the given origin to the
        given destination.
        """
        vector = []

        for v1, v2 in zip(origin, destination):
            if (v1 * v2) > 0:  # If v1 and v2 have the same sign
                new_val = abs(abs(v1) - abs(v2))
            else:
                new_val = abs(v1) + abs(v2)
            if v1 > v2:
                new_val *= -1
            vector.append(new_val)

        return tuple(vector)

    @property
    def colour(self):
        """Returns head_colour if this virus is at the 'head' of the snake,
        otherwise returns body_colour.
        """

        # Get the first virus in SnakeVirus.infected
        for first in SnakeVirus.infected.values():
            if self is first:
                return self.head_colour
            return self.body_colour

    @colour.setter
    def colour(self, value):
        """Raises an AttributeError as instances of this virus cannot have
        their colour changed.
        """
        raise AttributeError("can't set the colour of SnakeVirus instances")

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
        """Removes this virus from the given person and removes them from
        SnakeVirus' list of infected people.
        """
        person.remove_virus(self)
        del SnakeVirus.infected[person]


class Person:
    """This class represents a person which randomly roams around and can be
    infected by viruses.

    A person can be infected by multiple viruses at once, but they cannot be
    infected by more than one instance of the same type of virus at the same
    time.
    """

    def __init__(self, world_size, radius=7, colour=(0, 0, 0)):
        """Creates a new person at a random location who will randomly roam
        within the given world size.

        Args:
            world_size (tuple): width and height of the world which this person
                can roam around centered at (0, 0) on the default turtlescreen
            radius (int): radius of this person in pixels
            colour (tuple): an RGB colour where each channel is a float
                between 0 and 1.0

        Raises:
            ValueError: world size is smaller than this person
        """

        if any(dim < (radius * 2) for dim in world_size):
            raise ValueError("world size is smaller than this person")

        self.world_size = world_size
        self.radius = radius
        self.location = self._get_random_location()
        self.destination = self._get_random_location()
        self.viruses = list()
        self.colour = colour

    def _get_random_location(self):
        """Returns a random (x, y) position within this person's world size.

        The returned position will be no closer than 1 radius to the edge of
        this person's world.
        """

        width, height = self.world_size

        # # Generate a random (x, y) coordinate within the world's borders
        x = random.uniform(self.radius, width - self.radius)
        y = random.uniform(self.radius, height - self.radius)

        x -= width // 2
        y -= height // 2

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
            colour = [sum(channel) / n for channel in zip(*colours)]

        return tuple(colour)

    def draw(self):
        """Draws this person as a coloured dot at their current location.

        The colour will be the colour from this colour attribute if they aren't
        infected, otherwise it will be average colour of the virus(es) they are
        infected by.
        """
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

    def collision_list(self, people):
        """Returns a list of people from the given list who are in contact
        with this person.
        """
        return [person for person in people if self.collides(person)]

    def infect(self, virus):
        """Infects this person with the given virus if they aren't already
        infected by it, otherwise refreshes the virus' duration on this person.
        """

        try:
            self.get_virus(virus).reset_duration()
        except:
            self.viruses.append(virus)

    def reached_destination(self):
        """Returns True if this person's location is within 1 radius of
        destination, otherwise returns False.
        """
        return distance_2d(self.location, self.destination) <= self.radius

    def progress_illness(self):
        """Progress this person's viruses, curing them if it's run out."""
        for virus in self.viruses.copy():
            virus.progress()
            if virus.is_cured():
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
        """Moves this person radius / 2 towards their destination. If their
        destination is closer than radius / 2, they will move directly to their
        destination instead.
        """
        turtle.penup()  # Ensure nothing is drawn while moving
        turtle.setpos(self.location)

        distance = distance_2d(self.location, self.destination)

        # Clamp distance below radius / 2 (inclusive)
        half_radius = self.radius / 2
        if distance > half_radius:
            distance = half_radius

        # Move the person towards their destination
        turtle.setheading(turtle.towards(self.destination))
        turtle.forward(distance)
        self.location = turtle.pos()

    def cure(self, virus=None):
        """Cures the instance of the given virus' class on this person,
        otherwise, if a virus isn't given, removes all viruses on this person.
        """
        if virus is None:
            for v in self.viruses.copy():
                v.cure(self)
        else:
            virus.cure(self)

    def remove_virus(self, virus):
        """Removes the given virus from this person.

        Raises:
            ValueError: Person.remove_virus(x): x not in Person.viruses
        """
        try:
            self.viruses.remove(virus)
        except:
            raise ValueError('Person.remove_virus(x): x not in Person.viruses')

    def is_infected(self):
        """Returns True if this person is infected, else False."""
        return bool(len(self.viruses))

    def get_virus(self, virus):
        """Returns the instance of the given virus' class on this person (if
        any), otherwise returns None.
        """
        for v in self.viruses:
            if isinstance(v, virus.__class__):
                return v
        return None  # For clarity

    def has_virus(self, virus):
        """Returns True if this person has the given virus, else False."""
        return bool(self.get_virus(virus))


class World:
    """This class represents a simulated world containing people who can be
    infected by viruses.
    """

    def __init__(self,
                 width,
                 height,
                 n,
                 viruses=[
                     RainbowVirus, ZebraVirus, ImmunisableVirus, ZombieVirus,
                     SnakeVirus
                 ]):
        """Creates a new world centered on (0, 0) containing n people which
        simulates the spread of the given virus(es) through this world.

        Args:
            width (int): horizontal length of the world in pixels
            height (int): vertical length of the world in pixels
            n (int): number of people to add to this world
            viruses (iterable): virus classes that will be used to infect
                people in this world

        Raises:
            ValueError: width and height must be even
        """

        if width % 2 != 0 or height % 2 != 0:
            raise ValueError("width and height must be even")

        self.size = (width, height)
        self.hours = 0
        self.people = []
        self.viruses = viruses
        self.collision_table = EfficientCollision(28)
        for _ in range(n):
            self.add_person()

        # Reset each virus and add the on_world_update method for each virus if
        # they have one
        self.on_update_methods = []
        for cls in self.viruses:
            cls.reset_class()
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
        """Draws this world on the default turtle screen.

        - Clears the current screen
        - Draws all the people in this world
        - Draws the box that frames this world
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


# def draw_text(x, y, text, align='left', colour='black'):
def draw_text(x, y, text, colour='black', *args, **kwargs):
    """Wrapper for turtle.write which takes an (x, y) position to write the
    text at and an optional text colour.
    """
    turtle.penup()  # Ensure nothing is drawn while moving
    turtle.color(colour)
    turtle.setpos(x, y)
    turtle.write(text, *args, **kwargs)


def draw_rect(x, y, width, height, colour='black'):
    """Draws a rectangle starting from the top-left corner."""

    # Draw the top-left corner of the rectangle
    draw_line(x, y, width, orientation="horizontal", colour='black')
    draw_line(x, y, height, colour='black')

    # Draw the bottom-right corner of the rectangle
    x += width
    y -= height
    draw_line(x,
              y,
              width,
              orientation="horizontal",
              reverse=True,
              colour='black')
    draw_line(x, y, height, reverse=True, colour='black')


def draw_line(x,
              y,
              length,
              orientation="vertical",
              reverse=False,
              colour='black'):
    """Draws a line starting at the given coordinates.

    Args:
        x (int): horizontal coordinate on the default turtle screen
        y (int): vertical coordinate on the default turtle screen
        length (int): length of the line in pixels
        orientation (str): 'vertical' to draw a vertical line from the top-down
            starting at the given x, y coordinates, 'horizontal' to draw the
            line left-to-right
        reverse (bool): True to reverse the draw direction, e.g. draw
            bottom-top instead of top-down
        colour: colour of the line, can be any valid colour accepted by the
            turtle module
    """
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
    """Handles the user interface for the simulation

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
        self.framework = AnimationFramework(self.WIDTH, self.HEIGHT,
                                            self.TITLE)

        self.framework.add_key_action(self.setup, 'z')
        self.framework.add_key_action(self.infect, 'x')
        self.framework.add_key_action(self.cure, 'c')
        self.framework.add_key_action(self.toggle_simulation, " ")
        self.framework.add_tick_action(self.next_turn)

        self.world = None

    def setup(self):
        """Reset the simulation to the initial state."""
        print('resetting the world')
        self.framework.stop_simulation()
        self.world = World(self.WIDTH - self.MARGIN * 2,
                           self.HEIGHT - self.MARGIN * 2, self.PEOPLE)
        self.world.draw()

    def infect(self):
        """Infect a person and redraw the world if the simulation isn't
        running.
        """
        print('infecting a person')
        self.world.infect_person()
        if not self.framework.simulation_is_running():
            self.world.draw()

    def cure(self):
        """Remove infections from all the people and redraw the world if the
        simulation isn't running.
        """
        print('cured all people')
        self.world.cure_all()
        if not self.framework.simulation_is_running():
            self.world.draw()

    def toggle_simulation(self):
        """Starts and stops the simulation."""
        if self.framework.simulation_is_running():
            self.framework.stop_simulation()
        else:
            self.framework.start_simulation()

    def next_turn(self):
        """Perform the tasks needed for the next animation cycle."""
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
