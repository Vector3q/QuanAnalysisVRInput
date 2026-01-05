import os
import json
from collections import defaultdict

DATA_ROOT = os.path.join('..', 'data', 'Heisenberg')

TECHNIQUES = {
    'ControllerTracking': 'DC',
    'ControllerIntenSelect': 'SC',
    'BareHandTracking': 'DH',
    'BareHandIntenSelect': 'SH'
}

stats = defaultdict(lambda: defaultdict(int))

click_count = defaultdict(lambda: defaultdict(int))

try:
    for item in os.listdir(DATA_ROOT):
        item_path = os.path.join(DATA_ROOT, item)
        if os.path.isdir(item_path) and item.startswith('FP'):
            subject = item
            
            for tech_full, tech_abbrev in TECHNIQUES.items():
                tech_path = os.path.join(item_path, tech_full, 'Study1')
                
                if os.path.exists(tech_path):
                    json_count = 0
                    for filename in os.listdir(tech_path):
                        if filename.endswith('.json'):
                            json_count += 1

                            json_path = os.path.join(tech_path, filename)
                            with open(json_path, 'r') as f:
                                data = json.load(f)
                                click_count[subject][tech_full] += len(data['selectionSequence'])

                    stats[subject][tech_full] = json_count
                    print(f'subject: {subject}, condition: {tech_full}: {json_count} json file')

except Exception as e:
    print(f'error: {e}')
    print('ensure the correct path of the data folder.')

for subject in stats:
    total = sum(stats[subject].values())
    print(f'subject: {subject}: total {total} json file')

tech_click_total = defaultdict(int)
for subject in click_count:
    for tech, count in click_count[subject].items():
        tech_click_total[tech] += count

for tech, total in tech_click_total.items():
    print(f'condition: {tech}: {total} click')

# 总点击次数
total_all = sum(tech_click_total.values())
print(f'\ntotal click: {total_all}')
