import os
import json
import matplotlib.pyplot as plt
import argparse
import math

FOLDER_ABBREVIATIONS = {
    'ControllerTracking': 'DC',
    'ControllerIntenSelect': 'BC',
    'BareHandIntenSelect': 'BH',
    'BareHandTracking': 'DH'
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

x_coords = []
y_coords = []

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
            for i, selection in enumerate(data['selectionSequence'], 1):
                
                point = selection['endPointInEnd']
                x_coords.append(point[0])
                y_coords.append(point[1])

plt.figure(figsize=(6, 6))
plt.scatter(x_coords, y_coords, c='green', marker='o', alpha=0.3)

target_distance = 0.75
number_of_targets = 13
angle_step = 360 / number_of_targets


for i in range(number_of_targets):
    angle = i * angle_step
    x = target_distance * math.cos(math.radians(angle))
    y = target_distance * math.sin(math.radians(angle)) + 0.75
    
    plt.scatter(x, y, c='black', marker='.', s=100, label='Target Center' if i == 0 else "")
    
    if target_radius != 0:
        circle = plt.Circle((x, y), target_radius, color='black', fill=False, label='Target Radius' if i == 0 else "")
        plt.gca().add_patch(circle)

plt.title(f'Distribution of endPoint in {full_name}', fontsize=14)
plt.xlabel('X Coordinate', fontsize=12)
plt.ylabel('Y Coordinate', fontsize=12)

plt.grid(True, alpha = 0.1)

plt.tight_layout()
plt.show()