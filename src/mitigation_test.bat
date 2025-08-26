REM no check for the existence of the directory

python .\extract_training_data.py --tech=DC
python .\extract_training_data.py --tech=SC
python .\extract_training_data.py --tech=DH
python .\extract_training_data.py --tech=SH

python .\extract_training_adaptive_data.py --tech=DC
python .\extract_training_adaptive_data.py --tech=SC
python .\extract_training_adaptive_data.py --tech=DH
python .\extract_training_adaptive_data.py --tech=SH

@REM python  mitigation_strategy_VOTE.py --tech DC
@REM python  .\mitigation_strategy_VOTE.py --tech SC
@REM python  .\mitigation_strategy_VOTE.py --tech DH
@REM python  .\mitigation_strategy_VOTE.py --tech SH