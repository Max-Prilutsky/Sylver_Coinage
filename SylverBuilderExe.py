import re
import traceback
from datetime import datetime
import requests
import time 

class SylverUser():
    def __init__(self, username):
        self.username = username
        #self.endpoint = "http://10.0.0.54:8000"
        self.endpoint = "http://127.0.0.1:8000"
        pos_response = requests.get(f"{self.endpoint}/new_positions")
        if pos_response.status_code == 200:
            pos_json = pos_response.json()
            self.position = pos_json['position']
            self.position_result = pos_json['result']
        else:
            raise Exception(f"Failed to get new position receieved status code {pos_response.status_code}")
        self.positions_added_to_database = 0
        
    def minimalGeneratorsFromGaps(self, gaps):
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
    
    def positionAfterPlayingMove(self, gaps, move):
        part_of_semigroup = [element for element in range(max(gaps)) if element not in gaps]
        eliminated_gaps = []
        for gap in gaps:
            for element in part_of_semigroup:
                if(gap - element < 0):
                    break
                else:
                    if((gap-element)%move == 0):
                        eliminated_gaps.append(gap)
                        break
        return [gap for gap in gaps if(gap not in eliminated_gaps)]
    
    def addNewSetOfPositions(self):
        new_positions = {}
        right_gens = [gen for gen in self.minimalGeneratorsFromGaps(self.position) if(gen > max(self.position))]
        for gen in right_gens:
            new_position = self.position + [gen]
            if(self.position_result == ["L"]):
                new_positions[str(new_position)] = ["W", gen]
            else:
                losing = True
                for move in new_position:
                    if move > 1:
                        if move <= 3 and len(new_position) > 3 and new_position[:3] == [1, 2, 3]:
                            continue
                        trial = str(self.positionAfterPlayingMove(new_position, move))
                        trial_request = self.checkPosition(trial)
                        if(eval(trial_request['optimal_move'])[0] == "L"):
                            losing = False
                            new_positions[str(new_position)] = ["W", move]
                            break
                if losing:
                    new_positions[str(new_position)] = ["L"]
        data = {
            "position": self.position,
            "results" : new_positions
        }
        return data
    
    def checkPosition(self, position):
        API_response = requests.post(url = f"{self.endpoint}/look_up", json = {"position": position})
        if(API_response.status_code == 200):
            json_response = API_response.json()
            return json_response[0]
        else:
            raise Exception("Oh no") #
            
    def updateDatabase(self):
        timer = time.perf_counter()
        while(len(self.position) <= 15):
            data = self.addNewSetOfPositions()
            API_response = requests.post(f"{self.endpoint}/dictionary", json = data)
            if(API_response.status_code == 200):
                json_response = API_response.json()
                if len(json_response['position']) > len(self.position):  
                    print(f"{len(self.position)}; {time.perf_counter() - timer}")
                    timer = time.perf_counter()
                self.position = json_response['position']
                self.position_result = json_response['result']
                self.positions_added_to_database += 1
            elif API_response.status_code == 208:
                pos_response = requests.get(f"{self.endpoint}/new_positions")
                if pos_response.status_code == 200:
                    pos_json = pos_response.json()
                    self.position = pos_json['position']
                    self.position_result = pos_json['result']
                else:
                    raise Exception(f"Failed to get new position receieved status code {API_response.status_code}")
            else:
                raise Exception(f"Failed to post new position receieved status code {API_response.status_code}")
        print(f"{len(self.position)}; {time.perf_counter() - timer}")
        
if __name__ == "__main__":
    print("""
Thank you for participating in the building of the Sylver Coinage 
Endgame Dictionary. This program is built to help identify and 
document new Sylver Coinage positions and requires an Internet 
connection in order to work. The program uses some of your 
machine's CPU power to calculate new positions and update a 
centralized database of positions through an API. For additional
information on Sylver Coinage and this program, please visit:
    <website to be added>
    """)
    
    user_name = ""
    while(len(user_name) < 1):
        user_name = input("User Name: ").lower()
        regex = re.compile("[^a-zA-Z ]")
        user_name = regex.sub("", user_name)
    #print(user_name)
    new_user = SylverUser(user_name)
    try:
        new_user.updateDatabase()
        print(new_user.positions_added_to_database)
    except Exception as e:
        print(traceback.format_exc())
        #print(new_user.position)
    except KeyboardInterrupt:
        print(datetime.now())
        want_to_stop = input("\nAre you sure you would like to stop? [Y]/n: ").lower()
        if (want_to_stop in ["n", "no"]):
            new_user.updateDatabase()
            print(datetime.now())
        else:
            print(new_user.position)
            print(f"""
Thank you so much for all your help! You were able to add {new_user.positions_added_to_database} 
positions to the database!
            """)
   