from audioop import avg
import os
import json
import matplotlib.pyplot as plt
import argparse
import math
from collections import defaultdict

isprint = False

FOLDER_ABBREVIATIONS = {
    'ControllerTracking': 'DC',
    'ControllerIntenSelect': 'SC',
    'BareHandTracking': 'DH',
    'BareHandIntenSelect': 'SH'
}
ABBREV_TO_FULL = {v: k for k, v in FOLDER_ABBREVIATIONS.items()}

radius_spacing_stats = defaultdict(lambda: defaultdict(lambda: {
    'click_count': 0,
    'total_error': 0,
    'heisenberg_error': 0,
    'total_duration': 0
}))

parser = argparse.ArgumentParser(description='analyze the distribution of endPoint')
parser.add_argument('--folder', type=str, required=True, help='folder to be analyzed')
parser.add_argument('--radius', type=float, required=False, default=0, help='target radius')
parser.add_argument('--spacing', type=float, required=False, default=0, help='target distance')

args = parser.parse_args()
target_radius = args.radius
target_spacing = args.spacing

full_name = ABBREV_TO_FULL.get(args.folder, args.folder)
abbrev_name = FOLDER_ABBREVIATIONS.get(full_name, full_name)

data_folders = [
    f'../data\Heisenberg\P3\{full_name}/Study1',
    # f'../data\Heisenberg\P2\{full_name}/Study1'
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

            radius = data['radius']
            spacing = data['spacing']

            tech = data['inputtechnique']

            stats = radius_spacing_stats[radius][spacing]
            stats['click_count'] += len(data['selectionSequence'])

            for selection in data['selectionSequence']:
                stats['total_duration'] += selection['clickDuration']
                if not selection['isCorrect']:
                    stats['total_error'] += 1
                    if tech == "ControllerIntenSelect" or tech == "ControllerTracking":
                        intention_index = len(selection['historyCaches']) - 1
                        while intention_index >= 0:
                            if selection['historyCaches'][intention_index].get('confirmationValue', 0.0) == 0:
                                break
                            intention_index -= 1
                        if intention_index >= 0:
                            intention_obj = selection['historyCaches'][intention_index]['intendedObjectID']
                            target_obj = selection['targetPointID']
                            if (intention_obj is not None and 
                            target_obj is not None and 
                            intention_obj == target_obj):
                                stats['heisenberg_error'] += 1
                    
                    elif tech == "BareHandIntenSelect" or tech == "BareHandTracking":
                        velocityDIs = [cache.get('velocityDI', 0) for cache in selection['historyCaches']]
                        peak_index = velocityDIs.index(max(velocityDIs))
                        stable_index = peak_index
                        while stable_index >= 0 and velocityDIs[stable_index] >= 0.1:
                            stable_index -= 1
                        if stable_index >= 0:
                            stable_obj = selection['historyCaches'][stable_index]['intendedObjectID']
                            target_obj = selection['targetPointID']
                            if (stable_obj == target_obj):
                                stats['heisenberg_error'] += 1
            
print("\nRadius vs Spacing Statistics:")
print("Radius\tSpacing\tClicks\tError%\tH_Error%\tH_In_Error%")
for radius in sorted(radius_spacing_stats):
    for spacing in sorted(radius_spacing_stats[radius]):
        stats = radius_spacing_stats[radius][spacing]
        if stats['click_count'] > 0:
            print(f"{radius:.2f}\t{spacing:.2f}\t"
                  f"{stats['click_count']}\t"
                  f"{stats['total_error']/stats['click_count']:.2%}\t"
                  f"{stats['heisenberg_error']/stats['click_count']:.2%}\t\t"
                  f"{0 if stats['total_error'] == 0 else stats['heisenberg_error']/stats['total_error']:.2%}")

radius_stats = {}
for radius, spacing_dict in radius_spacing_stats.items():
    if radius not in radius_stats:
        radius_stats[radius] = {'click_count': 0, 'total_error': 0, 'heisenberg_error': 0, 'total_duration': 0}
    
    for spacing, stats in spacing_dict.items():
        radius_stats[radius]['click_count'] += stats['click_count']
        radius_stats[radius]['total_error'] += stats['total_error']
        radius_stats[radius]['heisenberg_error'] += stats['heisenberg_error']
        radius_stats[radius]['total_duration'] += stats['total_duration']


# 初始化spacing_stats字典
spacing_stats = {}

# 从radius_spacing_stats提取spacing单变量统计
for radius, spacing_dict in radius_spacing_stats.items():
    for spacing, stats in spacing_dict.items():
        if spacing not in spacing_stats:
            spacing_stats[spacing] = {'click_count': 0, 'total_error': 0, 'heisenberg_error': 0, 'total_duration': 0}
            
        spacing_stats[spacing]['click_count'] += stats['click_count']
        spacing_stats[spacing]['total_error'] += stats['total_error']
        spacing_stats[spacing]['heisenberg_error'] += stats['heisenberg_error']
        spacing_stats[spacing]['total_duration'] += stats['total_duration']


# 打印radius单变量统计
print("\nRadius Statistics:")
print("Radius | Click Count | Total Error % | Heisenberg Error % | Heisenberg/Total % | Avg Duration | e Score")
for radius, stats in sorted(radius_stats.items()):
    total_error_pct = (stats['total_error'] / stats['click_count'] * 100) if stats['click_count'] > 0 else 0
    heisenberg_pct = (stats['heisenberg_error'] / stats['click_count'] * 100) if stats['click_count'] > 0 else 0
    heisenberg_of_total = (stats['heisenberg_error'] / stats['total_error'] * 100) if stats['total_error'] > 0 else 0
    avg_duration = stats['total_duration'] / stats['click_count']
    print(f"{radius:6} | {stats['click_count']:11} | {total_error_pct:12.1f}% | {heisenberg_pct:17.1f}% | {heisenberg_of_total:17.1f}% | {avg_duration:12.3f} | {(1 / avg_duration) * (1 - stats['total_error'] / stats['click_count']):.3f}")

# 打印spacing单变量统计
print("\nSpacing Statistics:")
print("Spacing | Click Count | Total Error % | Heisenberg Error % | Heisenberg/Total % | Avg Duration | e Score")
for spacing, stats in sorted(spacing_stats.items()):
    total_error_pct = (stats['total_error'] / stats['click_count'] * 100) if stats['click_count'] > 0 else 0
    heisenberg_pct = (stats['heisenberg_error'] / stats['click_count'] * 100) if stats['click_count'] > 0 else 0
    heisenberg_of_total = (stats['heisenberg_error'] / stats['total_error'] * 100) if stats['total_error'] > 0 else 0
    avg_duration = stats['total_duration'] / stats['click_count']
    print(f"{spacing:7} | {stats['click_count']:11} | {total_error_pct:12.1f}% | {heisenberg_pct:17.1f}% | {heisenberg_of_total:17.1f}% | {avg_duration:12.3f} | {(1 / avg_duration) * (1 - stats['total_error'] / stats['click_count']):.3f} ")
