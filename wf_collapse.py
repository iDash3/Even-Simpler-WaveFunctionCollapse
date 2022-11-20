# 
# 
# WAVE FUNCTION COLLAPSE
# 
# 
# Setting up rules
#           Up [0] 
#   Left [1]    Right [3]     
#           Down [2] 

import numpy as np
import pandas as pd
import random

dimensions = [0,0]
options = []
rulebook = []
ocurrances = {}



# Build rule matrix
# -> Could turn this into a Rulebook class with addRule and checkRule
# -> Also, this is checking up,left,right,down and not diagonally
with open("./example.txt", "r") as ff:
    ffr = ff.read()
    content = ffr.split("\n")
    # print(content)
    content = content[:-1]

    # Setting dimensions
    width = dimensions[0] = len(content[0])
    length = dimensions[1] = len(content) 
    print("Input dimensions {}, {}".format(length, width))

    for line_id, line in enumerate(content):
        for c_id, c in enumerate(line):

            if c not in ocurrances.keys():
                ocurrances[c] = 1
            else:
                ocurrances[c] = ocurrances[c] + 1;

            check_idx = [line_id - 1, c_id - 1, line_id + 1, c_id + 1]
            check_if = []

            rules = []
            # Check uppper side
            if line_id - 1 >= 0:
                rule = [c, content[line_id - 1][c_id], 0]
                rules.append(rule)
            # Check left hand side
            if c_id - 1 >= 0:
                rule = [c, line[c_id - 1], 1]
                rules.append(rule)
            # Check down side
            if line_id + 1 < length:
                rule = [c, content[line_id + 1][c_id], 2]
                rules.append(rule)
            # Check right hand side
            if c_id + 1 < width:
                rule = [c, line[c_id + 1], 3]
                rules.append(rule)

            for r in rules:
                if r not in rulebook:
                    rulebook.append(r)

    rulebook = np.array(rulebook)
    options = np.unique(rulebook[:, 0])


def select_random_weighted(options):
    osum = sum([ocurrances[o] for o in options])
    ranges = [ocurrances[o] / osum for o in options]

    rand = random.random()

    correct = ranges[0]
    ssum = 0
    for idx, rang in enumerate(ranges):
        ssum = ssum + rang
        if rand < ssum:
            correct = idx
            break
    print("Correct: {}".format(correct))

    return options[correct]

def select(options):
    ws = [ocurrances[o] for o in options]
    random_option_weigthed = random.choices(options, weights=ws)
    print(options)
    print(ws)
    return random_option_weigthed[0]

def filtered_options(now, direction):
    direction = str(direction)
    specific_rules = np.array([rrule for rrule in rulebook if (rrule[0] == now and rrule[2] == direction)])

    if len(specific_rules) != 0:
        specific_rules = specific_rules[:,1]
    
    return specific_rules

def differential_matrix(m_base, m_extract):
    resm = []
    for i in m_base:
        if i in m_extract:
            resm.append(i)
    return resm



init = False
completed = False
solution_entropy = 1 / len(options)

while completed == False:

    if init == False:
        # Since you already know that all cells have N basic choices, you don't really need a matrix, you can just collapse with the basis vector if there's no rules yet
        print("+" * 10)
        print("Initial Run")
        print(rulebook)
        print("+" * 10)

        res_matrix = [{"collapsed": False, "options": options} for i in range(length * width)]
        i = 0
        init = True
        entropy_m = np.array([len(i["options"])/len(options) for i in res_matrix])

    if len(entropy_m[entropy_m != solution_entropy]) == 0:
        print("----------- DONE ----------")
        completed = True
        break

    current_i = 0
    current_val = 0
    if sum(entropy_m) == width * length:
        print("Complete entropy. Select at random")
        current_i = random.randrange(length*width)
    else:
        new_c = np.where((entropy_m == solution_entropy), 3, entropy_m)
        current_i = np.argmin(new_c)

    inital_collapse = res_matrix[current_i] 
    current_val =  select(inital_collapse["options"]) 
    res_matrix[current_i]["options"] = current_val
    res_matrix[current_i]["collapsed"] = True

    checks = [current_i - width, current_i - 1, current_i + width, current_i + 1]
    checks_if = [checks[0] >= 0, (current_i % width) - 1 >= 0, checks[2] < width * length, (current_i % width) + 1 < width]

    for ci_id, ci in enumerate(checks_if):
        if ci:
            m1 = res_matrix[checks[ci_id]]["options"]
            if len(m1) == 1:
                continue
            m3 = filtered_options(current_val, ci_id)
            dm = differential_matrix(m1, m3)
            res_matrix[checks[ci_id]]["options"] = dm
            if len(dm) == 0:
                print("ZTOP")
                init = False

    entropy_m = np.array([len(i["options"])/len(options) for i in res_matrix])
    num_display_m = np.array([len(i["options"]) for i in res_matrix]).reshape(length,width)
    display_m = np.array(["".join(i["options"]) for i in res_matrix]).reshape(length,width)

    print("-" * 10)
    print(i)
    print(current_i, current_val)
    print(display_m)
    # print(entropy_m.reshape(length, width))
    print("-" * 10)
    i = i + 1

# Save resulting matrix to file
with open("result.txt","w+") as rf:
    for val_id in range(len(res_matrix)):
        rf.write(res_matrix[val_id]["options"][0])

        if (val_id + 1) % width == 0:
            rf.write("\n")
