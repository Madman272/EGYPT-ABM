from tkinter import *
import time
import numpy
import random
import math
import csv

# All comments that start with ';' are copied from the original model

# Each patch represents a single square of land in the grid
class Patch:
    water = False           #  Whether patch is in the river
    fertility = 0
    settlement = False
    owned = False
    color = "yellow"
    population = 0
    harvested = False
    years_fallow = 0
    times_farmed = 0
    q_value = 0

# Squares on the map represent settlements which are each made up of a number of households
class Household:
    def __init__(self, position_x, position_y, grain, workers, ambition, competency, exploration, workers_worked, generation_countdown, fields_owned):
        self.position_x = position_x
        self.position_y = position_y
        self.grain = grain
        self.workers = workers
        self.ambition = ambition
        self.competency = competency
        self.exploration = exploration
        self.workers_worked = workers_worked
        self.generation_countdown = generation_countdown
        self.fields_owned = fields_owned
        self.fields_coord = []
        self.fields_q = []

# Class stores global variables used for outputs
class Globals:
    surplus = 0
    total_households = 0
    total_population = 0
    projected_historical_population = 0
    lorenz_points = 0
    avg_competency = 0
    avg_ambition = 0
    avg_explore = 0
    gini_index_reserve = 0                      # Statistical measure of wealth inequality among agents; higher value is greater inequality
    populations = []
    grains = []
    output_lines = [["Year","Surplus", "Total Households", "Total Population", "Projected Historical Population", "Average Ambition", "Average Competency", "Average Exploration", "Gini Index Reserve", "Household Populations", "Household Grains"]]

# Main frame used for gui
class App(Frame):
        def __init__(self, master):
            Frame.__init__(self,master)
            self.grid()
            self.years = 0

            #Array used to store the labels that make up the map
            self.labelsArr = numpy.empty(36, dtype=object)
            for i in range(36):
                self.labelsArr[i] = numpy.empty(36, dtype=object)

            #Array used to store patch information
            self.patchesArr = numpy.empty(36, dtype=object)
            for i in range(36):
                self.patchesArr[i] = numpy.empty(36, dtype=object)

            #Sets up the GUI
            self.menu_left = Frame(self, width=200, bg="grey")

            self.create_w()
            self.run_mode()
            self.max_years()
            self.starting_households()
            self.starting_workers()
            self.starting_grain()
            self.min_ambition()
            self.min_comp()
            self.generational_variation()
            self.knowledge_radius()
            self.distance_cost()
            self.fallow_limit()
            self.pop_growth_rate()
            self.max_exploration()
            self.explore_reduction()

            self.menu_left.pack(side="top", fill="both", expand=TRUE)

            self.canvas = Canvas(self, width=500,height=400,background="white")

            self.menu_left.grid(row=0, column=0, rowspan=2, sticky="nsew")
            self.canvas.grid(row=1, column=1, sticky="nsew")

            self.grid_rowconfigure(1, weight=1)
            self.grid_columnconfigure(1, weight=1)
            #end of GUI setup


# --------------------------- GUI element definitions start here here ---------------------------
        def create_w(self):
            self.label1 = Label(self.menu_left, text = "Year : 0")
            self.button1 = Button(self.menu_left)
            self.button1["text"] = "Go"
            self.button1["command"] = self.next_year
            self.button1.grid(row =0, column =0, columnspan =2, sticky =W)
            self.label1.grid(row=0, column=1, sticky=W)

            self.button3 = Button(self.menu_left)
            self.button3["text"] = "Go Repeating"
            self.button3["command"] = self.next_year_repeat
            self.button3.grid(row=1, column=0, columnspan=2, sticky=W)

            self.button2 = Button(self.menu_left)
            self.button2["text"] = "Setup"
            self.button2["command"] = self.setup
            self.button2.grid(row=2, column=0, sticky=W)

        # Gets mode in which simulation run should take place; Mode 1: full knowledge(standard model), Mode 2: Q-learning, Mode 3: Q-learning with information sharing
        def run_mode(self):
            self.label2 = Label(self.menu_left, text="Mode")
            self.label2.grid(row=3, column=0, sticky=W)
            self.mode = Scale(self.menu_left, from_=1, to=3, orient=HORIZONTAL)
            self.mode.set(1)
            self.mode.grid(row=3, column=1, sticky=W)

        # Gets years until which go repeating will run
        def max_years(self):
            self.label3 = Label(self.menu_left, text="Max years")
            self.label3.grid(row=4, column=0, sticky=W)
            self.maxYears = Scale(self.menu_left, from_=1, to=500, orient=HORIZONTAL)
            self.maxYears.set(5)
            self.maxYears.grid(row=4, column=1, sticky=W)

        # Gets amount of starting households
        def starting_households(self):
            self.label4 = Label(self.menu_left, text="Starting households")
            self.label4.grid(row=5, column=0, sticky=W)
            self.startHouseholds = Scale(self.menu_left, from_=1, to=20, orient=HORIZONTAL)
            self.startHouseholds.set(20)
            self.startHouseholds.grid(row=5, column=1, sticky=W)

        # Gets amount of starting workers
        def starting_workers(self):
            self.label5 = Label(self.menu_left, text="Starting workers")
            self.label5.grid(row=6, column=0, sticky=W)
            self.startWorkers = Scale(self.menu_left, from_=1, to=30, orient=HORIZONTAL)
            self.startWorkers.set(5)
            self.startWorkers.grid(row=6, column=1, sticky=W)

        # Gets amount of starting grain
        def starting_grain(self):
            self.label6 = Label(self.menu_left, text="Starting grain")
            self.label6.grid(row=7, column=0, sticky=W)
            self.startGrain = Scale(self.menu_left, from_=0, to=7500, resolution=100, orient=HORIZONTAL)
            self.startGrain.set(2000)
            self.startGrain.grid(row=7, column=1, sticky=W)

        # Gets minimum ambition value a household can have at start
        def min_ambition(self):
            self.label7 = Label(self.menu_left, text="Min Ambition")
            self.label7.grid(row=8, column=0, sticky=W)
            self.minAm = Scale(self.menu_left, from_=0.0, to=1.0, digits=2, resolution=0.1, orient=HORIZONTAL)
            self.minAm.set(0.5)
            self.minAm.grid(row=8, column=1, sticky=W)

        # Gets minimum ambition value a household can have at start
        def min_comp(self):
            self.label8 = Label(self.menu_left, text="Min competency")
            self.label8.grid(row=9, column=0, sticky=W)
            self.minComp = Scale(self.menu_left, from_=0.0, to=1.0, digits=2, resolution=0.1, orient=HORIZONTAL)
            self.minComp.set(0.5)
            self.minComp.grid(row=9, column=1, sticky=W)

        # Gets how much agent personality variables can change by on each generation
        def generational_variation(self):
            self.label9 = Label(self.menu_left, text="Generational variation")
            self.label9.grid(row=10, column=0, sticky=W)
            self.genVar = Scale(self.menu_left, from_=0.0, to=1.0, digits=2, resolution=0.05, orient=HORIZONTAL)
            self.genVar.set(0.5)
            self.genVar.grid(row=10, column=1, sticky=W)

        # Gets how far away from their base agents are able see and interact with the environment
        def knowledge_radius(self):
            self.label10 = Label(self.menu_left, text="Knowledge radius")
            self.label10.grid(row=11, column=0, sticky=W)
            self.knowRad = Scale(self.menu_left, from_=1, to=35, orient=HORIZONTAL)
            self.knowRad.set(10)
            self.knowRad.grid(row=11, column=1, sticky=W)

        # Gets how great the penalty is for farming distant lands
        def distance_cost(self):
            self.label11 = Label(self.menu_left, text="Distance cost")
            self.label11.grid(row=12, column=0, sticky=W)
            self.distanceCost = Scale(self.menu_left, from_=0, to=50, orient=HORIZONTAL)
            self.distanceCost.set(10)
            self.distanceCost.grid(row=12, column=1, sticky=W)

        # Gets how long a field must be unharvested for until the agent loses ownership; at 0 this feature is disabled
        def fallow_limit(self):
            self.label12 = Label(self.menu_left, text="Fallow limit(years)")
            self.label12.grid(row=13, column=0, sticky=W)
            self.fallowLim = Scale(self.menu_left, from_=0, to=10, orient=HORIZONTAL)
            self.fallowLim.set(5)
            self.fallowLim.grid(row=13, column=1, sticky=W)

        # Gets the rate at which the population grows
        def pop_growth_rate(self):
            self.label13 = Label(self.menu_left, text="Pop growth rate(%)")
            self.label13.grid(row=14, column=0, sticky=W)
            self.popGR = Scale(self.menu_left, from_=0.00, to=0.20, digits=2, resolution=0.01, orient=HORIZONTAL)
            self.popGR.set(0.1)
            self.popGR.grid(row=14, column=1, sticky=W)

        # Gets the max value of how likely an agent is to explore harvesting newer(less harvested) fields during q-learning
        def max_exploration(self):
            self.label14 = Label(self.menu_left, text="Max exploration")
            self.label14.grid(row=15, column=0, sticky=W)
            self.maxExplore = Scale(self.menu_left, from_=0.5, to=1, digits=3, resolution=0.05, orient=HORIZONTAL)
            self.maxExplore.set(0.75)
            self.maxExplore.grid(row=15, column=1, sticky=W)

        # Gets gets how much the explore value is reduced by each year
        def explore_reduction(self):
            self.label15 = Label(self.menu_left, text="Exploration Reduction per Year")
            self.label15.grid(row=16, column=0, sticky=W)
            self.expReduce = Scale(self.menu_left, from_=0, to=0.05, digits=2, resolution=0.005, orient=HORIZONTAL)
            self.expReduce.set(0.025)
            self.expReduce.grid(row=16, column=1, sticky=W)

# --------------------------- GUI element definitions end here here ---------------------------



# --------------------------- Model methods start here here ---------------------------

        #Setup settlements and households;  Run when setup button pressed
        def setup(self):
            self.years = 0
            self.globalsVars = Globals()

            self.avgYield = 2776            # Average potential yield of patches according to historical data; lookup source later
            self.workerRation = 164         # Ammount of grain (kg) consumed by each worker per year according to historical data; lookup source later

            #Array used to store household info
            self.householdArr = []

            self.setup_patches()
            self.setup_households()
            if self.mode.get() == 2:
                self.setup_household_q_values()
            self.globalsVars.total_households = self.startHouseholds.get()

            for i in range(36):
                for j in range(36):
                    if j == 0:
                        self.patchesArr[i][j].color = "blue"
                        self.patchesArr[i][j].water = True
                        self.labelsArr[i][j] = Label(self.canvas, width=2, height=1, bg=self.patchesArr[i][j].color)
                        self.labelsArr[i][j].grid(row=i, column=j)
                    else:
                        self.labelsArr[i][j] = Label(self.canvas, width =2, height=1, bg=self.patchesArr[i][j].color)
                        self.labelsArr[i][j].grid(row=i, column=j)

        #Creates array of patches
        def setup_patches(self):
            for i in range(36):
                for j in range(36):
                    self.patchesArr[i][j] = Patch()

        #Places households
        def setup_households(self):
            counter = 0
            while counter < self.startHouseholds.get():
                randX = random.randint(0, 35)
                randY = random.randint(1, 35)

                #checks if patch is free and if no other settlement too close
                if self.patchesArr[randX][randY].settlement is False and self.patchesArr[randX][randY].water is False and self.patchesArr[randX][randY].owned is False:
                    found = False
                    for x in range(-5, 6):
                        for y in range(-5, 6):
                            if (randX + x < 36 and randY + y < 36 and randX + x > -1 and randY + y > -1):
                                if (self.patchesArr[randX + x][randY + y].settlement is True):
                                    found = True
                    if found is False:
                        self.patchesArr[randX][randY].settlement = True
                        self.patchesArr[randX][randY].color = "brown"
                        self.patchesArr[randX][randY].fertility = 0
                        self.create_household(randX, randY)
                        self.claim_immediate_fields(counter)
                        counter += 1

        # Populates householdArr with a household
        def create_household(self, x, y):
            grain = self.startGrain.get()
            workers = self.startWorkers.get()
            ambition = self.minAm.get() + random.uniform(0, 1 - self.minAm.get())
            competency = self.minComp.get() + random.uniform(0, 1 - self.minComp.get())
            exploration =  random.uniform(0.49, self.maxExplore.get())
            workers_worked = 0
            gencountdown = random.randint(1, 5) + 10
            fields_owned = 0
            self.patchesArr[x][y].population += workers
            self.householdArr.append(Household(x, y, grain, workers, ambition, competency, exploration, workers_worked, gencountdown, fields_owned))

        # New settlements claim the fields in the immediate radius
        def claim_immediate_fields(self, index):
            posX = self.householdArr[index].position_x
            posY = self.householdArr[index].position_y
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if (x != 0) or (y != 0):
                        if (posX + x < 36 and posY + y < 36 and posX + x > -1 and posY + y > 0):
                            self.patchesArr[posX + x][posY + y].owned = True
                            self.patchesArr[posX + x][posY + y].harvested = False
                            self.patchesArr[posX + x][posY + y].years_fallow = 0
                            self.householdArr[index].fields_owned += 1
                            self.householdArr[index].fields_coord.append((posX + x, posY + y))
                            self.patchesArr[posX + x][posY + y].color = 'pink'  # Set field colour show field is claimed

        # Initialises individual household arrays of q values if mode 2 was selected
        def setup_household_q_values(self):
            for i in range(len(self.householdArr)):
                self.householdArr[i].fields_q = numpy.empty(36, dtype=object)
                for j in range(36):
                    self.householdArr[i].fields_q[j] = numpy.empty(36, dtype=object)
                    for k in range(36):
                        self.householdArr[i].fields_q[j][k] = 0

        def _from_rgb(self, rgb):
            """translates an rgb tuple of int to a tkinter friendly color code
            """
            return "#%02x%02x%02x" % rgb

        def update_patch_color(self):
            for i in range(36):
                for j in range(36):
                    self.labelsArr[i][j].config(bg=self.patchesArr[i][j].color)

        # Repeats simulation runs until 500 years are done
        def next_year_repeat(self):
            while self.years != self.maxYears.get() and self.globalsVars.total_households > 0:
                self.go()
                self.years += 1
                self.label1["text"] = "Year : " + str(self.years)

        # Runs one year of simulation
        def next_year(self):
            if self.globalsVars.total_households > 0:
                self.go()
                self.years += 1
                self.label1["text"] = "Year : " + str(self.years)

        # Runs all functions for a single year of simulation
        def go(self):
            if self.mode.get() != 1:
                self.claim_lands_Q_learning()
            self.flood()
            if self.mode.get() == 1:
                self.claim_lands()
                self.harvest_farms()
            else:
                self.harvest_farms_q_learning()
            self.consume_grain()
            if self.fallowLim.get() != 0:
                self.field_changeover()
            self.generational_changeover()
            self.population_shift()
            self.update_plot_values()
            self.output_globals()
            self.update_patch_color()
            self.update()

        # ; This method assigns a fertility value to each field based on its distance to water patches (ie: the Nile).
        def flood(self):
            lam = random.uniform(0,0.5)
            xmod = random.randint(2, 5)
            # Set fertility for patches that are not in the river nor has a settlement
            for i in range(36):
                for j in range(36):
                    if j !=0:
                        if (self.patchesArr[i][j].water is False) and (self.patchesArr[i][j].settlement is False):
                            self.patchesArr[i][j].fertility = 17 * lam * ((math.e) ** (-1 * lam * (math.ceil(j / xmod))))
                            # Set block colour according to fertility if not owned field
                            if self.patchesArr[i][j].owned == False:
                                temp = 20.0 * (self.patchesArr[i][j].fertility/1.3)
                                if temp > 150:
                                    temp = 150
                                temp = 150 - temp
                                self.patchesArr[i][j].color = self._from_rgb((0, math.floor(temp), 0))
                            else:
                                self.patchesArr[i][j].color = 'pink'  # Reset field colour to pink if owned
                            self.patchesArr[i][j].harvested = False

        # ; This method allows households to decide whether or not to claim fields that fall within their knowledge-radii.
        # ; The decision to claim is a function of distance to the field, the amount of grain needed to survive the walk, the fertility of the field, and ambition.
        # ; It also sets ownership of fields (rendering them farms) to households that claim them.
        def claim_lands(self):
            for i in range(len(self.householdArr)):
                claimChance = random.uniform(0, 1)
                if (claimChance < self.householdArr[i].ambition) or (self.householdArr[i].fields_owned <= 1):  # ; decide if this household will be trying to claim land this tick
                    posX = self.householdArr[i].position_x
                    posY = self.householdArr[i].position_y
                    currGrain = self.householdArr[i].grain
                    bestFertX = posX
                    bestFertY = posY
                    bestFertility = -9999999999999
                    radius = self.knowRad.get()
                    # Randomises from which direction the loops start
                    if (random.uniform(0, 1) > 0.5):
                        xstart = (-1) * radius
                        xend = radius + 1
                        xstep = 1
                    else:
                        xstart = radius
                        xend = (-1) * radius - 1
                        xstep = -1
                    if (random.uniform(0, 1) > 0.5):
                        ystart = (-1) * radius
                        yend = radius + 1
                        ystep = 1
                    else:
                        ystart = radius
                        yend = (-1) * radius - 1
                        ystep = -1
                    # Find best patch in knowledge radius
                    for x in range(xstart, xend, xstep):
                        for y in range(ystart, yend, ystep):
                            if x != 0 or y != 0:
                                distance = math.sqrt((x ** 2) + (y ** 2))
                                distanceFactor = distance * self.distanceCost.get()
                                if (posX + x < 36 and posY + y < 36 and posX + x > -1 and posY + y > 0):
                                    if (self.patchesArr[posX + x][posY + y].settlement is False) and (self.patchesArr[posX + x][posY + y].water is False) and (self.patchesArr[posX + x][posY + y].owned is False):
                                        if (((self.patchesArr[posX + x][posY + y].fertility * self.avgYield * ((1+self.minComp.get())/2)) - distanceFactor) > bestFertility) and (distanceFactor < currGrain):    # avgYield and avgComp used to accurately account for distanceFactor
                                            bestFertX = posX + x
                                            bestFertY = posY + y
                                            bestFertility = (self.patchesArr[posX + x][posY + y].fertility * 2082) - distanceFactor
                    # Claim field if appropriate field is found
                    if (self.patchesArr[bestFertX][bestFertY].settlement is False) and (self.patchesArr[bestFertX][bestFertY].water is False) and (self.patchesArr[bestFertX][bestFertY].owned is False):
                        self.patchesArr[bestFertX][bestFertY].owned = True
                        self.patchesArr[bestFertX][bestFertY].harvested = False
                        self.patchesArr[bestFertX][bestFertY].years_fallow = 0
                        self.householdArr[i].fields_owned += 1
                        self.householdArr[i].fields_coord.append((bestFertX, bestFertY))
                        self.patchesArr[bestFertX][bestFertY].color = 'pink'    # Set field colour show field is claimed

        # Special version of the claim lands method used during q-learning runs; run before flooding flooding method
        def claim_lands_Q_learning(self):
            for i in range(len(self.householdArr)):
                claimChance = random.uniform(0, 1)
                if (claimChance < self.householdArr[i].ambition) or (self.householdArr[i].fields_owned <= 1):  # ; decide if this household will be trying to claim land this tick
                    posX = self.householdArr[i].position_x
                    posY = self.householdArr[i].position_y
                    currGrain = self.householdArr[i].grain
                    bestX = posX
                    bestY = posY
                    bestQ = -999999999999999
                    radius = self.knowRad.get()
                    # Randomises from which direction the loops start
                    if (random.uniform(0, 1) > 0.5):
                        xstart = (-1) * radius
                        xend = radius + 1
                        xstep = 1
                    else:
                        xstart = radius
                        xend = (-1) * radius - 1
                        xstep = -1
                    if (random.uniform(0, 1) > 0.5):
                        ystart = (-1) * radius
                        yend = radius + 1
                        ystep = 1
                    else:
                        ystart = radius
                        yend = (-1) * radius - 1
                        ystep = -1
                    # Find best patch in knowledge radius
                    for x in range(xstart, xend, xstep):
                        for y in range(ystart, yend, ystep):
                            if x != 0 or y != 0:
                                distance = math.sqrt((x ** 2) + (y ** 2))
                                distanceFactor = distance * self.distanceCost.get()
                                if (posX + x < 36 and posY + y < 36 and posX + x > -1 and posY + y > 0):
                                    # Consider q-values from individual q-table if mode 2, or shared q-table in mode 3
                                    if self.mode.get() == 2:
                                        if (self.patchesArr[posX + x][posY + y].settlement is False) and (self.patchesArr[posX + x][posY + y].water is False) and (self.patchesArr[posX + x][posY + y].owned is False):
                                            if ((self.householdArr[i].fields_q[posX + x][posY + y] - distanceFactor) > bestQ) and (distanceFactor < currGrain):
                                                bestX = posX + x
                                                bestY = posY + y
                                                bestQ = self.householdArr[i].fields_q[posX + x][posY + y] - distanceFactor
                                    else:
                                        if (self.patchesArr[posX + x][posY + y].settlement is False) and (self.patchesArr[posX + x][posY + y].water is False) and (self.patchesArr[posX + x][posY + y].owned is False):
                                            if ((self.patchesArr[posX + x][posY + y].q_value - distanceFactor) > bestQ) and (distanceFactor < currGrain):
                                                bestX = posX + x
                                                bestY = posY + y
                                                bestQ = self.patchesArr[posX + x][posY + y].q_value - distanceFactor
                    # Claim field if appropriate field is found
                    if (self.patchesArr[bestX][bestY].settlement is False) and (self.patchesArr[bestX][bestY].water is False) and (self.patchesArr[bestX][bestY].owned is False):
                        self.patchesArr[bestX][bestY].owned = True
                        self.patchesArr[bestX][bestY].harvested = False
                        self.patchesArr[bestX][bestY].years_fallow = 0
                        self.householdArr[i].fields_owned += 1
                        self.householdArr[i].fields_coord.append((bestX, bestY))
                        self.patchesArr[bestX][bestY].color = 'pink'  # Set field colour show field is claimed

        # ; Determines which farms are harvested each year. A household may only harvest one farm for each 2 workers they have.
        # ; For each  2 workers, the highest yield farm is found. The worker then decides whether they are ambitious and competent enough to harvest. A harvested farm is then marked with an 'H'.
        # ; Once a farm is harvested for the year, it may not be harvested again that year.
        # ; A 'seeding cost' is deducted; the seeding cost is calculated at 65kg/feddan; in the current setup, each patch is 200x200m, or 40,000m2.
        # ; A feddan = 4200m2, so each patch equals 9.52 feddans, so 9.52 * 65kg equals 618. If the layout of the world is changed, then the seeding cost will need to be recalculated.
        def harvest_farms(self):
            for i in range(len(self.householdArr)):
                totalHarvest = 0
                householdX = self.householdArr[i].position_x
                householdY = self.householdArr[i].position_y
                householdComp = self.householdArr[i].competency
                self.householdArr[i].workers_worked = 0
                for k in range(self.householdArr[i].workers):
                    bestHarvest = 0
                    bestFieldX = 0
                    bestFieldY = 0
                    # Find best field for harvesting
                    for l in range(self.householdArr[i].fields_owned):
                        fieldX = self.householdArr[i].fields_coord[l][0]
                        fieldY = self.householdArr[i].fields_coord[l][1]
                        dist = math.sqrt(((householdX - fieldX) ** 2) + ((householdY - fieldY) ** 2))
                        thisHarvest = ((self.patchesArr[fieldX][fieldY].fertility * self.avgYield * householdComp) - (dist * self.distanceCost.get()))
                        if (self.patchesArr[fieldX][fieldY].harvested is False) and (thisHarvest > bestHarvest):
                            bestHarvest = thisHarvest
                            bestFieldX = fieldX
                            bestFieldY = fieldY
                    farmChance = random.uniform(0, 1)
                    # Harvest field if one is available
                    if (bestHarvest != 0):
                        if (self.householdArr[i].grain < (self.householdArr[i].workers * self.workerRation)) or (farmChance < (self.householdArr[i].ambition * householdComp)):
                            self.patchesArr[bestFieldX][bestFieldY].harvested = True
                            self.patchesArr[bestFieldX][bestFieldY].color = 'red'   # Mark field as harvested
                            totalHarvest += bestHarvest - 618  # ; 618 = cost of seeding the field
                            self.householdArr[i].workers_worked += 1
                self.householdArr[i].grain += totalHarvest

        # Special version of the harvest farms method used during q-learning runs
        def harvest_farms_q_learning(self):
            for i in range(len(self.householdArr)):
                self.householdArr[i].workers_worked = 0
                # Get copy of coordinates of owned fields and corresponding q-values
                unfarmed = self.householdArr[i].fields_coord.copy()
                unfarmedQValues = []
                unfarmedTimesFarmed = []
                harvestingFields = []
                # Consider q-values from individual q-table if mode 2, or shared q-table in mode 3
                if self.mode.get() == 2:
                    for j in range(self.householdArr[i].fields_owned):
                        unfarmedTimesFarmed.append(self.patchesArr[unfarmed[j][0]][unfarmed[j][1]].times_farmed)
                        unfarmedQValues.append(self.householdArr[i].fields_q[unfarmed[j][0]][unfarmed[j][1]])
                else:
                    for j in range(self.householdArr[i].fields_owned):
                        unfarmedTimesFarmed.append(self.patchesArr[unfarmed[j][0]][unfarmed[j][1]].times_farmed)
                        unfarmedQValues.append(self.patchesArr[unfarmed[j][0]][unfarmed[j][1]].q_value)
                # All farms selected if enough workers
                if self.householdArr[i].workers >= self.householdArr[i].fields_owned:
                    harvestingFields = unfarmed.copy()
                else:
                    for k in range(self.householdArr[i].workers):
                        if (len(unfarmedQValues) > 0):
                            # Check if remaining unfarmed fields have equal q-values and choose randomly from them if they do
                            equal = True
                            for l in  range(len(unfarmedQValues)-1):
                                if (unfarmedQValues[l] != unfarmedQValues[l+1]):
                                    equal = False
                                    break
                            if (equal):
                                rand = random.randint(0, len(unfarmedQValues)-1)
                                harvestingFields.append(unfarmed[rand])
                                unfarmed[rand] = "x"
                                unfarmed.remove("x")
                                unfarmedTimesFarmed[rand] = "x"
                                unfarmedTimesFarmed.remove("x")
                                unfarmedQValues[rand] = "x"
                                unfarmedQValues.remove("x")
                            else:
                                exploreChance = random.uniform(0, 1)
                                # Chance of exploiting best current option or exploring new option
                                if exploreChance < self.householdArr[i].exploration and self.householdArr[i].exploration != 0:
                                    # Explore new option
                                    rank = math.ceil(exploreChance / self.householdArr[i].exploration * len(unfarmedQValues)) -1
                                    sortedTimes = unfarmedQValues.copy()
                                    sortedTimes.sort()
                                    qTime = sortedTimes[rank]
                                    qIn = unfarmedQValues.index(qTime)
                                    harvestingFields.append(unfarmed[qIn])
                                    unfarmed[qIn] = "x"
                                    unfarmed.remove("x")
                                    unfarmedTimesFarmed[qIn] = "x"
                                    unfarmedTimesFarmed.remove("x")
                                    unfarmedQValues[qIn] = "x"
                                    unfarmedQValues.remove("x")
                                else:
                                    # Choose current best option
                                    bestQ = unfarmedQValues[0]
                                    bestIn = 0
                                    for l in range(1, len(unfarmedQValues)):
                                        if unfarmedQValues[l] > bestQ:
                                            bestQ = unfarmedQValues[l]
                                            bestIn = l
                                    harvestingFields.append(unfarmed[bestIn])
                                    unfarmed[bestIn] = "x"
                                    unfarmed.remove("x")
                                    unfarmedTimesFarmed[bestIn] = "x"
                                    unfarmedTimesFarmed.remove("x")
                                    unfarmedQValues[bestIn] = "x"
                                    unfarmedQValues.remove("x")
                # Attempt to farm all fields chosen before
                totalHarvest = 0
                harvests = []
                for j in range(len(harvestingFields)):
                    farmChance = random.uniform(0, 1)
                    if (self.householdArr[i].grain < (self.householdArr[i].workers * self.workerRation)) or (farmChance < (self.householdArr[i].ambition * self.householdArr[i].competency)):
                        self.patchesArr[harvestingFields[j][0]][harvestingFields[j][1]].harvested = True
                        self.patchesArr[harvestingFields[j][0]][harvestingFields[j][1]].color = 'red'   # Mark field as harvested
                        self.patchesArr[harvestingFields[j][0]][harvestingFields[j][1]].times_farmed += 1
                        dist = math.sqrt(((self.householdArr[i].position_x - harvestingFields[j][0]) ** 2) + ((self.householdArr[i].position_y - harvestingFields[j][1]) ** 2))
                        thisHarvest = self.patchesArr[harvestingFields[j][0]][harvestingFields[j][1]].fertility * self.avgYield * self.householdArr[i].competency
                        harvests.append(thisHarvest)
                        totalHarvest += thisHarvest
                        self.householdArr[i].workers_worked += 1
                    else:
                        harvests.append("x")
                if self.householdArr[i].workers_worked > 0:
                    # Ajust q-values according to difference between harvested grain on patch and average grain harvested by the household
                    avgHarvest = totalHarvest / self.householdArr[i].workers_worked
                    # Update q-values from individual q-table if mode 2, or shared q-table in mode 3
                    if self.mode.get() == 2:
                        for j in range(len(harvests)):
                            if harvests[j] != "x":
                                self.householdArr[i].fields_q[harvestingFields[j][0]][harvestingFields[j][1]] += (harvests[j] - avgHarvest)
                    else:
                        for j in range(len(harvests)):
                            if harvests[j] != "x":
                                self.patchesArr[harvestingFields[j][0]][harvestingFields[j][1]].q_value += (harvests[j] - avgHarvest)
                    # Add total harvest to household grain
                    for j in range(len(harvests)):
                        if harvests[j] != "x":
                            self.householdArr[i].grain += (harvests[j] - (dist * self.distanceCost.get()) - 618)  # ; 618 = cost of seeding the field

        # decreases grain, kills a member if not enough grain, and remove household if no members
        def consume_grain(self):
            for i in range(len(self.householdArr)-1, -1, -1):     # Loop backwards so removals don't break anything
                self.householdArr[i].grain -= (self.householdArr[i].workers * self.workerRation)
                if self.householdArr[i].grain <= 0:
                    self.householdArr[i].grain = 0
                    self.householdArr[i].workers -= 1
                    self.patchesArr[self.householdArr[i].position_x][self.householdArr[i].position_y].population -= 1
                # combined the storage loss function here since it seemed extra to have it as an additional function
                # ; accounts for typical annual storage loss of agricultural product to storage-loss
                self.householdArr[i].grain -= (self.householdArr[i].grain * 0.1)
                # Set empty household's fields to not owned and remove household
                if self.householdArr[i].workers <= 0:
                    for k in range(self.householdArr[i].fields_owned):
                        self.patchesArr[self.householdArr[i].fields_coord[k][0]][self.householdArr[i].fields_coord[k][1]].owned = False
                    self.patchesArr[self.householdArr[i].position_x][self.householdArr[i].position_y].color = 'grey'
                    self.householdArr[i] = 0
                    self.householdArr.remove(0)

        # ; allows fields that have lay fallow for a certain number of years to be forfeited for claim by other households to field-changeover
        def field_changeover(self):
            removal = False
            for i in range(36):
                for j in range(36):
                    if self.patchesArr[i][j].owned is True:
                        if self.patchesArr[i][j].harvested is True:
                            self.patchesArr[i][j].years_fallow = 0
                        else:
                            self.patchesArr[i][j].years_fallow += 1
                        if self.patchesArr[i][j].years_fallow > self.fallowLim.get():
                            removal = True
                            self.patchesArr[i][j].owned = False
                            self.patchesArr[i][j].owned = False
            # loop through households to remove fields that are no longer owned
            if removal is True:
                for i in range(len(self.householdArr)):
                    for k in range(self.householdArr[i].fields_owned - 1, -1, -1):  # loop backwards so that removals don't break anything
                        if self.patchesArr[self.householdArr[i].fields_coord[k][0]][self.householdArr[i].fields_coord[k][1]].owned is False:
                            self.householdArr[i].fields_owned -= 1
                            self.householdArr[i].fields_coord[k] = 0
                            self.householdArr[i].fields_coord.remove(0)

        # on generational changeover, resets its count and recalculates ambition and competence
        def generational_changeover(self):
            for i in range(len(self.householdArr)):
                self.householdArr[i].generation_countdown -= 1
                if self.mode.get() != 1:
                    self.householdArr[i].exploration -= self.expReduce.get()
                    if self.householdArr[i].exploration < 0:
                        self.householdArr[i].exploration = 0
                if self.householdArr[i].generation_countdown <= 0:
                    # Reset generational countdown of household
                    self.householdArr[i].generation_countdown = random.randint(1, 5) + 10
                    # Recalculate household ambition
                    ambitionChange = random.uniform(0, self.genVar.get())
                    decreaseChance = random.uniform(0, 1)
                    if decreaseChance < 0.5:
                        ambitionChange = ambitionChange * (-1)
                    newAmbition = self.householdArr[i].ambition + ambitionChange
                    while (newAmbition > 1) or (newAmbition < self.minAm.get()):
                        ambitionChange = random.uniform(0, self.genVar.get())
                        decreaseChance = random.uniform(0, 1)
                        if decreaseChance < 0.5:
                            ambitionChange = ambitionChange * (-1)
                        newAmbition = self.householdArr[i].ambition + ambitionChange
                    self.householdArr[i].ambition = newAmbition
                    # Recalculate household competence
                    competenceChange = random.uniform(0, self.genVar.get())
                    decreaseChance = random.uniform(0, 1)
                    if decreaseChance < 0.5:
                        competenceChange = competenceChange * (-1)
                    newCompetence = self.householdArr[i].competency + competenceChange
                    while (newCompetence > 1) or (newCompetence < self.minComp.get()):
                        competenceChange = random.uniform(0, self.genVar.get())
                        decreaseChance = random.uniform(0, 1)
                        if decreaseChance < 0.5:
                            competenceChange = competenceChange * (-1)
                        newCompetence = self.householdArr[i].competency + competenceChange
                    self.householdArr[i].competency = newCompetence
                    # Recalculate household exploration
                    if self.mode.get() != 1:
                        exploreChange = random.uniform(0, self.genVar.get())
                        decreaseChance = random.uniform(0, 1)
                        if decreaseChance < 0.5:
                            exploreChange = exploreChange * (-1)
                        newExplore = self.householdArr[i].exploration + exploreChange
                        while (newExplore > 1):
                            exploreChange = random.uniform(0, self.genVar.get())
                            decreaseChance = random.uniform(0, 1)
                            if decreaseChance < 0.5:
                                exploreChange = exploreChange * (-1)
                            newExplore = self.householdArr[i].exploration + exploreChange
                        self.householdArr[i].exploration = newExplore
                        if self.householdArr[i].exploration < 0:
                            self.householdArr[i].exploration = 0

        # ;allows for population maintenance as households 'die', simulating a movement of workers from failed households to more successful households
        # ;as well as more natural population increase (higher birth-rate vs death-rate)
        # ;but to keep the overall population density and growth to within reasonable limits that correlate with those projected by historians and archaeologists,
        # ;who reconstruct a less than .1% annual population growth for Egypt in the predynastic.
        # ;since the landscape abstracted here represents the more fertile parts of ancient egypt,
        # ;one might expect greater growth here than the average for all of Egypt, which is why the equation below allows a cushion of 2 * the pop-growth-rate parameter.
        def population_shift(self):
            startingPopulation = self.startHouseholds.get() * self.startWorkers.get()
            for i in range(len(self.householdArr)):
                populateChance = random.uniform(0, 1)
                if (populateChance < self.householdArr[i].ambition * self.householdArr[i].competency) and (self.householdArr[i].grain > (self.householdArr[i].workers * self.workerRation)) and (self.globalsVars.total_population < (startingPopulation * (1 + 2 * (self.popGR.get() / 100)) ** self.years)):
                    self.householdArr[i].workers += 1
                    self.patchesArr[self.householdArr[i].position_x][self.householdArr[i].position_y].population += 1

        # Updates values that got added to line graphs
        def update_plot_values(self):
            self.globalsVars.surplus = 0
            self.globalsVars.total_households = 0
            self.globalsVars.total_population = 0
            self.globalsVars.populations = []
            self.globalsVars.grains = []
            totalAmbition = 0
            totalCompetence = 0
            totalExplore = 0
            startingPopulation = self.startHouseholds.get() * self.startWorkers.get()
            sortedWealths = []
            self.globalsVars.projected_historical_population = startingPopulation * (1.001) ** self.years  # ; to compare with archaelogical estimates of population growth for this period
            for i in range(len(self.householdArr)):
                self.globalsVars.surplus += self.householdArr[i].grain
                self.globalsVars.total_households += 1
                self.globalsVars.total_population += self.householdArr[i].workers
                totalAmbition += self.householdArr[i].ambition
                totalCompetence += self.householdArr[i].competency
                totalExplore += self.householdArr[i].exploration
                sortedWealths.append(self.householdArr[i].grain)
                self.globalsVars.populations.append(self.householdArr[i].workers)
                self.globalsVars.grains.append(self.householdArr[i].grain)
            if self.globalsVars.total_households > 0:
                self.globalsVars.avg_ambition = totalAmbition / self.globalsVars.total_households
                self.globalsVars.avg_competency = totalCompetence / self.globalsVars.total_households
                self.globalsVars.avg_explore = totalExplore / self.globalsVars.total_households
            # Calculate Lorentz Points and Gini Index Reserve
            sortedWealths.sort()
            wealthSum = 0
            self.globalsVars.gini_index_reserve = 0.0
            self.globalsVars.lorenz_points = []
            for i in range(self.globalsVars.total_households):
                wealthSum = wealthSum + sortedWealths[i]
                if self.globalsVars.surplus > 0:
                    self.globalsVars.lorenz_points.append((wealthSum / self.globalsVars.surplus) * 100)
                    self.globalsVars.gini_index_reserve = self.globalsVars.gini_index_reserve + ((i + 1) / self.globalsVars.total_households) - (wealthSum / self.globalsVars.surplus)

        # Outputs global variables to .csv file for easy analysis
        def output_globals(self):
            line = [(self.years+1), self.globalsVars.surplus, self.globalsVars.total_households, self.globalsVars.total_population, self.globalsVars.projected_historical_population, self.globalsVars.avg_ambition,  self.globalsVars.avg_competency, self.globalsVars.avg_explore, self.globalsVars.gini_index_reserve, self.globalsVars.populations, self.globalsVars.grains]
            print(self.globalsVars.populations)
            self.globalsVars.output_lines.append(line)
            with open('output.csv', 'w') as writeFile:
                writer = csv.writer(writeFile)
                writer.writerows(self.globalsVars.output_lines)
            writeFile.close()

# --------------------------- Model methods end here here ---------------------------



#THIS NEEDS TO BE AT BOTTOM
root = Tk()
root.title("Egypt")
#root.geometry("600x200")

app = App(root)
8
root.mainloop()