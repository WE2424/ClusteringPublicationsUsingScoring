from sqlalchemy import create_engine
import pyodbc
import pandas as pd
import yaml

class Repository:
    def __init__(self, cfg):
        self.cfg = cfg

    def get(self):
        if (self.cfg['useDb']):
            return self.get_from_db()
        return self.get_sample()

    def get_from_db(self):
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + self.cfg['server'] + ';DATABASE=' + self.cfg['database'] + ';UID=' + self.cfg['username'] + ';PWD=' + self.cfg['password'])
        sql_query = "SELECT * FROM patstat_golden_set"
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return df

    def post(self, extracted_bibliographic_items, clusters_of_name_variants, precision_recall_f1_analysis):
        connection_string = f"mssql+pyodbc://{self.cfg['username']}:{self.cfg['password']}@{self.cfg['server']}/{self.cfg['database']}?driver=ODBC Driver 17 for SQL Server"
        engine = create_engine(connection_string)
        extracted_bibliographic_items.to_sql('extracted_bibliographic_items_group10', con=engine, if_exists='replace', index=False)
        (clusters_of_name_variants.astype(str)).to_sql('clusters_of_name_variants_group10', con=engine, if_exists='replace', index=False)
        precision_recall_f1_analysis.to_sql('precision_recall_f1_analysis_group10', con=engine, if_exists='replace', index=False)
        engine.dispose()

    def get_sample(self):
        with open('samples/sample.yaml') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        return pd.DataFrame(data)