import argparse
import os
from dotenv import load_dotenv
from google.cloud import bigquery
import warnings
warnings.filterwarnings("ignore")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sql_folder", help="Insert your queries folder's path, if interested in a batch of queries")
    parser.add_argument("--destination_folder", help="Insert your destination folder's path, if interested in a batch of queries")
    parser.add_argument("--sql", help="Insert your SQL query's path")
    parser.add_argument("--destination", help="Insert your pulled data's destination path")

    return parser.parse_args()

# Run Query to get a DataFrame from BigQuery
def run_query(sql_query_path):

    # Load env file 
    load_dotenv()

    # Get GCP's secrets
    BIGQUERY_KEYS_FILE = os.getenv("BIGQUERY_KEYS_FILE")
    BIGQUERY_PROJECT_ID = os.getenv("BIGQUERY_PROJECT_ID")

    # Set environment variables
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = BIGQUERY_KEYS_FILE

    # Establish connection with BigQuery
    BigQuery_client = bigquery.Client()

    # Read query
    with open(sql_query_path, 'r') as fd:
        query = fd.read()

    # Replace the project id by the coder's project id in GCP
    my_query = query.replace("physionet-data", BIGQUERY_PROJECT_ID).replace("db_name", BIGQUERY_PROJECT_ID, -1)

    # Make request to BigQuery with our query
    df = BigQuery_client.query(my_query).to_dataframe()

    return df


def batch_run(queries_folder, destination_folder):

    # read all files in the folder that end with .sql
    queries = [f for f in os.listdir(queries_folder) if f.endswith('.sql')]

    # run all queries in the folder
    for query in queries:
        print(f"Running query: {query}")
        df = run_query(queries_folder + query)
        df.to_csv(destination_folder + query.replace('.sql', '.csv'))


if __name__ == '__main__':

    args = parse_args()

    if args.sql_folder and args.destination_folder:
        batch_run(queries_folder=args.sql_folder, destination_folder=args.destination_folder)
        exit()
    
    elif args.sql and args.destination:
        df = run_query(sql_query_path = args.sql)
        df.to_csv(args.destination)