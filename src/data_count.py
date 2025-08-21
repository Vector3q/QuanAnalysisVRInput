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

click_count = 0

try:
    # 获取所有被试文件夹 (FP开头的文件夹)
    for item in os.listdir(DATA_ROOT):
        item_path = os.path.join(DATA_ROOT, item)
        if os.path.isdir(item_path) and item.startswith('FP'):
            subject = item
            
            # 检查每种技术类型
            for tech_full, tech_abbrev in TECHNIQUES.items():
                tech_path = os.path.join(item_path, tech_full, 'Study1')
                
                if os.path.exists(tech_path):
                    # 计算该文件夹下的json文件数量
                    json_count = 0
                    for filename in os.listdir(tech_path):
                        if filename.endswith('.json'):
                            json_count += 1

                        json_path = os.path.join(tech_path, filename)
                        with open(json_path, 'r') as f:
                            data = json.load(f)
                            click_count += len(data['selectionSequence'])

                        


                    stats[subject][tech_full] = json_count
                    print(f'被试 {subject}, 条件 {tech_full}: {json_count} 个JSON文件')

    # 将统计结果保存为JSON
    with open('json_file_counts.json', 'w') as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)
        print(f'统计结果已保存到 json_file_counts.json')

except Exception as e:
    print(f'发生错误: {e}')
    print('请确保数据文件夹路径正确，并且具有访问权限。')

# 打印统计摘要
print('\n统计摘要:')
for subject in stats:
    total = sum(stats[subject].values())
    print(f'被试 {subject}: 总计 {total} 个JSON文件')

print(f'click_count: {click_count}')