from ehrmonize import EHRmonize
import argparse
import os
import yaml
import pandas as pd
import numpy as np
import warnings
import time
warnings.filterwarnings("ignore")


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", help="Insert the experiment's name")
    parser.add_argument("--experiments", help="Insert the experiment's name")
    return parser.parse_args()


def load_config(experiments, task):

    with open(f'experiments/configs/{experiments}.yaml', 'r') as file:
        for key, value in yaml.safe_load(file).items():
            globals()[key] = value

    engines = []
    promptings = []

    for m in model_id:
        for t in temperature:

            engines.append({'model_id': m, 'temperature': t})

    for n_s in number_of_shots:
        for n_a in number_of_attempts:
            
            if n_a == 1:
                agentic_loop = [False]

            elif n_a > 1:
                agentic_loop = agentic

            for a in agentic_loop:
                promptings.append({'n_shots': n_s, 'n_attempts': n_a, 'agentic': a})

    data_settings = []

    with open(f'experiments/configs/{task}.yaml', 'r') as file:
        for key, value in yaml.safe_load(file).items():
            globals()[key] = value

    for db, path, inp, gt in zip(source_db, source_csv, input_col_name, gt_col_name):
        data_settings.append({'source_db': db, 'source_csv': path, 'input_col_name': inp, 'gt_col_name': gt})

    return engines, promptings, data_settings


def run_experiment(experiments, task):
    engines, promptings, data_settings = load_config(experiments, task)

    print(f"Running {task}...")

    results = pd.DataFrame()
    # results = pd.read_csv(f"experiments/metrics/{experiments}/{task}.csv")
    for d in data_settings:

        data = pd.read_csv(d['source_csv'])

        if not isinstance(d['input_col_name'], list):
            # rename columns from input_col_name to 'drug', 'route'
            data_to_save = data[[d['input_col_name'],d['gt_col_name']]]
        else:
            data_to_save = data[d['input_col_name'] + [d['gt_col_name']]]

        for e in engines:
            ehrm = EHRmonize(**e)

            for p in promptings: #add tqdm here

                iter_number = len(results) + 1
                start_time = time.time()
                ehrm.config_prompting(**p)
                ehrm.set_task(**task_specific)

                if p['n_attempts'] == 1:
                    preds = ehrm.predict(data[d['input_col_name']])
                    consistencies = np.nan
                    # save predictions
                    data_to_save[f'pred_{iter_number}'] = preds

                elif p['n_attempts'] > 1:
                    res = ehrm.predict(data[d['input_col_name']])
                    preds = res['pred']
                    try:
                        consistencies = res['consistency'].mean()
                    except Exception as excp:
                        consistencies = np.nan
                        print(excp)
                    # save predictions
                    data_to_save[f'pred_{iter_number}'] = preds
                    data_to_save[f'all_pred_{iter_number}'] = res['all_pred']
                    data_to_save[f'consistency_{iter_number}'] = res['consistency']

                data_to_save.to_csv(f"experiments/results/{experiments}/{task}_{d['source_db']}.csv", index=False)
                
                metrics = ehrm.evaluate(data[d['gt_col_name']], preds, iter_number)

                meta_metrics = pd.DataFrame({
                    'elapsed_time': [np.round(time.time() - start_time, 3)],
                    'consistencies': [np.round(consistencies, 3)]
                }, index=[iter_number])

                results = pd.concat([
                    results,
                    pd.concat([
                        pd.DataFrame({'db': d['source_db']}, index=[iter_number]), # data settings
                        pd.DataFrame(e, index=[iter_number]), # engine
                        pd.DataFrame(p, index=[iter_number]), # prompting
                        meta_metrics,
                        metrics
                    ], axis=1)
                ], axis=0)

                results.to_csv(f"experiments/metrics/{experiments}/{task}.csv", index=False)


if __name__ == '__main__':

    args = arg_parser()
    run_experiment(args.experiments, args.task)