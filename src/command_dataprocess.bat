REM no check for the existence of the directory

python data_preprocess.py --tech DC
python data_preprocess.py --tech SC
python data_preprocess.py --tech DH
python data_preprocess.py --tech SH

REM also no check for the existence of the technology type for data analysis

python data_analysis.py --tech DC
python data_analysis.py --tech SC
python data_analysis.py --tech DH
python data_analysis.py --tech SH

REM Drawing Images
python draw_figure.py