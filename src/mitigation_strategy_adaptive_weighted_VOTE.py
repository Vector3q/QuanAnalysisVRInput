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

def train_func(file_path, func_file):
    if os.path.exists(file_path):
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
    
    file_path = "./train_data/" + full_name + "_train_data.json"
    func_file = "./train_coeffs/" + full_name + "_weighted_VOTE_coeffs.npy"
    poly_func = train_func(file_path, func_file)
    
    
    x_plot = np.linspace(0, 1, 100)
    y_plot = poly_func(x_plot)
    
    plt.figure(figsize=(5, 4))

    if args.tech == "DC":
        plt.plot(x_plot, y_plot, label='P(accuracy | relative time)', color='blue')
    else:
        plt.plot(x_plot, y_plot, color='blue')
    # plt.scatter(df['relative_position'], df['is_correct'], alpha=0.1, label='Raw data points')
    plt.xlabel('Relative Time', fontsize=20)
    plt.ylabel('Accuracy', fontsize=20)
    if args.tech == "DC":
        plt.legend(loc='lower right', fontsize=14)
    plt.grid(axis='y', linestyle='--', linewidth=0.5, alpha=1)
    plt.ylim(0.3, 1.05)
    plt.tick_params(axis='both', which='both', length=0, labelsize=14)
    plt.tight_layout()
    plt.savefig(f'./output_image/{full_name}accuracy_plot.png', dpi=300, bbox_inches='tight')
    # plt.show()

    print(f"plt saved to {f'./output_image/{full_name}accuracy_plot.png'}")

    coeffs_file = func_file
    coeffs = np.load(coeffs_file)
    weight_func = np.poly1d(coeffs)

    data_folders = []
    fp_values = []
    fp_range = utils.fp_test
    data_folders = [
        os.path.join('..', 'data', 'Heisenberg', f'FP{i}', full_name, 'Study1') 
        for i in fp_range
    ]

    adaptive_weight_funcs = {}
    for fp_value in fp_range:
        adaptive_func_file = f"./train_coeffs/FP{fp_value}_{full_name}_weighted_VOTE_coeffs.npy"
        if os.path.exists(adaptive_func_file):
            adaptive_coeffs = np.load(adaptive_func_file)
            adaptive_func = np.poly1d(adaptive_coeffs)
            alpha = 1

            interpolated_func = lambda x, fp=fp_value: alpha * adaptive_func(x) + (1 - alpha) * weight_func(x)
            adaptive_weight_funcs[fp_value] = interpolated_func
            print(f"adaptive_func: {adaptive_func}")
            print(f"weight_func: {weight_func}")
        else:
            adaptive_weight_funcs[fp_value] = weight_func

    

    

    derivative = weight_func.deriv()
    critical_points = derivative.roots
    critical_values = weight_func(critical_points)
    x_min, x_max = 0.0, 1.0
    endpoint_values = [weight_func(x_min), weight_func(x_max)]
    all_values = np.concatenate((critical_values, endpoint_values))
    max_value = np.max(all_values)
    max_index = np.argmax(all_values)
    if max_index < len(critical_points):
        max_x = critical_points[max_index]
    else:
        max_x = x_min if max_index == len(critical_points) else x_max

    print(f"max poly func: {max_value:.4f}, correspond to: {max_x:.4f}")
    power = 20.0
    
    click_count = 0
    weighted_vote_count = 0
    total_VOTE_eror_count = 0
    total_Befor_error_count = 0

    for data_folder, fp_value in zip(data_folders, fp_range):
        for filename in os.listdir(data_folder):
            if filename.endswith('.json'):
                json_path = os.path.join(data_folder, filename)
                with open(json_path, 'r') as f:
                    data = json.load(f)
                selection_sequence = data['selectionSequence']
                total_selections = len(selection_sequence)
                start_index = int(total_selections * 0.2)
                selection_sequence = selection_sequence[start_index:]

                for selection in selection_sequence:
                    
                    if selection['clickDuration'] < 0.05:
                        continue
                    
                    click_count += 1
                    weighted_votes = defaultdict(float)
                    
                    a, b = 0, 1
                    n = 500
                    xs = np.linspace(a, b, n)
                    ys = adaptive_weight_funcs[fp_value](xs)
                    x_q = np.quantile(ys, 3/4)
                    # print("3/4 y value =", x_q)

                    closest_cache = None
                    min_diff = float('inf')
                    history_caches = selection.get('historyCaches', [])

                    for idx, cache in enumerate(selection['historyCaches']):
                        relative_position = idx / (len(selection['historyCaches']) - 1) if len(selection['historyCaches']) > 1 else 0.5
                        if relative_position is not None:
                            diff = abs(relative_position - max_x)
                            if diff < min_diff:
                                min_diff = diff
                                closest_cache = cache
                        

                        if 'intendedObjectID' in cache:
                            object_id = cache['intendedObjectID']
                            
                            weight = adaptive_weight_funcs[fp_value](relative_position)
                            weight = max(0, weight)

                            k = 15.0   
                            x0 = x_q     
                            transformed_weight = 1 / (1 + math.exp(-k * (weight - x0)))
                            weighted_votes[object_id] += transformed_weight
                            # transformed_weight = weight ** power
                            # weighted_votes[object_id] += transformed_weight
                    
                    if closest_cache is not None:
                            intended_object = closest_cache.get('intendedObjectID')
                            if intended_object != selection['targetPointID']:
                                total_Befor_error_count+=1

                    if weighted_votes:
                        sorted_objects = sorted(weighted_votes.items(), key=lambda x: x[1], reverse=True)

                        predicted_object = sorted_objects[0][0] if sorted_objects else None

                        if predicted_object is None or predicted_object == "null":
                            if len(sorted_objects) > 1:
                                predicted_object = sorted_objects[1][0]

                        target_id = selection['targetPointID']
                        is_correct = 1 if predicted_object == target_id else 0

                        if is_correct == 1:
                            weighted_vote_count += 1
                    else:
                        print('no valid voting data')

                    intended_objects = [cache['intendedObjectID'] for cache in selection['historyCaches'] 
                    if 'intendedObjectID' in cache and cache['intendedObjectID'] != "null"]
                    obj_counter = Counter(intended_objects)
                    most_common_obj, count = obj_counter.most_common(1)[0] if intended_objects else (None, 0)
                    if selection['targetPointID'] != most_common_obj:
                        total_VOTE_eror_count += 1

    print(f"Error rate of vote:  ({total_VOTE_eror_count / click_count:.2%})")
    print(f"Error rate of before click:  ({total_Befor_error_count / click_count:.2%})")
    print(f"Error rate of weighted vote:  ({1-(weighted_vote_count / click_count):.2%})")

if __name__ == '__main__':
    main()