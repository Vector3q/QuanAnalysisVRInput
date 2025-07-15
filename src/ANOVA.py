from audioop import avg
import os
import json
import pandas as pd
from spicy import stats as spstats
import matplotlib.pyplot as plt
import argparse
import math
import utils
from collections import defaultdict
import statsmodels.formula.api as smf
from statsmodels.stats.anova import AnovaRM
isprint = False

FOLDER_ABBREVIATIONS = {
    'ALL': 'ALL',
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

radius_spacing_tech_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {
    'click_count': 0,
    'total_error': 0,
    'heisenberg_error': 0,
    'total_duration': 0
})))

parser = argparse.ArgumentParser(description='analyze the distribution of endPoint')
parser.add_argument('--folder', type=str, required=True, help='folder to be analyzed')
parser.add_argument('--radius', type=float, required=False, default=0, help='target radius')
parser.add_argument('--spacing', type=float, required=False, default=0, help='target distance')

args = parser.parse_args()
target_radius = args.radius
target_spacing = args.spacing

full_name = ABBREV_TO_FULL.get(args.folder, args.folder)
abbrev_name = FOLDER_ABBREVIATIONS.get(full_name, full_name)

data_folders = []

if(full_name != 'ALL'):
    data_folders = [
        f'../data\Heisenberg\FP1\{full_name}/Study1',
        f'../data\Heisenberg\FP2\{full_name}/Study1',
        f'../data\Heisenberg\FP3\{full_name}/Study1',
        f'../data\Heisenberg\FP4\{full_name}/Study1',
        f'../data\Heisenberg\FP5\{full_name}/Study1',
        f'../data\Heisenberg\TEST3\{full_name}/Study1',
    ]

if(full_name == 'ALL'):
    data_folders = [
        f'../data\Heisenberg',
    ]

# '../data/Heisenberg/P1/BareHandIntenSelect/Study1_ISO_Test_Varied_Distance',

click_count = 0
total_error_count = 0
heisenberg_error_count = 0
all_records = []

json_files = utils.get_all_json_files('../data/Heisenberg')

for file_name in json_files:
    with open(file_name, 'r') as f:
        data = json.load(f)

    base_info = {
        'username': data.get('username'),
        'inputtechnique': data.get('inputtechnique'),
        'radius': data.get('radius'),
        'distance': data.get('distance'),
        'spacing': data.get('spacing')
    }
    tech = data['inputtechnique']
    trial_Duration = 0
    trial_ClickCount = len(data['selectionSequence'])
    trial_ErrorCount = 0
    trial_HErrorCount = 0
    for selection in data['selectionSequence']:
        trial_Duration += selection['clickDuration']
        if not selection['isCorrect']:
            trial_ErrorCount += 1
            if tech == "ControllerIntenSelect" or tech == "ControllerTracking":
                intention_index = len(selection['historyCaches']) - 1
                while intention_index >= 0:
                    if selection['historyCaches'][intention_index].get('confirmationValue', 0.0) == 0 and selection['historyCaches'][intention_index]['intendedObjectID'] != "null":
                        break
                    intention_index -= 1
                if intention_index >= 0:
                    intention_obj = selection['historyCaches'][intention_index]['intendedObjectID']
                    target_obj = selection['targetPointID']
                    if (intention_obj is not None and 
                            target_obj is not None and 
                            intention_obj == target_obj):
                        trial_HErrorCount += 1
                    
            elif tech == "BareHandIntenSelect" or tech == "BareHandTracking":
                velocityDIs = [cache.get('velocityDI', 0) for cache in selection['historyCaches']]
                peak_index = velocityDIs.index(max(velocityDIs))
                stable_index = peak_index
                while stable_index >= 0:
                    if velocityDIs[stable_index] <= 0.1 and selection['historyCaches'][stable_index]['intendedObjectID'] != "null":
                        break
                    stable_index -= 1
                if stable_index >= 0:
                    stable_obj = selection['historyCaches'][stable_index]['intendedObjectID']
                    target_obj = selection['targetPointID']
                    if (stable_obj == target_obj):
                        trial_HErrorCount += 1
    trial_record = base_info.copy()
    trial_record.update({
        'clickDuration': trial_Duration,
        'errorRate': trial_ErrorCount / trial_ClickCount,
        'HerrorRate': trial_HErrorCount / trial_ClickCount
    })
    all_records.append(trial_record)
    
df = pd.DataFrame(all_records)
df['username'] = df['username'].astype('category')
df['inputtechnique'] = df['inputtechnique'].astype('category')
df['radius'] = df['radius'].astype('category')

if True:  # 始终执行所有数据的统计
    # 按技术和半径分组计算统计量
    grouped = df.groupby(['inputtechnique', 'radius'])
    stats = grouped['clickDuration'].agg(['count', 'mean', 'std'])
    
    # 遍历所有组并打印结果
    for (technique, radius), row in stats.iterrows():
        count = row['count']
        avg_duration = row['mean']
        std_duration = row['std']
        
        if count > 0:
            print(f"== {technique} (radius={radius}) 时间统计 ===")
            print(f"样本量: {count}")
            print(f"平均点击时间: {avg_duration:.3f} s")
            print(f"时间标准差: {std_duration:.3f} s")
            print(f"95%置信区间: [{avg_duration - 1.96*std_duration/math.sqrt(count):.3f}, {avg_duration + 1.96*std_duration/math.sqrt(count):.3f}]")

df_agg = df.groupby(['username', 'inputtechnique', 'radius', 'spacing'])['HerrorRate'].mean().reset_index()

aovrm = AnovaRM(data=df_agg, depvar='HerrorRate', subject='username',
                within=['inputtechnique', 'radius', 'spacing']) # 包含所有组内因素
fit = aovrm.fit()

print(fit)

