import os
import argparse
import json
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
import numpy as np
import math
import utils
from collections import defaultdict, Counter

def save_poly_func(file, coeffs):
    np.save(file, coeffs)

def apply_poly_func(file):
    try:
        coeffs = np.load(file)
        poly_func = np.poly1d(coeffs)
        return poly_func
    except:
        return None

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


    # DC 1, SC 10 DH 10 SH 8
    parser.add_argument('--par', type=int, default='1', help='the chosen participant')
    args = parser.parse_args()
    full_name = ABBREV_TO_FULL.get(args.tech, args.tech)
    
    abbrev_name = FOLDER_ABBREVIATIONS.get(full_name, full_name)
    data_folders = [
        os.path.join('..', 'data', 'Heisenberg_updated', f'FP{args.par}', full_name, 'Study1') 
    ]

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

    train_data_path = os.path.join( 'indi_train_data', full_name + 'indi_train_data.json')
    with open(train_data_path, 'w') as f:
        json.dump(records, f, indent=2)
    print(f"filtered data saved to: {train_data_path}")

    
    
    file_path = train_data_path
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            records = json.load(f)

    df = pd.DataFrame(records)
    X = df[['relative_position']].values
    y = df['is_correct'].values

    coeffs = np.polyfit(df['relative_position'], df['is_correct'], deg=3)
    print(coeffs)
    poly_func = np.poly1d(coeffs)

    save_poly_func("./train_coeffs/" + full_name + "ind_weighted_VOTE_coeffs.npy", coeffs)


    x_plot = np.linspace(0, 1, 100)
    y_plot = poly_func(x_plot)

    print("x=0.2: " + str(poly_func(0.2)))
    plt.figure(figsize=(5, 4))
    
    plt.plot(x_plot, y_plot, label=f'Accuracy of           intention', color='blue')
    # plt.scatter(df['relative_position'], df['is_correct'], alpha=0.1, label='Raw data points')
    plt.xlabel('Relative Time', fontsize=20)
    plt.ylabel('Accuracy', fontsize=20)
    plt.legend(loc='lower right', fontsize=14)
    plt.grid(axis='y', linestyle='--', linewidth=0.5, alpha=1)
    plt.ylim(0.3, 1.05)
    plt.xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0], ['-1.0', '-0.8', '-0.6', '-0.4', '-0.2', '0.0'])
    plt.tick_params(axis='both', which='both', length=0,labelsize=14)
    plt.tight_layout()
    plt.savefig(f'./output_image/ind_{full_name}accuracy_plot.png', dpi=300, bbox_inches='tight')
    plt.show()
if __name__ == '__main__':
    main()