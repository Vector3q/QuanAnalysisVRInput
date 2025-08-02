import os
import argparse
import json
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
import numpy as np

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

    args = parser.parse_args()
    full_name = ABBREV_TO_FULL.get(args.tech, args.tech)
    abbrev_name = FOLDER_ABBREVIATIONS.get(full_name, full_name)
    
    file_path = "./train_data/" + full_name + "_train_data.json"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            records = json.load(f)

    df = pd.DataFrame(records)
    X = df[['relative_position']].values
    y = df['is_correct'].values

    coeffs = np.polyfit(df['relative_position'], df['is_correct'], deg=3)
    print(coeffs)
    poly_func = np.poly1d(coeffs)

    save_poly_func("./train_coeffs/" + full_name + "_weighted_VOTE_coeffs.npy", coeffs)


    x_plot = np.linspace(0, 1, 100)
    y_plot = poly_func(x_plot)

    print("x=0.2: " + str(poly_func(0.2)))
    
    plt.figure(figsize=(5, 4))
    plt.plot(x_plot, y_plot, label='P(accuracy | relative time)', color='blue')
    # plt.scatter(df['relative_position'], df['is_correct'], alpha=0.1, label='Raw data points')
    plt.xlabel('Relative Time', fontsize=15)
    plt.ylabel('Accuracy', fontsize=15)
    plt.legend(loc='lower right')
    plt.grid(axis='y', linestyle='--', linewidth=0.5, alpha=1)
    plt.ylim(0.4, 1.05)
    plt.tick_params(axis='both', which='both', length=0)
    plt.tight_layout()
    plt.savefig(f'./output_image/{full_name}accuracy_plot.png', dpi=300, bbox_inches='tight')
    plt.show()

    coeffs_file = "./train_coeffs/" + full_name + "_weighted_VOTE_coeffs.npy"
    coeffs = np.load(coeffs_file)
    weight_func = np.poly1d(coeffs)

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
    fp_range = range(8, 14)
    data_folders = [
        os.path.join('..', 'data', 'Heisenberg', f'FP{i}', full_name, 'Study1') 
        for i in fp_range
    ]
    click_count = 0
    weighted_vote_count = 0
    total_VOTE_eror_count = 0
    total_Befor_error_count = 0
    for data_folder in data_folders:
        # print(f"\nAnalyzing file folder: {data_folder}")

        for filename in os.listdir(data_folder):
            if filename.endswith('.json'):
                json_path = os.path.join(data_folder, filename)
                
                with open(json_path, 'r') as f:
                    data = json.load(f)

                radius = data['radius']
                spacing = data['spacing']

                tech = data['inputtechnique']

                for selection in data['selectionSequence']:
                    
                    if selection['clickDuration'] < 0.05:
                        continue
                    
                    click_count += 1
                    weighted_votes = defaultdict(float)
                    
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
                            
                            weight = weight_func(relative_position)
                            
                            weight = max(0, weight)

                            transformed_weight = weight ** power
                            
                            weighted_votes[object_id] += transformed_weight
                    
                    if closest_cache is not None:
                            intended_object = closest_cache.get('intendedObjectID')
                            if intended_object != selection['targetPointID']:
                                total_Befor_error_count+=1

                    if weighted_votes:
                        sorted_objects = sorted(weighted_votes.items(), key=lambda x: x[1], reverse=True)

                        # 获取第一个物体
                        predicted_object = sorted_objects[0][0] if sorted_objects else None

                        # 如果第一个物体是null，尝试使用第二个物体
                        if predicted_object is None or predicted_object == "null":
                            if len(sorted_objects) > 1:
                                predicted_object = sorted_objects[1][0]
                            # 如果只有一个物体且是null，则保留null

                        target_id = selection['targetPointID']
                        is_correct = 1 if predicted_object == target_id else 0

                        if is_correct == 1:
                            weighted_vote_count += 1
                    else:
                        print('没有有效的投票数据')

                    intended_objects = [cache['intendedObjectID'] for cache in selection['historyCaches'] 
                    if 'intendedObjectID' in cache and cache['intendedObjectID'] != "null"]
                    obj_counter = Counter(intended_objects)
                    most_common_obj, count = obj_counter.most_common(1)[0] if intended_objects else (None, 0)
                    if selection['targetPointID'] != most_common_obj:
                        total_VOTE_eror_count += 1


    print(f"Error rate of vote:  ({total_VOTE_eror_count / click_count:.2%})")
    print(f"Error rate of before vote:  ({total_Befor_error_count / click_count:.2%})")
    print(f"Error rate of weighted vote:  ({1-(weighted_vote_count / click_count):.2%})")
if __name__ == '__main__':
    main()