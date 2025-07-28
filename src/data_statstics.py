from calendar import c
import numpy as np
import argparse
import json
from scipy import stats
import pandas as pd
import pingouin as pg
import os

def load_technique_data(npy_dir):
    data = []
    for filename in os.listdir(npy_dir):
        if filename.endswith('.npy') and ('spacing' in filename or 'radius' in filename):
            parts = filename.split('_')
            if len(parts) < 3:
                continue
                
            # 提取技术类型、条件类型和水平
            technique = parts[0]
            condition_type = parts[1]  # 'spacing'或'radius'
            condition_level = parts[2]
            
            # 加载npy数据
            file_path = os.path.join(npy_dir, filename)
            try:
                processed_data = np.load(file_path, allow_pickle=True).item()
            except:
                continue
            
            # 提取需要分析的因变量（可根据需求扩展）
            for dv_name in ['global_avg_selection_time', 'global_error_rate', 'global_H_offset_magnitude']:
                if dv_name in processed_data:
                    data.append({
                        'Technique': technique,
                        'ConditionType': condition_type,
                        'ConditionLevel': condition_level,
                        'DependentVariable': dv_name,
                        'Value': processed_data[dv_name]
                    })
    
    return pd.DataFrame(data)

def run_technique_anova(df):
    # 按因变量和条件类型分组分析
    for (dv, condition), group_df in df.groupby(['DependentVariable', 'ConditionType']):
        print(f"\n=== ANOVA Results for {dv} ({condition}) ===")
        
        art_data = pg.art(
            data=group_df,
            dv='Value',
            between='Technique'
        )
        # 单因素ANOVA (Technique为自变量)
        anova_result = pg.anova(
            data=art_data,
            dv='aligned_rank',
            between='Technique',
            detailed=True
        )
        print(anova_result)
        
        # 事后检验 (Tukey HSD)
        if len(group_df['Technique'].unique()) > 2:
            posthoc = pg.pairwise_tukey(
                data=group_df,
                dv='Value',
                between='Technique'
            )
            print("\nPost-hoc Tukey HSD Results:")
            print(posthoc[['A', 'B', 'mean(A)', 'mean(B)', 'p-tukey', 'hedges']])
        
        # 效应量计算
        eta_sq = anova_result.loc[0, 'np2'] if len(anova_result) > 0 else 0
        print(f"\nEffect Size (η²): {eta_sq:.4f}")
        print("=====================================")

def main():
    numpy_dir = os.path.join(os.path.dirname(__file__), './output_numpy')
    if not os.path.exists(numpy_dir):
        print(f"Error: Directory {numpy_dir} not found!")
        return
    
    # 加载并整合数据
    df = load_technique_data(numpy_dir)
    if df.empty:
        print("No valid data found for ANOVA analysis!")
        return
    
    # 执行ANOVA分析
    run_technique_anova(df)

if __name__ == '__main__':
    main()