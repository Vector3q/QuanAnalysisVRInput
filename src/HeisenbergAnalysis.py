import os
import json
import matplotlib.pyplot as plt

data_folders = [ 
    '../data\Heisenberg\P1\ControllerTracking/Study1_ISO_Test_Varied_TargetSize'
    
]

# '../data/Heisenberg/P1/BareHandIntenSelect/Study1_ISO_Test_Varied_Distance',

click_count = 0
total_error_count = 0
heisenberg_error_count = 0


for data_folder in data_folders:
    print(f"\nAnalyzing file folder: {data_folder}")

    for filename in os.listdir(data_folder):
        if filename.endswith('.json'):
            json_path = os.path.join(data_folder, filename)
            
            with open(json_path, 'r') as f:
                data = json.load(f)

            print(f"\n-------    Experiment Data in {filename}   -------\n")
            total_error_count_in_trial = 0
            heisenberg_error_count_in_trial = 0

            click_count += len(data['selectionSequence'])
            for i, selection in enumerate(data['selectionSequence'], 1):
                
                if selection['isCorrect'] == False:
                    
                    total_error_count_in_trial += 1
                    history_caches = selection['historyCaches']
                    middle_index = len(history_caches) // 2

                    if history_caches[middle_index]['intendedObjectID'] == selection['targetPointID']:
                        print(f"Selection {i}: Target in start: {history_caches[middle_index]['intendedObjectID']}        Target in end: {selection['selectedPointID']}")
                        heisenberg_error_count_in_trial += 1

            total_error_count += total_error_count_in_trial
            heisenberg_error_count += heisenberg_error_count_in_trial

            print(f"Error count: {total_error_count_in_trial}, Heisenberg error count {heisenberg_error_count_in_trial}")

print(f"\n")
print(f"Total click count: {click_count}")
print(f"Total error count: {total_error_count}")
print(f"Heisenberg error count: {heisenberg_error_count}")
print(f"Heisenberg error in total error: {heisenberg_error_count / total_error_count}")
print(f"Heisenberg error rate: {heisenberg_error_count / click_count}")