import requests
import time 
class SylverUser():
    def __init__(self, username):
        self.username = username
        #self.endpoint = "http://10.0.0.54:8000"
        self.endpoint = "http://127.0.0.1:8000"
        dic_response = requests.get(f"{self.endpoint}/dictionary")
        if dic_response.status_code == 200:
            self.recorded_results = dic_response.json()
        else:
            raise Exception(f"Failed to get dictionary receieved status code {dic_response.status_code}")
        pos_response = requests.get(f"{self.endpoint}/new_positions")
        if pos_response.status_code == 200:
            pos_json = pos_response.json()
            self.position = pos_json['position']
            self.position_result = pos_json['result']
        else:
            raise Exception(f"Failed to get new position receieved status code {pos_response.status_code}")
        self.current_queue_position_size = len(self.position)
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
                        trial = str(self.positionAfterPlayingMove(new_position, move))
                        if(trial in self.recorded_results):
                            if(eval(self.recorded_results[trial][0]) == "L"):
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
    
    def updateDatabase(self):
        while(True):
            data = self.addNewSetOfPositions()
            API_response = requests.post(f"{self.endpoint}/dictionary", json = data)
            if(API_response.status_code == 200):
                json_response = API_response.json()
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
            if(len(self.position) > self.current_queue_position_size):
                print(len(self.position))
                dic_response = requests.get(f"{self.endpoint}/dictionary")
                if dic_response.status_code == 200:
                    self.recorded_results = dic_response.json()
                else:
                    raise Exception(f"Failed to get dictionary receieved status code {dic_response.status_code}")
                self.current_queue_position_size = len(self.position)
           