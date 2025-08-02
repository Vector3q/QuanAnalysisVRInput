import os
import argparse
import json
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
import numpy as np

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

    x_plot = np.linspace(0, 1, 100)
    y_plot = poly_func(x_plot)
    
    plt.figure(figsize=(8, 5))
    plt.plot(x_plot, y_plot, label='P(correct | relative_position)', color='blue')
    # plt.scatter(df['relative_position'], df['is_correct'], alpha=0.1, label='Raw data points')
    plt.xlabel('Relative Position in HistoryCache')
    plt.ylabel('P(Intended == Target)')
    plt.title('Voting Weight Function Across Multiple Sessions')
    plt.legend()
    plt.grid(True)
    plt.ylim(0.4, 1)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()