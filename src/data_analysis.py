import numpy as np
import argparse
import json

from data_preprocess import load_json_data, save_data_to_json
def read_from_numpy(file_path):
    data = np.load(file_path, allow_pickle=True)
    return data.item()
    
def extract_all_wanted_data(data):
    all_selection_times = []
    all_correct_selection_times = []
    all_selection_errors = []
    all_H_selection_errors = []

    # print("data len: ", len(data))

    for data_item in data:
        correct_selection_times = [entry["clickDuration"] for entry in data_item["selectionSequence"] if float(entry["isCorrect"]) > 0]
        selection_times = [entry["clickDuration"] for entry in data_item["selectionSequence"]]
        selection_errors = [float(entry["isCorrect"]) for entry in data_item["selectionSequence"]]
        H_selection_errors = [float(1) if entry["HeisenbergError"] == 1 and entry["isCorrect"] == 0 else float(0) for entry in data_item["selectionSequence"]]

        all_selection_times.extend(selection_times)
        all_selection_errors.extend(selection_errors)
        all_H_selection_errors.extend(H_selection_errors)
        all_correct_selection_times.extend(correct_selection_times)

    return len(all_correct_selection_times), all_selection_times, all_selection_errors, all_H_selection_errors


def get_global_avg_and_std(selection_times):
    # print("sum: ", np.sum(selection_times))
    # print("len: ", len(selection_times))
    print("average: ", np.mean(selection_times))

    avg = np.mean(selection_times)

    std_dev = np.std(selection_times)
    print("std_dev: ", std_dev)
    
    sem = std_dev / np.sqrt(len(selection_times))
    print("sem: ", sem)
    return avg, std_dev, sem

def compute_global_error_rate(selection_errors):
    accuracy_rate = np.mean(selection_errors)
    print("accuracy: ", accuracy_rate)
    accuracy_sem = np.std(selection_errors) / np.sqrt(len(selection_errors))
    print("accuracy_sem: ", accuracy_sem)
    print("error rate: ", 1-accuracy_rate)
    return accuracy_rate, accuracy_sem

def compute_global_H_error_rate(H_selection_errors):
    H_error_rate = np.mean(H_selection_errors)
    print("H_error_rate: ", H_error_rate)
    H_error_rate_sem = np.std(H_selection_errors) / np.sqrt(len(H_selection_errors))
    print("H_error_rate_sem: ", H_error_rate_sem)
    print("")
    return H_error_rate, H_error_rate_sem

def save_to_numpy(data, file_path):
    np.save(file_path, data) 

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

    radius_range = ['radius_007', 'radius_014', 'radius_021']
    spacing_range = ['spacing_03', 'spacing_05', 'spacing_07']

    def analyze_data(partial_name):
        data_file_path = './output_json/' + full_name + "_" + partial_name + "_data.json"
        data = load_json_data(data_file_path)

        print(f'tech: {full_name}, partial_name: {partial_name}')


        if data is None:
            print("The data is None for ", full_name, " and ", partial_name)

        click_count, all_selection_times, all_selection_errors, H_selection_errors = extract_all_wanted_data(data)
        global_avg_selection_time, global_std_selection_time, global_sem_selection_time = get_global_avg_and_std(all_selection_times)

        global_error_rate, global_error_rate_sem = compute_global_error_rate(all_selection_errors)

        global_H_error_rate, global_H_error_rate_sem = compute_global_H_error_rate(H_selection_errors)

        processed_data = {
            "technique": full_name,
            "global_avg_selection_time": global_avg_selection_time,
            "global_std_selection_time": global_std_selection_time,
            "global_sem_selection_time": global_sem_selection_time,
            "global_error_rate": global_error_rate,
            "global_error_rate_sem": global_error_rate_sem,
            "global_H_error_rate": global_H_error_rate,
            "global_H_error_rate_sem": global_H_error_rate_sem
        }
        save_to_numpy(processed_data, './output_numpy/' + full_name + "_" + partial_name + "_data.npy")

    for r in radius_range:
        analyze_data(r)

    for s in spacing_range:
        analyze_data(s)

if __name__ == '__main__':
    main()