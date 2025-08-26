import os
import argparse
import json
import pandas as pd
import numpy as np
import utils
import matplotlib.pyplot as plt

from collections import defaultdict, Counter
def save_poly_func(file, coeffs):
    np.save(file, coeffs)

def train_func(file_path, func_file):
    print("os.path.exists(file_path): " + file_path)
    if os.path.exists(file_path):
        print(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            records = json.load(f)

    
    df = pd.DataFrame(records)
    X = df[['relative_position']].values
    y = df['is_correct'].values

    coeffs = np.polyfit(df['relative_position'], df['is_correct'], deg=3)
    print(coeffs)
    poly_func = np.poly1d(coeffs)
    save_poly_func(func_file, coeffs)
    return poly_func

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

    fp_range = utils.fp_test
    selection_records = 0
        
    data_folders = []
    fp_values = []
    for i in fp_range:
        data_folders.append(os.path.join('..', 'data', 'Heisenberg', f'FP{i}', full_name, 'Study1'))
        fp_values.append(i)
        
    print(f"data_len: {len(data_folders)}")


    train_data = []
    filtered_selections = []
    for data_folder, fp_value in zip(data_folders, fp_values):
        print(f"Processing FP{fp_value}")
        records = []
        for filename in os.listdir(data_folder):
            if filename.endswith('.json'):
                json_path = os.path.join(data_folder, filename)
                
                with open(json_path, 'r') as f:
                    data = json.load(f)

                selection_sequence = data['selectionSequence']
                total_selections = len(selection_sequence)
                end_idx = int(total_selections * 0.2)
                selection_sequence = selection_sequence[:end_idx]
                    
                selection_records += len(data['selectionSequence'])
                for selection in selection_sequence:
                    
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

        train_data_adaptive_path = os.path.join( 'train_data_adaptive', f'FP{fp_value}_{full_name}_train_data_adaptive.json')
        with open(train_data_adaptive_path, 'w') as f:
            json.dump(records, f, indent=2)
        print(f"过滤后的数据已保存到: {train_data_adaptive_path}")

    for data_folder, fp_value in zip(data_folders, fp_values):
        print(fp_value)
        train_data_adaptive_path = os.path.join( 'train_data_adaptive', f'FP{fp_value}_{full_name}_train_data_adaptive.json')
        func_file = os.path.join( 'train_coeffs', f'FP{fp_value}_{full_name}_weighted_VOTE_coeffs.npy')
        poly_func = train_func(train_data_adaptive_path, func_file)
        x_plot = np.linspace(0, 1, 100)
        y_plot = poly_func(x_plot)
        
        plt.figure(figsize=(5, 4))
        plt.plot(x_plot, y_plot, color='blue')
        # plt.scatter(df['relative_position'], df['is_correct'], alpha=0.1, label='Raw data points')
        plt.xlabel('Relative Time', fontsize=20)
        plt.ylabel('Accuracy', fontsize=20)
        plt.grid(axis='y', linestyle='--', linewidth=0.5, alpha=1)
        plt.ylim(0.3, 1.05)
        plt.tick_params(axis='both', which='both', length=0, labelsize=14)
        plt.tight_layout()
        plt.savefig(f'./output_image_adaptive/FP{fp_value}_{full_name}_accuracy_plot.png', dpi=300, bbox_inches='tight')

if __name__ == '__main__':
    main()