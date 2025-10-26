from lib.clustering import Clustering
from lib.cleaning import clean_data
from lib.evaluation import f1_measure_top100, output
from lib.DAL import Repository
import yaml


def main():
    with open('.config/config.yaml') as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)

        repo = Repository(cfg['dbAccess'])
        df = repo.get()
        extracted_bibliographic_items = clean_data(df)
        clusters_of_name_variants = Clustering(cfg['jaccard_threshold_words'], cfg['column_titles'], cfg['threshold'], cfg['weights']).cluster_data(extracted_bibliographic_items)
        precision_recall_f1_analysis = f1_measure_top100(df,clusters_of_name_variants)
        output(precision_recall_f1_analysis)

        if (repo.cfg['useDb']):
            repo.post(extracted_bibliographic_items, clusters_of_name_variants, precision_recall_f1_analysis)

if __name__ == '__main__':
    main()
