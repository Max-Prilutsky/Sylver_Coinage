import argparse
from distutils.util import strtobool
import json
import copy
import time
import traceback
import numpy as np
import logging

def parse_args():
    """
    Helper function for parsing the passed in arguments for the script.
    """
    parser = argparse.ArgumentParser()    
    parser.add_argument("-p", "--prune", type=strtobool, default=False, help="Determines whether the dictionary propogation will use pruning or not. By default set to False, so there is no pruning.") 
    parser.add_argument("-n", "--positionsize", type=int, default=10, help="The largest size position to be recorded in the endgame dictionary.") 
    parser.add_argument("-s", "--save", type=strtobool, default=True, help="Determines whether or not to save the resulting calculated dictionary. By default set to True, so that the results will be saved.") 
    args = parser.parse_args()

    logging.info(f"Parsed Input Args: {args}")
    return args

def minimalGeneratorsFromGaps(gaps : list):
    conductor = max(gaps) + 1
    part_of_semigroup = [i for i in range(0, 2*conductor) if(i not in gaps)] # Getting a subsection of the semigroup that includes all the Apery Set
    multiplicity = min(part_of_semigroup[1:]) # The first element in the semigroup is 0 so we ignore it
    minimal_generators = [multiplicity]
    for modular_class in range(1, multiplicity):
        for test_element in part_of_semigroup:
            if(test_element%multiplicity==modular_class):
                is_generator = True
                for element in part_of_semigroup[1:]: # Once again we ignore 0
                    if(test_element - element <= 0):
                        break
                    else:
                        if((test_element - element) in part_of_semigroup):
                            is_generator = False
                            break
                if(is_generator):
                    minimal_generators.append(test_element)
                break
    return minimal_generators

def positionAfterPlayingMove(gaps : list, move : int):
    part_of_semigroup = [element for element in range(max(gaps)) if element not in gaps]
    not_in_new_gaps = []
    for gap in gaps:
        for element in part_of_semigroup:
            if(gap - element < 0):
                break
            else:
                if((gap-element)%move == 0):
                    not_in_new_gaps.append(gap)
                    break
    return [gap for gap in gaps if(gap not in not_in_new_gaps)]

def addNewSetOfPositions(basePosition : list, inputDic : dict, prunedDic : dict, prune : bool = False):
    # basePosition = T
    newPositions = []
    right_gens = [gen for gen in minimalGeneratorsFromGaps(basePosition) if(gen > max(basePosition))]
    if(prune):
        winning_gens = None
        if(inputDic[str(basePosition)][0] == "W"):
            winning_move = inputDic[str(basePosition)][1] # g
            winning_position = positionAfterPlayingMove(basePosition, winning_move) # gaps(S)
            winning_gens = minimalGeneratorsFromGaps(winning_position) # gens(S)
    for gen in right_gens: # Note, gen is min(gaps(T')\gaps(T))
        newPosition = basePosition + [gen] # T'
        if((prune) and (winning_gens) and (gen > max(winning_gens))): # if g > max(gens(S)) then we can prune
            prunedDic[str(newPosition)] = winning_move
        else:
            if(inputDic[str(basePosition)][0] == 'L'):
                inputDic[str(newPosition)] = ["W", gen]
            else:
                losing = True
                for move in newPosition:
                    if move > 1:
                        trial = positionAfterPlayingMove(newPosition, move)
                        if(str(trial) in inputDic):
                            if(inputDic[str(trial)][0] == 'L'):
                                losing = False
                                inputDic[str(newPosition)] = ["W", move]
                                break

                if losing:
                    inputDic[str(newPosition)] = ['L']

            newPositions.append(newPosition)
    
    return newPositions

def updatedEndGameBuilder(dictionary : dict, start : int = 1, n : int = 20, prune : bool = False, save_results : bool = True):
    if(prune):
        saveTo = "endgame_pruned_trial.json"
        prunedDicLoc = "pruned.json"
    else:
        saveTo = "endgame_trial.json"
    dic = copy.deepcopy(dictionary)
    prunedDic = {}
    newPositions = [[1]]
    start_time = time.perf_counter()
    for i in range(start, n + 1):
        timer = time.perf_counter()
        generatedList = list(newPositions)  # [j for j in dic['Documented'] if (len(j) == i)]
        newPositions = []
        for base in generatedList:
            temp = addNewSetOfPositions(base, dic, prunedDic, prune=prune)
            newPositions += temp
        if(prune):
            print(f"Finished positions up to size {i+1}. This took {time.perf_counter() - timer} seconds and we have {len(dic)} positions recorded. We have pruned {len(prunedDic)} positions. Total Time: {time.perf_counter() - start_time}")
        else:
            print(f"{i+1}; {time.perf_counter() - timer}")
            #print(f"Finished positions up to size {i+1}. This took {time.perf_counter() - timer} seconds and we have {len(dic)} positions recorded. Total Time: {time.perf_counter() - start_time}")
        if(save_results and (i == n)): 
            with open(saveTo, 'w') as f:
                json.dump(dic, f)
            if(prune):
                with open(prunedDicLoc, 'w') as f2:
                    json.dump(prunedDic, f2)
    return dic

if __name__ == '__main__':
    
    args = parse_args()
    print(args)
    endgame = {
        '[1]' : ['L']
    }
    try:
        resolvedDic = updatedEndGameBuilder(endgame, 1, n=14, prune=args.prune, save_results=args.save)
    except KeyboardInterrupt:
        print('problem #TODO fix this')
    except Exception as e:
        print(traceback.format_exc())
        print(str(e))