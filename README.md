# Clustering Publications Using Scoring

Clustering Publications Using Scoring is a Python solution for clustering publications from [PATSTAT](https://www.epo.org/en/searching-for-patents/business/patstat). The goal of this solution is to transform unstructured data into structured properties, and cluster entries based on their similarity. For PATSTAT, the solution achieves an [F1 score](https://en.wikipedia.org/wiki/F-score) of 98.8%.

- [Features](#features)
  - [Cleaning](#cleaning)
  - [Clustering](#clustering)
  - [Evaluation](#evaluation)
- [Requirements](#requirements)
  - [Python](#python)
  - [SQL (optional)](#sql-optional)
- [Getting Started](#getting-started)
- [License](#license)

## Features

### Cleaning
The solution cleans the publications and extracts structured information such as authors, titles, and page numbers using regular expressions.

### Clustering
The solution implements a custom algorithm to cluster the publications. It uses the [Jaccard index](https://en.wikipedia.org/wiki/Jaccard_index) to assign a score to the properties of the publication. A publication is added to a cluster if its score exceeds a certain threshold, otherwise a new cluster is formed.

### Evaluation
The solution evaluates the found clusters against a gold standard. It calculates cluster-level precision, recall and F1 scores using the overlap of entries within corresponding clusters. The [summary statistics](outputs/analysis_precision-recall-f1.xlsx) and a [scatter plot](outputs/plot_for_precision-recall-f1_scores.pdf) of F1 scores are also included.

## Requirements

### Python
Python version 3.11+ is required.

The following external packages are used:
- pyodbc
- pandas
- numpy
- matplotlib
- sqlalchemy
- pyyaml

### SQL (optional)
The original solution uses an SQL database with a table named `patstat_golden_set`, which contains clustered PATSTAT data with following columns: 
- `cluster_id`. The correct cluster used to check the final solution.
- `npl_publn_id`. The unique ID for the publication entry.
- `npl_biblio`. The publication.

Since PATSTAT is not freely available, the current solution uses a sample not related to PATSTAT. The solution can be configured to use an SQL database.

In `config.yaml`, update `dbAccess` to use the SQL database.

## Getting Started

1. Clone the repository

```bash
git clone https://github.com/WE2424/ClusteringPublicationsUsingScoring.git
cd ClusteringPublicationsUsingScoring
```
2. Install the dependencies

```bash
pip install -r dep/requirements.txt
```

3. Run the solution

```bash
python src/main.py
```

## License
[MIT License](LICENSE.md)