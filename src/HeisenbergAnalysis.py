import os
import json
import matplotlib.pyplot as plt
import argparse
import math

FOLDER_ABBREVIATIONS = {
    'ControllerTracking': 'DC',
    'ControllerIntenSelect': 'SC',
    'BareHandTracking': 'DH',
    'BareHandIntenSelect': 'SH'
}
ABBREV_TO_FULL = {v: k for k, v in FOLDER_ABBREVIATIONS.items()}

parser = argparse.ArgumentParser(description='analyze the distribution of endPoint')
parser.add_argument('--folder', type=str, required=True, help='folder to be analyzed')
parser.add_argument('--radius', type=float, required=True, default=0, help='target radius')

args = parser.parse_args()
target_radius = args.radius

full_name = ABBREV_TO_FULL.get(args.folder, args.folder)
abbrev_name = FOLDER_ABBREVIATIONS.get(full_name, full_name)

data_folders = [
    f'../data\Heisenberg\P1\{full_name}/Study1_ISO_Test_Varied_TargetSize'
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

            if target_radius != 0 and data['radius'] != target_radius:
                continue;
            
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
print(f"Total error rate: {total_error_count/click_count:.2%}")
print(f"Heisenberg error rate: {heisenberg_error_count/click_count:.2%}")
print(f"Heisenberg error in total error: {heisenberg_error_count/total_error_count:.2%}")