### Integration with Google Cloud Platform (GCP)

In this section, we explain how to set up GCP and your environment in order to run SQL queries through GCP right from your local Python setting. Follow these steps:

1) Create a Google account if you don't have one and go to [Google Cloud Platform](https://console.cloud.google.com/bigquery)
2) Enable the [BigQuery API](https://console.cloud.google.com/apis/api/bigquery.googleapis.com)
3) Create a [Service Account](https://console.cloud.google.com/iam-admin/serviceaccounts), where you can download your JSON keys
4) Place your JSON keys in the parent folder (for example) of your project
5) Create a .env file with the command `nano .env` or `touch .env` for Mac and Linux users or `echo. >  .env` for Windows.
6) Update your .env file with your ***JSON keys*** path and the ***id*** of your project in BigQuery

Follow the format:

```sh
BIGQUERY_KEYS_FILE = "../GoogleCloud_keys.json"
BIGQUERY_PROJECT_ID = "project-id"
```

After getting credentialing at PhysioNet, you must sign the data use agreement and connect the database with GCP, either asking for permission or uploading the data to your project. Please note that only MIMIC v2.0 is available at GCP.

Having all the necessary tables for the cohort generation query in your project, run the following command to fetch the data as a dataframe that will be saved as CSV in your local project. Make sure you have all required files and folders, and run this in the root of the project. 

This is an example to run the `mimic_meds.sql` query, which will be saved under the same name:

```sh
python3 dataset/get_bigquery_data.py --sql "dataset/queries/mimic_meds.sql" --destination "dataset/unlabeled/mimic_meds.csv"
```

In case you're interested in running a batch of queries, i.e, all the queries that are within a folder, run the following command:

```sh
python3 dataset/get_bigquery_data.py --sql_folder "dataset/queries/" --destination_folder "dataset/unlabeled/"
```

### Run Experiments

1. Set the .YAML configuration file in the `experiments/config/` folder

2. Run the following command

```sh
python3 run_experiment.py --experiment {name_of_experiment/config}
```

As an example,

```sh
python3 run_experiment.py --experiment one_hot_antibiotic
```

will run the experiment defined in `experiments/config/one_hot_antibiotic.yaml`.


### Run sh file

```sh
sh '/Users/joaomatos/Documents/ehrmonize/experiments/sh/figure3.sh'
```