> ## ⚠️ This project is archived and no longer maintained.

[![Python application](https://github.com/enriquea/fsspark/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/enriquea/fsspark/actions/workflows/python-app.yml)
[![Python Package using Conda](https://github.com/enriquea/fsspark/actions/workflows/python-package-conda.yml/badge.svg?branch=main)](https://github.com/enriquea/fsspark/actions/workflows/python-package-conda.yml)

# fsspark

---

## Feature selection in Spark

### Description

`fsspark` is a python module to perform feature selection and machine learning based on spark.
Pipelines written using `fsspark` can be divided roughly in four major stages: 1) data pre-processing, 2) univariate 
filters, 3) multivariate filters and 4) machine learning wrapped with cross-validation (**Figure 1**).

![Feature Selection flowchart](images/fs_workflow.png)
**Figure 1**. Feature selection workflow example implemented in fsspark.

### Documentation

The package documentation describes the [data structures](docs/README.data.md) and 
[features selection methods](docs/README.methods.md) implemented in `fsspark`.

### Installation

- pip
```bash
git clone https://github.com/enriquea/fsspark.git
cd fsspark
pip install . -r requirements.txt
```

- conda
```bash
git clone https://github.com/enriquea/fsspark.git
cd fsspark
conda env create -f environment.yml
conda activate fsspark-venv
pip install . -r requirements.txt
```

### Maintainers
- Enrique Audain (https://github.com/enriquea)
- Yasset Perez-Riverol (https://github.com/ypriverol)
