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
parser.add_argument('--tech', type=str, required=True, help='folder to be analyzed')
parser.add_argument('--radius', type=float, required=True, default=0, help='target radius')
parser.add_argument('--spacing', type=float, required=True, default=0, help='target spacing')

args = parser.parse_args()
target_radius = args.radius
target_spacing = args.spacing

full_name = ABBREV_TO_FULL.get(args.tech, args.tech)
abbrev_name = FOLDER_ABBREVIATIONS.get(full_name, full_name)

data_folders = [ 
    f'../data\Heisenberg\FP1\{full_name}/Study1',
    f'../data\Heisenberg\FP2\{full_name}/Study1',
    f'../data\Heisenberg\FP3\{full_name}/Study1',
    f'../data\Heisenberg\FP4\{full_name}/Study1',
    f'../data\Heisenberg\FP5\{full_name}/Study1',
    f'../data\Heisenberg\FP6\{full_name}/Study1',
    f'../data\Heisenberg\FP7\{full_name}/Study1',
    f'../data\Heisenberg\FP8\{full_name}/Study1',
    f'../data\Heisenberg\FP9\{full_name}/Study1',
    f'../data\Heisenberg\FP10\{full_name}/Study1',
    f'../data\Heisenberg\FP11\{full_name}/Study1',
    f'../data\Heisenberg\FP12\{full_name}/Study1',
    f'../data\Heisenberg\FP13\{full_name}/Study1',
    f'../data\Heisenberg\FP14\{full_name}/Study1',
    f'../data\Heisenberg\FP15\{full_name}/Study1',
    f'../data\Heisenberg\FP16\{full_name}/Study1',
    f'../data\Heisenberg\FP17\{full_name}/Study1',
    f'../data\Heisenberg\FP18\{full_name}/Study1',
    f'../data\Heisenberg\FP19\{full_name}/Study1',
    f'../data\Heisenberg\FP20\{full_name}/Study1',
    f'../data\Heisenberg\FP21\{full_name}/Study1',
    f'../data\Heisenberg\FP22\{full_name}/Study1',
    f'../data\Heisenberg\FP23\{full_name}/Study1',
    f'../data\Heisenberg\FP24\{full_name}/Study1',
]

# '../data/Heisenberg/P1/BareHandIntenSelect/Study1_ISO_Test_Varied_Distance',

x_coords = []
y_coords = []
colors = []
bar_colors_group1 = ['#FED976', '#FEB24C', '#9EC9E2', '#5F97D2']
for data_folder in data_folders:
    for filename in os.listdir(data_folder):
        if filename.endswith('.json'):
            json_path = os.path.join(data_folder, filename)

            with open(json_path, 'r') as f:
                data = json.load(f)

            if target_radius != 0 and data['radius'] != target_radius:
                continue;
            if target_spacing != 0 and data['spacing'] != target_spacing:
                continue;
                
            for i, selection in enumerate(data['selectionSequence'], 1):
                
                point = selection['endPointInEnd']

                if(abs(point[0]) < 0.01 and abs(point[1]) < 0.01):
                    continue;
                x_coords.append(point[0])
                y_coords.append(point[1])

print(f"records_count: {len(x_coords)}")


plt.figure(figsize=(6, 6))
plt.scatter(x_coords, y_coords, c='green', marker='o', alpha=0.3)

import numpy as np
x_ticks = plt.xticks()[0]
x_ticks = [-1,0,1]
x_tick_labels = [-3.6, 0.0, 3.6]
plt.xticks(x_ticks, x_tick_labels)


y_ticks = plt.yticks()[0]
y_ticks = [0,1,2,3,4,5,6]
y_tick_labels = [-7.1, -3.6, 0.0, 3.6, 7.1, 10.6, 14.0]
plt.yticks(y_ticks, y_tick_labels)
plt.tick_params(axis='both', which='major', labelsize=16)

# if(args.tech == "DC"):
#     plt.tick_params(axis='both', which='major', labelsize=16)
# else:
#     plt.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)
#     plt.tick_params(axis='x', which='major', labelsize=16)

target_distance = 0.75
number_of_targets = 13
angle_step = 360 / number_of_targets

for i in range(1,6):
    for j in range(1,6):
        x = (j - 3) * (target_spacing)
        y = (6 - i) * (target_spacing)



        plt.scatter(x, y, c='black', marker='.', s=100, label='Target Center' if i == 0 else "")

        if target_radius != 0:
            circle = plt.Circle((x, y), target_radius, color='black', fill=False, label='Target Radius' if i == 0 else "")
            plt.gca().add_patch(circle)

# for i in range(number_of_targets):
#     angle = i * angle_step
#     x = target_distance * math.cos(math.radians(angle))
#     y = target_distance * math.sin(math.radians(angle)) + 0.75
    
#     plt.scatter(x, y, c='black', marker='.', s=100, label='Target Center' if i == 0 else "")
    
#     if target_radius != 0:
#         circle = plt.Circle((x, y), target_radius, color='black', fill=False, label='Target Radius' if i == 0 else "")
#         plt.gca().add_patch(circle)

plt.xlabel('X Angle (Deg)', fontsize=20)
plt.ylabel('Y Angle (Deg)', fontsize=20)

plt.grid(True, alpha = 0.1)
plt.xlim(-2, 2)  
plt.ylim(0.2, 4.2) 

plt.tight_layout()
plt.savefig(f'./output_image/endpoint_{full_name}.png', dpi=300, bbox_inches='tight')