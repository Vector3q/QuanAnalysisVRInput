import json
import matplotlib.pyplot as plt

json_path = '..\data\Heisenberg\P1\Study1_ISO_Test_Varied_TargetSize\P1_ExperimentData_20250529_161136.json'

with open(json_path, 'r') as f:
    data = json.load(f)

print("\n-------    实验数据    -------\n")
print(f"用户名: {data['username']}")
print(f"年龄: {data['userAge']}")
print(f"性别: {data['usergender']}")

distance_di_values = []

plt.figure(figsize=(8, 5), dpi=100)

for i, selection in enumerate(data['selectionSequence'], 1):
    print(f"\n选择 {i}:")
    print(f"点击时长: {selection['clickDuration']}秒")
    print(f"是否正确: {'是' if selection['isCorrect'] else '否'}")
    print(f"选择点ID: {selection['selectedPointID']}")
    print(f"目标点ID: {selection['targetPointID']}")
    