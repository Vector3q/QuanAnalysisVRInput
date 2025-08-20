import os
import argparse
import json
import pandas as pd
import numpy as np
import utils


from collections import defaultdict, Counter



def main():
    FOLDER_ABBREVIATIONS = {
    'ControllerTracking': 'DC',
    'ControllerIntenSelect': 'SC',
    'BareHandTracking': 'DH',
    'BareHandIntenSelect': 'SH'
    }
    ABBREV_TO_FULL = {v: k for k, v in FOLDER_ABBREVIATIONS.items()}

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--tech', type=str, default='DC', help='the technique of the json files')

    args = parser.parse_args()
    full_name = ABBREV_TO_FULL.get(args.tech, args.tech)
    abbrev_name = FOLDER_ABBREVIATIONS.get(full_name, full_name)

    fp_range = utils.fp_all

        
    data_folders = [
        os.path.join('..', 'data', 'Heisenberg', f'FP{i}', full_name, 'Study1') 
        for i in fp_range
    ]
    print(f"data_len: {len(data_folders)}")

    train_data = []
    filtered_selections = []
    records = []
    for data_folder in data_folders:
        # print(f"\nAnalyzing file folder: {data_folder}")

        for filename in os.listdir(data_folder):
            if filename.endswith('.json'):
                json_path = os.path.join(data_folder, filename)
                
                with open(json_path, 'r') as f:
                    data = json.load(f)

                for selection in data['selectionSequence']:
                    
                    if selection['clickDuration'] < 0.05:
                        continue

                    intended_objects = [cache['intendedObjectID'] for cache in selection['historyCaches'] 
                    if 'intendedObjectID' in cache and cache['intendedObjectID'] != "null"]
                    
                    target_id = selection['targetPointID']
                    if target_id in intended_objects:
                        selection.pop('clickDuration')
                        selection.pop('targetPointPos')
                        selection.pop('endPointInStart')
                        selection.pop('selectedPointID')
                        selection.pop('isCorrect')
                        selection.pop('endPointInEnd')
                        
                        selection['username'] = data['username']
                        lens = len(selection['historyCaches'])
                        for idx, entry in enumerate(selection['historyCaches']):
                            intended = entry['intendedObjectID']
                            is_correct = int(intended == selection['targetPointID'])
                            records.append({
                                'user': data['username'],
                                'relative_position': idx/(lens-1),
                                'is_correct': is_correct
                            })
                        
                        filtered_selections.append(selection)

    train_data_path = os.path.join( 'train_data', full_name + '_train_data.json')
    with open(train_data_path, 'w') as f:
        json.dump(records, f, indent=2)
    print(f"过滤后的数据已保存到: {train_data_path}")

    df = pd.DataFrame(records)
    bins = np.arange(0, 1.1, 0.1)
    df['bucket'] = pd.cut(df['relative_position'], bins, labels=bins[:-1])
    pivot = df.groupby(['user', 'bucket'])['is_correct'].mean().unstack(fill_value=0)

    positions = [f"{pos:.1f}" for pos in bins[:-1]]
    header = "User".ljust(8) + " | " + " | ".join([f"Pos={p}".ljust(6) for p in positions])
    print(header)
    print("-" * len(header))

    for user, row in pivot.iterrows():
        line = user.ljust(8) + " | " + " | ".join([f"{row[pos]:.2f}".ljust(7) for pos in row.index])
        print(line)

if __name__ == '__main__':
    main()