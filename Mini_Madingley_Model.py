
# coding: utf-8

# # The Madingley Model

# ## Import

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
from random import shuffle
import copy
import time


# ## Class Definitions

# In[2]:


class Herbivorous:
    '''Groups the specific parameters for a herbivore cohort'''
    def __init__(self, assimilation_efficiency, hunting_rate):
        self.assimilation_efficiency = assimilation_efficiency
        self.hunting_rate = hunting_rate


# In[3]:


class Carnivorous:
    '''Groups the specific parameters for a carnivore cohort'''
    def __init__(self, assimilation_efficiency, hunting_rate):
        self.assimilation_efficiency = assimilation_efficiency
        self.hunting_rate = hunting_rate   


# In[4]:


class Cohort:
    '''Groups the parameters for a cohort'''
    def __init__(self, alive, diet, birth_m, maturity_m, assimilation_efficiency, hunting_rate, N, m, reproductive_m, max_m, maturity, maturity_age, position):
        self.alive = alive
        self.diet = diet
        self.birth_m = birth_m
        self.maturity_m = maturity_m
        if diet == 'herbivore':
            self.herbivorous = Herbivorous(assimilation_efficiency, hunting_rate)   
        elif diet == 'carnivore':
            self.carnivorous = Carnivorous(assimilation_efficiency, hunting_rate)
        self.N = N
        self.m = m
        self.reproductive_m = reproductive_m
        self.max_m = max_m
        self.maturity = maturity
        self.maturity_age = maturity_age
        self.position = position


# ## Initial Functions

# In[5]:


def initial_grid_location(width, length):
    '''creates a nested list of lists'''
    grid_location = [[[] for l in range(length)] for w in range(width)]
    return(grid_location)


# In[6]:


def initial_grid_grass(width, length, grass_amount):
    '''creates a grid of amounts of grass'''
    initial_grass_amount = float(grass_amount)
    grid_grass = np.array([[initial_grass_amount for l in range(length)] for w in range(width)])
    return(grid_grass)


# In[7]:


def initial_objects(width, length, grass_amount):
    cohort_list = []
    grid_location = initial_grid_location(width, length)
    grid_grass = initial_grid_grass(width, length, grass_amount)
    return(cohort_list, grid_location, grid_grass)


# In[8]:


def add_rabbit(cohort_list, grid_location):
    '''adds a rabbit cohort to a given cell'''
    position = [np.random.randint(0,width), np.random.randint(0,length)]
    new = Cohort(True, 'herbivore', 0.4, 4, 0.7, 10 ** (-4), 90, 2, 0, 2, False, 0, position)
    start_index = len(cohort_list)
    cohort_list.append(new)
    grid_location[position[0]][position[1]].append(start_index)
    return(cohort_list, grid_location)
    
def add_fox(cohort_list, grid_location):
    '''adds a fox cohort to a given cell'''
    position = [np.random.randint(0,width), np.random.randint(0,length)]
    new = Cohort(True, 'carnivore', 1, 10, 0.64, 10 ** (-7), 30, 6, 0, 6, False, 0, position)
    #new = Cohort('carnivore', 6, 25, 30, 0.64, 1, position)
    start_index = len(cohort_list)
    cohort_list.append(new)
    grid_location[position[0]][position[1]].append(start_index)
    return(cohort_list, grid_location)

def add_multiple(cohort_list, grid_location, taxonomy, number_of_cohorts):
    '''repeatedly adds cohorts to a given cell'''
    if taxonomy == 'rabbit':
        for i in range(number_of_cohorts):
            cohort_list, grid_location = add_rabbit(cohort_list, grid_location)
    elif taxonomy == 'fox':
        for i in range(number_of_cohorts):
            cohort_list, grid_location = add_fox(cohort_list, grid_location)
    return(cohort_list, grid_location)


# ## Mechanistic Functions

# In[9]:


def herbivore_eating(grid_grass_cell, cohort):
    '''carries out the eating of a herbivore cohort'''
    hunting = cohort.herbivorous.hunting_rate * cohort.m
    available_stock = grid_grass_cell
    F = (hunting * available_stock ** 2) / (1 + hunting * available_stock ** 2)
    amount_eaten_perN = available_stock * (1 - np.exp(-F))
    amount_eaten = amount_eaten_perN * cohort.N
    if amount_eaten > available_stock:
        amount_eaten = available_stock
        amount_eaten_perN = amount_eaten / cohort.N    
    new_mass_herbivation = cohort.m + amount_eaten_perN * cohort.herbivorous.assimilation_efficiency
    grid_grass_cell = available_stock - amount_eaten
    return(grid_grass_cell, new_mass_herbivation)


# In[10]:


def carnivore_eating(available_prey_indices, cohort_list, cohort):
    '''carries out eating of a carnivore cohort'''
    before_mass = cohort.m
    ## Pull up values
    hunting = cohort.carnivorous.hunting_rate * cohort.m
    mN_predation_total = 0
    divisor = 1
    for l in available_prey_indices:        
        divisor = divisor + hunting * cohort_list[l].N ** 2
    amount_eaten = 0
    delta_Ns = []
    for l in available_prey_indices:
        F = (hunting * cohort_list[l].N ** 2) / divisor
        print(F, 'CHECK THIS IS LESS THAN 1')
        N_predation_perN = cohort_list[l].N * (1 - np.exp(-F))
        N_predation = N_predation_perN * cohort.N
        if N_predation > cohort_list[l].N:
            N_predation = cohort_list[l].N
        delta_Ns.append(N_predation)
        mN_predation = cohort_list[l].m * N_predation
        mN_predation_total = mN_predation_total + mN_predation
    new_carnivore_m = cohort.m + (mN_predation_total * cohort.carnivorous.assimilation_efficiency)
    after_mass = new_carnivore_m
    change_mass = after_mass - before_mass
    if change_mass < 0:
        print('Error:', 'carnivore eating caused a loss of weight')  
    return(delta_Ns, new_carnivore_m)


# In[11]:


def metabolising(cohort):
    '''carries out metabolising of a cohort'''
    # Need a proper value for rate
    rate = 0.1
    if cohort.m <= 0:
        if cohort.m < 0:
            print('Error:', 'mass less than 0!', 'apfpisadhpifhapdngpiegnpinagpanpnfdpiaunbpiabipbianfdpignifdiapbgipabdipgbpdiuvhpiadhpvhdfigggggggggggggggggggggggggggggggggggggggg')
        metabolise_mass = 0
    else:
        metabolise_mass = rate * cohort.m ** (3/4)
    new_mass = cohort.m - metabolise_mass
    if new_mass < 0:
        new_mass = 0
    return(new_mass)


# In[12]:


def aging(cohort):
    '''carries out aging of a cohort'''
    new_age = cohort.maturity_age + 1
    return(new_age)


# In[13]:


def dying(cohort):
    '''carries out dying of a cohort'''
    deaths = 0.05 * cohort.N
    new_N = cohort.N - deaths
    return(new_N)


# In[14]:


def reproducing(cohort):
    '''carries out reproducing of a cohort'''
    juvenile_cohort = copy.deepcopy(cohort)
    if juvenile_cohort.alive == False:
        print('Error:', 'dead juvenile alert!!')
    available_m = cohort.reproductive_m * cohort.N
    juvenile_cohort.N = available_m / cohort.birth_m
    juvenile_cohort.m = juvenile_cohort.birth_m
    juvenile_cohort.reproductive_m = 0
    juvenile_cohort.max_m = juvenile_cohort.m
    juvenile_cohort.maturity = False
    if juvenile_cohort.N == 0:
        print('Error:', 'zero juvenile N')
    return(juvenile_cohort)


# In[15]:


def moving(next_grid_location, acting_index, cohort):
    '''carries out moving of a cohort'''
    next_grid_location[cohort.position[0]][cohort.position[1]].remove(acting_index)
    new_position = [0,0]
    new_position[0] = (cohort.position[0] + int(np.random.uniform(-0.25,1.25))) % length
    new_position[1] = (cohort.position[1] + int(np.random.uniform(-0.25,1.25))) % width
    next_grid_location[new_position[0]][new_position[1]].append(acting_index)
    return(new_position)


# ## Efficiency Functions

# In[16]:


def list_cleaner(cohort_list, grid_location):
    '''removes dead cohorts from cohort_list'''
    new_cohort_list = []
    new_grid_location = initial_grid_location(width,length)
    range(len(cohort_list))
    cleaner_counter = 0
    for i in range(len(cohort_list)):
        if cohort_list[i].alive == True:
            add_pos = cohort_list[i].position
            new_cohort_list.append(cohort_list[i])
            new_grid_location[add_pos[0]][add_pos[1]].append(cleaner_counter)
            cleaner_counter = cleaner_counter + 1
    return(new_cohort_list, new_grid_location)


# ## Analytic Functions

# In[17]:


def total_mass_calc(cohort_list):
    '''calculates the total mass in the cohort_list including reproductive mass'''
    total_mass = 0
    for i in range(len(cohort_list)):
        if cohort_list[i].alive == True:
            total_mass = total_mass + cohort_list[i].m * cohort_list[i].N + cohort_list[i].reproductive_m
    return(total_mass)


# ## Timestep & Tests

# In[18]:


def timestep(cohort_list, grid_location, grid_grass):
    '''one full timestep of the model'''
    next_grid_location = copy.deepcopy(grid_location)
    x = [j for j in range(len(cohort_list))]
    shuffle(x)
    for acting_index in x:
        print('total_mass =', total_mass_calc(cohort_list))
        acting_cohort = cohort_list[acting_index]
        pos = acting_cohort.position
        
        if acting_cohort.alive == True:
            
            # Eating
            if acting_cohort.alive == True:
                if acting_cohort.diet == 'herbivore':
                    grid_grass[pos[0],pos[1]], acting_cohort.m = herbivore_eating(grid_grass[pos[0]][pos[1]], acting_cohort)

                elif acting_cohort.diet == 'carnivore':
                    print('before predation total_mass =', total_mass_calc(cohort_list))
                    grid_copy = copy.deepcopy(grid_location)
                    available_prey_indices = grid_copy[pos[0]][pos[1]]
                    for i2 in available_prey_indices:
                        if cohort_list[i2].alive == False:
                            available_prey_indices.remove(i2)
                    #print('grid_location', grid_copy, ' ', 'available_prey_indices', available_prey_indices, ' ', 'acting_index', acting_index)
                    available_prey_indices.remove(acting_index)
                    if len(available_prey_indices) > 0:
                        print('carnivore eating occuring')
                        delta_Ns, acting_cohort.m = carnivore_eating(available_prey_indices, cohort_list, acting_cohort)
                        k_to_index = 0
                        print('in between', total_mass_calc(cohort_list))
                        for k in available_prey_indices:
                            print('delta_Ns', delta_Ns)
                            cohort_list[k].N = cohort_list[k].N - delta_Ns[k_to_index]
                            if cohort_list[k].N < 1:
                                cohort_list[k].alive = False
                                cohort_list[k].N = 0
                            k_to_index = k_to_index + 1
                    print('after predation total_mass =', total_mass_calc(cohort_list))
                            
                if acting_cohort.m >= acting_cohort.maturity_m:
                    if acting_cohort.maturity == False:
                        acting_cohort.maturity = True
                        acting_cohort.maturity_age = 0
                    acting_cohort.reproductive_m = acting_cohort.reproductive_m + acting_cohort.m - acting_cohort.maturity_m
                    acting_cohort.m = acting_cohort.maturity_m
                    
                if acting_cohort.m > acting_cohort.max_m:
                    acting_cohort.max_m = acting_cohort.m

            # Metabolism
            #if acting_cohort.alive == True:
                #acting_cohort.m = metabolising(acting_cohort)

            # Aging
            if acting_cohort.alive == True:
                if acting_cohort.maturity == True:
                    acting_cohort.maturity_age = aging(acting_cohort)

            # Dying
            if acting_cohort.alive == True:
                acting_cohort.N = dying(acting_cohort)
            
            #Zeroing
            if acting_cohort.alive == True:
                if acting_cohort.N < 1:
                    acting_cohort.alive = False
                    acting_cohort.N = 0

                if acting_cohort.m == 0:
                    acting_cohort.alive = False
                    acting_cohort.N = 0

            # Reproducing
            if acting_cohort.alive == True:
                if (acting_cohort.m + acting_cohort.reproductive_m) / acting_cohort.maturity_m > 1.5:
                    print('heeeeere is reproduction', acting_cohort.m, acting_cohort.reproductive_m, acting_cohort.maturity_m)
                    grid_location[pos[0]][pos[1]].append(len(cohort_list))
                    next_grid_location[pos[0]][pos[1]].append(len(cohort_list))
                    cohort_list.append(reproducing(acting_cohort))
                    acting_cohort.reproductive_m = 0

            # Moving
            if acting_cohort.alive == True:
                acting_cohort.position = moving(next_grid_location, acting_index, acting_cohort)
    
    print('grid_location', grid_location)
    print('next_grid_location', next_grid_location)
    grid_location = next_grid_location
    grid_grass = grid_grass + 2           
    return(cohort_list, grid_location, grid_grass)


# In[19]:


def test1(test_timesteps):
    '''runs the model for a given number of timesteps starting at initial conditions'''
    cohort_list, grid_location, grid_grass = initial_objects(width, length, grass_amount)
    cohort_list, grid_location = add_multiple(cohort_list, grid_location, 'rabbit', 0)
    cohort_list, grid_location = add_multiple(cohort_list, grid_location, 'fox', 3)
    print('test1 initial lineup is ', 'number_of_cohorts =', len(cohort_list), ' ',grid_location)    
    for itest in range(test_timesteps):
        cohort_list, grid_location, grid_grass = timestep(cohort_list, grid_location, grid_grass)
        print(grid_location, 'before_cleaning')
        cohort_list, grid_location = list_cleaner(cohort_list, grid_location)
        print(grid_location, 'after_cleaning')
        for jtest in range(len(cohort_list)):
            if cohort_list[jtest].alive == True:
                1
                #print('index =', jtest, cohort_list[jtest].m, cohort_list[jtest].N, cohort_list[jtest].reproductive_m, cohort_list[jtest].diet)
    print('test1 final lineup is   ', 'number_of_cohorts =', len(cohort_list), ' ', grid_location)    
    return(cohort_list, grid_location, grid_grass)


# In[20]:


def test2(test_timesteps, cohort_list, grid_location, grid_grass):
    '''runs the model for a given number of timesteps continuing from the current point'''  
    for itest in range(test_timesteps):
        cohort_list, grid_location, grid_grass = timestep(cohort_list, grid_location, grid_grass)
        cohort_list, grid_location = list_cleaner(cohort_list, grid_location)
        print('number_of_cohorts =', len(cohort_list), ' ', grid_location)
        for jtest in range(len(cohort_list)):
            if cohort_list[jtest].alive == True:
                1
                print('index =', jtest, cohort_list[jtest].m, cohort_list[jtest].N, cohort_list[jtest].reproductive_m, cohort_list[jtest].diet)
        print('')
    print('test2 final linesup is  ', 'number_of_cohorts =', len(cohort_list), ' ', grid_location)    
    return(cohort_list, grid_location, grid_grass)


# ## Starting the program

# In[68]:


width = 1
length = 1
grass_amount = 5.0


# In[70]:


cohort_list, grid_location, grid_grass = test1(0)
cohort_list, grid_location, grid_grass = test2(1, cohort_list, grid_location, grid_grass)
print('total_mass =', total_mass_calc(cohort_list))


# In[36]:


y = np.zeros(10)
x = np.array(list(range(10)))
x = x + 1
print(x)
print(y)
2.85883049389e+14


# In[37]:


y[0] = 540
y[1] = 823
y[2] = 56000
y[3] = 210441054
y[4] = 677701487616
y[5] = 2.85883049389e+14
y[6] = 1.09386011754e+27
y[7] = 1.76557080048e+41
y[8] = 2.70727325316e+55
y[9] = 3.943688943e+69


# In[38]:


np.log(np.exp(1))


# In[45]:


X = np.array(x)
Y = np.log(np.log10(np.array(y)))
plt.plot(X,Y)
plt.show()


# In[436]:


for i in range(len(cohort_list)):
    print(cohort_list[i].alive, cohort_list[i].diet)


# In[24]:


# The initial conditions
width = 2
length = 2
cohort_list, grid_location, grid_grass = initial_objects(width, length, grass_amount)
cohort_list, grid_location = add_multiple(cohort_list, grid_location, 'rabbit', 2)
cohort_list, grid_location = add_multiple(cohort_list, grid_location, 'fox', 2)
print('number_of_cohorts =', len(cohort_list), ' ',grid_location)


# In[25]:


# Chic version
timesteps_total = 1000
total_time_start = time.time()
cohort_list, grid_location, grid_grass = initial_objects(width, length, initial_grass_amount)
cohort_list, grid_location = add_multiple(cohort_list, grid_location, 'rabbit', 16)
cohort_list, grid_location = add_multiple(cohort_list, grid_location, 'fox', 1)
for m in range(timesteps_total):
    if m % 50 == 0:
        cohort_list, grid_location = list_cleaner(cohort_list, grid_location)  
    if m % 1000 == 0:
        print('multiple of 1000 =', m)
        how_many_alive = 0
        for i in range(len(cohort_list)):
            if cohort_list[i].alive == True:
                how_many_alive = how_many_alive + 1
        print('how_many_alive =', how_many_alive)
        if how_many_alive == 0:
            print('all_dead!')
            break     
    cohort_list, grid_location, grid_grass = timestep(cohort_list, grid_location, grid_grass)
for i in range(len(cohort_list)):
    if cohort_list[i].alive == True:
        print('index =', i, cohort_list[i].m, cohort_list[i].N, cohort_list[i].reproductive_m, cohort_list[i].diet, cohort_list[i].alive)       
total_time_end = time.time()
total_time = total_time_end - total_time_start
print('total time to run =', total_time)


# In[26]:


# Practice version
timesteps_total = 5000
total_time_start = time.time()
x = []
y = []
vector = np.array(timesteps_total)
cohort_list, grid_location, grid_grass = initial_objects(width, length, initial_grass_amount)
cohort_list, grid_location = add_multiple(cohort_list, grid_location, 'rabbit', 4)
cohort_list, grid_location = add_multiple(cohort_list, grid_location, 'fox', 0)
for m in range(timesteps_total):
    #print('m', m)   
    if m % 50 == 1:
        print('before', len(cohort_list))
        cohort_list, grid_location = list_cleaner(cohort_list, grid_location)
        print('after', len(cohort_list))
        
    if m % 1000 == 0:
        print('multiple of 1000', m)
        x.append(m)
        how_many_alive = 0
        for i in range(len(cohort_list)):
            if cohort_list[i].alive == True:
                how_many_alive = how_many_alive + 1
        print('how_many_alive', how_many_alive, 'len(cohort_list)', len(cohort_list))
        if how_many_alive == 0:
            print('all_dead!')
            break
        time_start = time.time()            
    cohort_list, grid_location, grid_grass = timestep(cohort_list, grid_location, grid_grass)
    #for i in range(len(cohort_list)):
        #if cohort_list[i].alive == True:
        #if 0 == 0:
            #print('index =', i, cohort_list[i].m, cohort_list[i].N, cohort_list[i].reproductive_m, cohort_list[i].diet, cohort_list[i].alive)    
    if m % 1000 == 100:
        time_end = time.time()
        timestep_time = time_end - time_start
        y.append(timestep_time)
        print(timestep_time, 'timestep_time')
cohort_list, grid_location, grid_grass = timestep(cohort_list, grid_location, grid_grass)
for i in range(len(cohort_list)):
    if cohort_list[i].alive == True:
    #if 0 == 0:
        print('index =', i, cohort_list[i].m, cohort_list[i].N, cohort_list[i].reproductive_m, cohort_list[i].diet, cohort_list[i].alive)       
total_time_end = time.time()
total_time = total_time_end - total_time_start
print('total time to run =', total_time)

