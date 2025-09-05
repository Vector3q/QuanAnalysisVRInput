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
bar_colors_group1 = ['#231942', '#9F86C0', '#E0B1CB', '#318BE0']
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

    TECH_TO_INDEX = {
        'DC': [1,5,10],
        'SC': [8,12,5],
        'DH': [7,10,17],
        'SH': [1,8,15]
    }
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--tech', type=str, default='DC', help='the technique of the json files')

    plt.figure(figsize=(5, 4))
    # DC 1,5,10 SC 7,10,12 DH 7,10,17 SH 8,15 [8,15]
    parser.add_argument('--par', type=int, default='1', help='the chosen participant')
    args = parser.parse_args()
    full_name = ABBREV_TO_FULL.get(args.tech, args.tech)
    target_par = TECH_TO_INDEX[args.tech]
    abbrev_name = FOLDER_ABBREVIATIONS.get(full_name, full_name)

    for pidx, par in enumerate(target_par):
       
        data_folders = [
            os.path.join('..', 'data', 'Heisenberg_updated', f'FP{par}', full_name, 'Study1') 
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

        derivative = poly_func.deriv()
        critical_points = derivative.roots
        critical_values = poly_func(critical_points)
        x_min, x_max = 0.0, 1.0
        endpoint_values = [poly_func(x_min), poly_func(x_max)]
        all_values = np.concatenate((critical_values, endpoint_values))
        max_value = np.max(all_values)
        max_index = np.argmax(all_values)
        if max_index < len(critical_points):
            max_x = critical_points[max_index]
            if max_x < 0.0:
                max_x = 0.0
                max_value = poly_func(0.0)
        else:
            max_x = x_min if max_index == len(critical_points) else x_max
            if max_x < 0.0:
                max_x = 0.0
                max_value = poly_func(0.0)
        
        print(f"max poly func: {max_value:.4f}, correspond to: {max_x:.4f}")

        x_plot = np.linspace(0, 1, 100)
        y_plot = poly_func(x_plot)

        print("x=0.2: " + str(poly_func(0.2)))
        
        print(pidx)
        # plt.plot(x_plot, y_plot, color=bar_colors_group1[pidx % 3])
        plt.plot(x_plot, y_plot, label=f'           intention', color=bar_colors_group1[pidx % 3])
        plt.plot([max_x, max_x], [0, max_value],
         color='gray', linestyle='--', linewidth=1)
        plt.scatter(max_x, max_value, color='gray', s=15, zorder=5)
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