#README P3 Submission 250031439

##This submission includes the following directories:

1. **notebooks**
- censis-ni-2021.ipynb - report in Jupyter Notebook format
- censis-ni-2021.html - HTML version of the report

2. **code**
- notebook_to_html.py - script that automates the conversion process from .ipynb to .html
- refine.py - script that refines the provided dataset

4. **data**
- census-2021-public-microdata-teaching-sample.csv - dataset used for the analysis
- data_dictionary.json - variable codes and values also used in the analysis
- refined_census_data.csv - clean versin of original dataset
- another directory describing the details aout the dataset

##Installation Instructions

To successfully run the **notebook_to_html.py** script and replicate the HTML report, you need a Python environment with the following dependencies installed:

### `nbconvert` and `nbformat` for notebook conversion
 
**Installation Command via pip:**
```bash
pip install pandas numpy matplotlib jupyter nbconvert