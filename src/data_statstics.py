from calendar import c
import numpy as np
import argparse
import json
from scipy import stats
import pandas as pd
import pingouin as pg
from statsmodels.stats.anova import AnovaRM
import os
import art



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
            
            for dv_name in ['global_avg_selection_time', 'global_error_rate', 'global_H_offset_magnitude']:
                if dv_name in processed_data:
                    dv_value = processed_data[dv_name]
                    if np.isscalar(dv_value):
                        data.append({
                            'Subject': f"S0",  # Single subject for scalar value
                            'Technique': technique,
                            'ConditionType': condition_type,
                            'ConditionLevel': str(condition_level),
                            'DependentVariable': dv_name,
                            'Value': dv_value
                        })
                    else:
                        for subject_id, value in enumerate(dv_value):
                            data.append({
                                'Subject': f"S{subject_id}",  # Subject 必须为 categorical
                                'Technique': technique,
                                'ConditionType': condition_type,
                                'ConditionLevel': str(condition_level),
                                'DependentVariable': dv_name,
                                'Value': value
                            })
    return pd.DataFrame(data)

def run_art_rm_anova(df):
    for (dv, condition), group_df in df.groupby(['DependentVariable', 'ConditionType']):
        print(f"\n=== ART + RM-ANOVA for {dv} ({condition}) ===")

        # 检查是否包含 Subject 列
        if 'Subject' not in group_df.columns:
            print("Missing 'Subject' column for RM-ANOVA. Skipping...")
            continue

        # 将数据传入 R 环境
        with localconverter(default_converter + pandas2ri.converter):
            r_df = pandas2ri.py2rpy(group_df)
            robjects.globalenv['data'] = r_df

        robjects.r(f'''
        library(ARTool)
        library(emmeans)

        model <- art(Value ~ Technique + (1|Subject), data=data)
        art_anova <- anova(model)

        # Bonferroni pairwise comparisons
        pairwise_result <- emmeans(model, pairwise ~ Technique, adjust = "bonferroni")
        ''')

        print(robjects.r('art_anova'))
        print(robjects.r('pairwise_result'))

def run_technique_anova(df):
    # 按因变量和条件类型分组分析
    for (dv, condition), group_df in df.groupby(['DependentVariable', 'ConditionType']):
        print(f"\n=== ANOVA Results for {dv} ({condition}) ===")
        
        # 单因素ANOVA (Technique为自变量)
        anova_result = pg.anova(
            data=group_df,
            dv='Value',
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

def load_json_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def convert_json_to_anova_format(input_dir, output_csv):
    all_data = []
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]

    for filename in json_files:
        file_path = os.path.join(input_dir, filename)
        try:
            # 加载JSON数据
            data = load_json_data(file_path)
            if not data:
                continue
            
            # 提取关键信息并添加到总数据列表
            for entry in data:
                
                # 基础参数
                base_info = {
                    'technique': entry.get('inputtechnique', 'unknown'),
                    'radius': entry.get('radius', 0),
                    'distance': entry.get('distance', 0),
                    'spacing': entry.get('spacing', 0),
                    'username': entry.get('username', 'unknown')
                }

                observation = {
                    **base_info,
                    'click_duration': entry.get('clickDuration', 0),
                    'is_correct': entry.get('isCorrect', 0),
                    'heisenberg_error': entry.get('HeisenbergError', 0),
                    'heisenberg_angle': entry.get('HeisenbergAngle', 0)
                    }
                all_data.append(observation)

                    
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {str(e)}")
            continue

    # 转换为DataFrame并保存
    df = pd.DataFrame(all_data)
    def filter_outliers(group):
        mean = group['click_duration'].mean()
        std = group['click_duration'].std()
        upper_bound = mean + 3 * std
        mask = (
            (group['click_duration'] >= 0.05) & 
            (group['click_duration'] <= upper_bound) & 
            (group['heisenberg_angle'] >= 0.02)
        )
        return group[mask]

    filtered_df = df.groupby(['technique', 'radius', 'spacing']).apply(filter_outliers).reset_index(drop=True)
    
    normality_results = []
    def perform_normality_test(group):
        condition = (
            f"tech:{group['technique'].iloc[0]}, "
            f"radius:{group['radius'].iloc[0]}, "
            f"spacing:{group['spacing'].iloc[0]}"
        )
        if len(group) >= 3:
            # 使用原始数据进行检验，不做任何筛选
            sw_stat, sw_p = stats.shapiro(group['click_duration'])
            
            # 判断是否符合正态分布 (p>0.05为符合)
            is_normal = sw_p > 0.05
            normality_results.append({
                'technique': group['technique'].iloc[0],
                'radius': group['radius'].iloc[0],
                'spacing': group['spacing'].iloc[0],
                'sample_size': len(group),
                'shapiro_w': round(sw_stat, 4),
                'p_value': round(sw_p, 4),
                'is_normal': is_normal
            })
            
            # 打印检验结果
            print(f"Shapiro-Wilk检验: {condition} | W={sw_stat:.4f}, p={sw_p:.4f} | {'' if is_normal else '不'}符合正态分布")
        else:
            print(f"Shapiro-Wilk检验: {condition} | 样本量不足(n={len(group)})，无法检验")

        return group

    filtered_df.groupby([
        'technique', 'radius', 'spacing', 'distance'
    ], group_keys=False).apply(perform_normality_test)

    filtered_df.to_csv(output_csv, index=False)
    print(f"所有数据已合并并过滤至: {output_csv}")
    print(f"过滤前记录数: {len(df)}, 过滤后记录数: {len(filtered_df)}")
    return filtered_df

def main():
    input_json = './output_stats/'
    output_csv = './output_csv/' + "csv_files.csv"
    
    convert_json_to_anova_format(input_json, output_csv)
    
    df = pd.read_csv(output_csv)

    target_radius = 0.21
    target_spacing = 0.3
    # BareHandIntenSelect BareHandTracking ControllerIntenSelect ControllerTracking
    target_tech = "BareHandIntenSelect"

    output_radius_csv = './output_csv/' + "csv_files_radius"+ "_021"+".csv"
    output_spacing_csv = './output_csv/' + "csv_files_spacing"+ "_03"+".csv"
    output_tech_csv = './output_csv/' + "csv_files_tech"+ "_"+"BareHandIntenSelect"+".csv"

    df_filtered = df[df['radius'] == target_radius].copy()
    df_filtered.to_csv(output_radius_csv, index=False)

    df_filtered_spacing = df[df['spacing'] == target_spacing].copy()
    df_filtered_spacing.to_csv(output_spacing_csv, index=False)

    df_filtered_tech = df[df['technique'] == target_tech].copy()
    df_filtered_tech.to_csv(output_tech_csv, index=False)

    df = df_filtered_tech
    df_agg = df.groupby(['username', 'spacing'])['is_correct'].mean().reset_index()

    print(df_agg)


    aovrm = AnovaRM(data=df_agg, depvar='is_correct', subject='username',
                    within=['spacing']) 
    fit = aovrm.fit()

    print(fit)

    posthoc_ttest = pg.pairwise_tests(dv='is_correct',      # 因变量
                                   within='spacing',         # 重复测量因子
                                   subject='username',         # 被试ID
                                   data=df_agg,
                                   padjust='bonf')             # 多重比较校正方法，例如 bonferroni
    print(posthoc_ttest.to_string())  


if __name__ == '__main__':
    main()