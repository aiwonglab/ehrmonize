import pandas as pd
import numpy as np
import json
from dotenv import load_dotenv
import os
import yaml
import sys

class EHRmonize:

    def __init__(self,
                 model_id, 
                 temperature=0.1,
                 max_tokens=8):
        

        # make sure that model_id is a string and is supported 
        if not isinstance(model_id, str):
            raise ValueError('model_id must be a string')

        # read supported models from YAML file
        with open('supported_models.yaml', 'r') as file:
            supported_models = yaml.safe_load(file)
        
        if model_id not in supported_models:
            raise ValueError(f"model_id not supported. We currently support: {supported_models}")

        # make sure that temperatue is a float between 0 and 1
        if (temperature < 0) | (temperature > 1):
            raise ValueError('temperature must be numeric and between 0 and 1')

        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens

        load_dotenv()


        # OpenAI models
        if self.model_id in ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o']:
            import openai
            openai.api_key = str(os.getenv('OPENAI_API_KEY'))

            self.client = openai.OpenAI(
                api_key = openai.api_key,
            )

        # Bedrock models
        else:
            import boto3
            aws_access_key_id = str(os.getenv('AWS_ACCESS_KEY_ID'))
            aws_secret_access_key = str(os.getenv('AWS_SECRET_ACCESS_KEY'))

            self.client = boto3.client(
                service_name = 'bedrock-runtime',
                region_name = 'us-east-1',
                aws_access_key_id = aws_access_key_id,
                aws_secret_access_key = aws_secret_access_key,
            )

        # set default prompting configuration
        self.n_shots = 0
        self.n_attempts = 1
        self.agentic = False

    # update how prompting is done
    def config_prompting(self, n_shots, n_attempts, agentic):
        self.n_shots = n_shots
        self.n_attempts = n_attempts
        self.agentic = agentic


    def _invoke_bedrock_llama(self,
                        prompt):
        
        body = json.dumps({
            "prompt": "\n\nHuman:" + prompt + "\n\nAssistant: ",
            "max_gen_len": self.max_tokens, 
            "temperature": self.temperature,
            "top_p": 0.9,
        })
        
        response = self.client.invoke_model(body = body,
                                            modelId = self.model_id,
                                            accept = 'application/json',
                                            contentType =  'application/json'
                                            )
        response_body = json.loads(response.get('body').read())

        return response_body.get('generation')
    
    def _invoke_bedrock_claude(self,
                        prompt):
        
        body = json.dumps({
            "prompt": "\n\nHuman:" + prompt + "\n\nAssistant: ",
            "max_tokens_to_sample": self.max_tokens, 
            "temperature": self.temperature,
            "top_p": 0.9,
        })
        
        response = self.client.invoke_model(body = body,
                                            modelId = self.model_id,
                                            accept = 'application/json',
                                            contentType =  'application/json'
                                            )
        response_body = json.loads(response.get('body').read())

        return response_body.get('completion')
    
    def _invoke_bedrock_mistral(self,
                        prompt):
        
        body = json.dumps({
            "prompt": "\n\nHuman:" + prompt + "\n\nAssistant: ",
            "max_tokens": self.max_tokens, 
            "temperature": self.temperature,
            "top_p": 0.9,
        })
        
        response = self.client.invoke_model(body = body,
                                            modelId = self.model_id,
                                            accept = 'application/json',
                                            contentType =  'application/json'
                                            )
        response_body = json.loads(response.get('body').read())

        return response_body.get('outputs')[0].get('text')
    
    
    def _invoke_openai(self,
                       prompt):
          
        response = self.client.chat.completions.create(
            model = self.model_id, 
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens = self.max_tokens, 
            n = 1,
            stop = None,
            temperature = self.temperature,
        )

        return response.choices[0].message.content
    
    def _clean_text(self, text):
        # remove "\n" and spaces
        text = text.replace("\n", " ").strip()
        # transform to lowercase
        text = text.lower()
        # remove any '
        text = text.replace("'", "")
        return text
    
    def _prompt(self, prompt):
        if self.model_id in ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o']:
            try:
                text = self._invoke_openai(prompt=prompt)
            except Exception as e:
                text = 'API failed'
                print(text + ', proceeding...')

            return self._clean_text(text)
                
        elif self.model_id in ['meta.llama2-13b-chat-v1', 'meta.llama2-70b-chat-v1', 'meta.llama3-70b-instruct-v1:0']:
            try:
                text = self._invoke_bedrock_llama(prompt=prompt)
            except Exception as e:
                text = 'API failed'
                print(text + ', proceeding...')
            
            return self._clean_text(text)
        
        elif self.model_id in ['anthropic.claude-v2:1', 'anthropic.claude-instant-v1']:
            try:
                text = self._invoke_bedrock_claude(prompt=prompt)
            except Exception as e:
                text = 'API failed'
                print(text + ', proceeding...')


            return self._clean_text(text)
        
        elif self.model_id in ['mistral.mistral-7b-instruct-v0:2', 'mistral.mixtral-8x7b-instruct-v0:1']:
            try:
                text = self._invoke_bedrock_mistral(prompt=prompt)
            except Exception as e:
                text = 'API failed'
                print(text + ', proceeding...')

            return self._clean_text(text)

        else:
            raise ValueError('model_id not supported. Please make sure you are using the correct model_id. We currently support: \
                             gpt-3.5-turbo, gpt-4, gpt-4o,\
                             meta.llama2-13b-chat-v1, meta.llama2-70b-chat-v1, meta.llama3-70b-instruct-v1:0\
                             anthropic.claude-v2:1, anthropic.claude-instant-v1,\
                             mistral.mistral-7b-instruct-v0:2, mistral.mixtral-8x7b-instruct-v0:1')

    def _run_rule_based(self, results):
        consistency = results.count(max(set(results), key = results.count)) / len(results)

        # see if there is a tie, i.e, more than one class with the same count that are the max
        # while results.count(max(set(results), key = results.count)) <= len(results)/2:
        #     # run prompt again, until there is no tie
        #     results.append(self._get_clean_route(route, classes))

        if consistency <= 0.5:
            return results, 'unsure', consistency
        else:
            return max(set(results), key = results.count), consistency, results

    def _run_agentic(self, previous_prompt, results):

        consistency = results.count(max(set(results), key = results.count)) / len(results)

        prompt = f" \
            You are a well trained, senior clinician who is reviewing the work done by your more junior colleagues\
            who are doing data cleaning and harmonization. This was the task that they received:\
            {previous_prompt}\
            After asking {self.n_attempts} different colleagues, these were their responses:\
            {results}\
            Please decide the final answer to this task.\
            Output nothing more than the final answer, without explaining anything,\
            and write 'unsure' if there is a tie or you are unable to decide.\
        "

        output = self._prompt(
            prompt=('\nHuman: ' + prompt + '\nAssistant:')
        )

        return self._clean_text(output), consistency, results
        

    def _generate_route_prompt(self, route, classes, possible_shots):    

        if self.n_shots == 0:
            prompt = f" \
            You are a well trained clinician doing data cleaning and harmonization. \
            You are given a raw route name, which may contain spelling typos and variations, below within squared brackets[]. \
            Please classify [{route}] into one of the following categories: \
            {classes} \
            Please output nothing more than the category name. \
        "

        else:
            shots = possible_shots[:self.n_shots]

            prompt = f" \
            You are a well trained clinician doing data cleaning and harmonization. \
            You are given a raw route name, which may contain spelling typos and variations, below within squared brackets[]. \
            Please classify [{route}] into one of the following categories: \
            {classes} \
            Consider the following example(s): \
            {shots} \
            Please output nothing more than the category name. \
        "
            

        return prompt

    def _get_generic_route(self, route, classes, possible_shots):

        prompt = self._generate_route_prompt(route, classes, possible_shots)

        output = self._prompt(
            prompt=('\nHuman: ' + prompt + '\nAssistant:')
        )

        return self._clean_text(output)

    def get_generic_route(self, route, classes, possible_shots=[]):

        results = []

        for i in range(self.n_attempts):
            results.append(self._get_generic_route(route, classes, possible_shots))

        # if only one attempt, simply return the result
        if self.n_attempts == 1:
            return results[0]

        # if more than one attempt, return the most common result, or let another agent decide
        else:  
            # first, rule-based approach, return the most common result
            if not self.agentic:
                return self._run_rule_based(results)

            # second, agentic approach, return the result that another LLM decides
            elif self.agentic:
                previous_prompt = self._generate_route_prompt(route, classes, possible_shots)
                return self._run_agentic(previous_prompt, results)

                

    def _generate_generic_name_prompt(self, drugname, possible_shots):

        # For reference, as this prompt would therefore include shots:
        # Remove salt names (e.g., hydromorphone hydrochloride -> hydromorphone) \
        #     unless there are multiple salts with different clinical effects (e.g., metoprolol tartrate and metoprolol succinate). \
        #     Remove prescription strengths (e.g, hydromorphone hydrochloride 1 mg to hydromorphone) \
        #     Include concentrations for intravenous fluids and dextrose solutions \
        #     (e.g., normal saline 0.9% -> sodium chloride 9 MG/ML, dextrose 50% -> glucose 500 MG/ML). \
        #     Please output nothing more than the generic name in lowercase. \

        if self.n_shots == 0:
            prompt = f" \
            You are a well trained clinician doing data cleaning and harmonization. \
            You are given a raw drug name out of EHR, below, within squared brackets[]. \
            Please give me this drug's generic name in accordance with RxNorm standards: [{drugname}] \
            Remove salt names unless there are multiple salts with different clinical effects. \
            Remove prescription strengths. \
            Include concentrations for intravenous fluids and dextrose solutions. \
            Please output nothing more than the generic name in lowercase. \
        "
        else:
            shots = possible_shots[:self.n_shots]

            prompt = f" \
            You are a well trained clinician doing data cleaning and harmonization. \
            You are given a raw drug name out of EHR, below, within squared brackets[]. \
            Please give me this drug's generic name: [{drugname}] \
            Consider the following example(s): \
            {shots} \
            Remove salt names unless there are multiple salts with different clinical effects. \
            Remove prescription strengths. \
            Include concentrations for intravenous fluids and dextrose solutions. \
            Please output nothing more than the generic name in lowercase. \
        "

        return prompt
    
    def _get_generic_name(self, drugname, possible_shots):

        prompt = self._generate_generic_name_prompt(drugname, possible_shots)

        output = self._prompt(
            prompt=('\nHuman: ' + prompt + '\nAssistant:')
        )

        return self._clean_text(output)

    def get_generic_name(self, drugname, possible_shots=[]):
        results = []

        for i in range(self.n_attempts):
            results.append(self._get_generic_name(drugname, possible_shots))

        if self.n_attempts == 1:
            return results[0]

        else:  
            if not self.agentic:
                return self._run_rule_based(results)

            elif self.agentic:
                previous_prompt = self._generate_generic_name_prompt(drugname, possible_shots)
                return self._run_agentic(previous_prompt, results)


    def _generate_drug_classification_prompt(self, drugname, route, classes, possible_shots):

        if self.n_shots == 0:
            
            prompt = f" \
                You are a well trained clinician doing data cleaning and harmonization. \
                You are given a raw drug name and administration route out of EHR, below, within squared brackets as [drugname, route]. \
                Please classify [{drugname}, {route}] into one of the following categories: \
                {classes} \
                Please output nothing more than the category name. \
            "
        else:
            shots = possible_shots[:self.n_shots]

            prompt = f" \
                You are a well trained clinician doing data cleaning and harmonization. \
                You are given a raw drug name and administration route out of EHR, below, within squared brackets as [drugname, route]. \
                Please classify [{drugname}, {route}] into one of the following categories: \
                {classes} \
                Consider the following example(s): \
                {shots} \
                Please output nothing more than the category name. \
            "
        return prompt

    def _get_drug_classification(self, drugname, route, classes, possible_shots):

        prompt = self._generate_drug_classification_prompt(drugname, route, classes, possible_shots)
    
        output = self._prompt(
            prompt=('\nHuman: ' + prompt + '\nAssistant:')
        )

        return self._clean_text(output)


    def classify_drug(self, drugname, route, classes, possible_shots=[]):

        results = []

        for i in range(self.n_attempts):
            results.append(self._get_drug_classification(drugname, route, classes, possible_shots))

        if self.n_attempts == 1:
            return results[0]

        else:  
            if not self.agentic:
                return self._run_rule_based(results)

            elif self.agentic:
                previous_prompt = self._generate_drug_classification_prompt(drugname, route, classes, possible_shots)
                return self._run_agentic(previous_prompt, results)
            
    def _generate_one_hot_drug_classification(self, drugname, route, classif, expanded_classif, possible_shots):

        if self.n_shots == 0:
            prompt = f" \
                You are a well trained clinician doing data cleaning and harmonization. \
                You are given a raw drug name and administration route out of EHR, below, within squared brackets as [drugname, route]. \
                Please output 1 if [{drugname}, {route}] is classified as {classif}, otherwise output 0. \
                {classif} means {expanded_classif}. \
                Please output nothing more than 1 or 0. \
            "
        else:
            shots = possible_shots[:self.n_shots]
            prompt = f" \
                You are a well trained clinician doing data cleaning and harmonization. \
                You are given a raw drug name and administration route out of EHR, below, within squared brackets as [drugname, route]. \
                Please output 1 if [{drugname}, {route}] is classified as {classif}, otherwise output 0. \
                {classif} means {expanded_classif}. \
                Consider the following example(s): \
                {shots} \
                Please output nothing more than 1 or 0. \
            "

        return prompt
    
    def _get_one_hot_drug_classification(self, drugname, route, classif, expanded_classif, possible_shots):
            
            prompt = self._generate_one_hot_drug_classification(drugname, route, classif, expanded_classif, possible_shots)
        
            output = self._prompt(
                prompt=('\nHuman: ' + prompt + '\nAssistant:')
            )
    
            return self._clean_text(output)
    
    def one_hot_drug_classification(self, drugname, route, classif, expanded_classif=None, possible_shots=[]):
            
            results = []
    
            for i in range(self.n_attempts):
                results.append(self._get_one_hot_drug_classification(drugname, route,
                                                                     classif, expanded_classif, possible_shots))
    
            if self.n_attempts == 1:
                return results[0]
    
            else:  
                if not self.agentic:
                    return self._run_rule_based(results)
    
                elif self.agentic:
                    previous_prompt = self._generate_one_hot_drug_classification(drugname, route,
                                                                                 classif, expanded_classif,
                                                                                 possible_shots)
                    return self._run_agentic(previous_prompt, results)
            
    def _generate_custom_prompt(self, prompt, input):
        return f" {prompt} \n {input}"    
        
    def _custom_prompt(self, full_prompt):

        output = self._prompt(
            prompt=('\nHuman: ' + full_prompt + '\nAssistant:')
        )

        return self._clean_text(output)
    
    def custom_task(self, prompt, input):

        full_prompt = self._generate_custom_prompt(prompt, input)

        results = []

        for i in range(self.n_attempts):
            results.append(self._custom_prompt(full_prompt))

        if self.n_attempts == 1:
            return results[0]

        else:  
            if not self.agentic:
                return self._run_rule_based(results)

            elif self.agentic:
                previous_prompt = full_prompt
                return self._run_agentic(previous_prompt, results)

    def set_task(self, task, **kwargs):
        """
        Set the task to be performed by the model.
        
        Parameters
        ----------
        task : str
            The task to be performed.
            We currently support: 'get_generic_route', 'get_generic_name', 'classify_drug', 'one_hot_drug_classification', and 'custom'.
            Additional arguments to be passed to the task function.
            Please find which arguments are necessary for each task in the documentation.

        Returns
        -------
        None
        """

        self.task = task
        self.kwargs = kwargs

    def predict(self, input):
        """
        Predict the output of the specified task.

        Parameters
        ----------
        input : Pandas Series or DataFrame
            The input data. If the task is get_generic_route or get_generic_name, input must be a Pandas Series.
            If the task is classify_drug or one_hot_drug_classification, input must be a Pandas DataFrame.
            "custom" tasks are currently limited to Pandas Series.

        Returns
        -------
        Pandas Series or DataFrame
            The predicted output.
        """

        if self.task == 'get_generic_route':
            # make sure that input is a pandas Series
            if not isinstance(input, pd.Series):
                raise ValueError('input must be a pandas Series')
            
            res = input.apply(
                lambda x: self.get_generic_route(
                    route=x,
                    classes=self.kwargs.get('classes'),
                    possible_shots=self.kwargs.get('possible_shots'),
                )
            )

            if self.n_attempts == 1:
                return res
            
            elif self.n_attempts > 1:
                return {
                    'pred': res.apply(lambda x: x[0]), 
                    'consistency': res.apply(lambda x: x[1]), 
                    'all_pred': res.apply(lambda x: x[2]) 
                }

        elif self.task == 'get_generic_name':
            # make sure that input is a pandas Series
            if not isinstance(input, pd.Series):
                raise ValueError('input must be a pandas Series')
            
            res = input.apply(
                lambda x: self.get_generic_name(
                    drugname=x,
                    possible_shots=self.kwargs.get('possible_shots'),
                )
            )

            if self.n_attempts == 1:
                return res
            
            elif self.n_attempts > 1:
                return {
                    'pred': res.apply(lambda x: x[0]),
                    'consistency': res.apply(lambda x: x[1]),
                    'all_pred': res.apply(lambda x: x[2])
                }
        
        elif self.task == 'classify_drug':
            # make sure that input is a pandas DataFrame
            if not isinstance(input, pd.DataFrame):
                raise ValueError('input must be a pandas DataFrame')
                        
            res = input.apply(
                lambda row: self.classify_drug(
                    drugname=row.iloc[0],
                    route=row.iloc[1],
                    classes=self.kwargs.get('classes'),
                    possible_shots=self.kwargs.get('possible_shots'),
                ),
                axis=1
            )

            if self.n_attempts == 1:
                return res
            
            elif self.n_attempts > 1:
                return {
                    'pred': res.apply(lambda x: x[0]),
                    'consistency': res.apply(lambda x: x[1]),
                    'all_pred': res.apply(lambda x: x[2])
                }
            
        elif self.task == 'one_hot_drug_classification':
            # make sure that input is a pandas DataFrame
            if not isinstance(input, pd.DataFrame):
                raise ValueError('input must be a pandas DataFrame')
            
            res = input.apply(
                lambda row: self.one_hot_drug_classification(
                    drugname=row.iloc[0],
                    route=row.iloc[1],
                    classif=self.kwargs.get('classif'),
                    expanded_classif=self.kwargs.get('expanded_classif'),
                    possible_shots=self.kwargs.get('possible_shots'),
                ),
                axis=1
            )

            if self.n_attempts == 1:
                return res
            
            elif self.n_attempts > 1:
                return {
                    'pred': res.apply(lambda x: x[0]),
                    'consistency': res.apply(lambda x: x[1]),
                    'all_pred': res.apply(lambda x: x[2])
                }
            
        elif self.task == 'custom':
            # make sure that input is a pandas Series
            if not isinstance(input, pd.Series):
                raise ValueError('input must be a pandas Series')
            
            res = input.apply(
                lambda x: self.custom_task(
                    prompt=self.kwargs.get('prompt'),
                    input=x,
                )
            )

            if self.n_attempts == 1:
                return res
            
            elif self.n_attempts > 1:
                return {
                    'pred': res.apply(lambda x: x[0]),
                    'consistency': res.apply(lambda x: x[1]),
                    'all_pred': res.apply(lambda x: x[2])
                }
    
        else:
            raise ValueError('task not supported. Please make sure you are using the correct task. We currently support: \
                             get_generic_route, get_generic_name, classify_drug, custom')
        
    def accuracy_score(self, y_true, y_pred):
        """
        Compute the accuracy score.
        Defined as the proportion of true labels that are exactly equal to the predicted labels.

        Parameters
        ----------
        y_true : Pandas Series
            The true labels.
        y_pred : Pandas Series
            The predicted labels.

        Returns
        -------
        float
            The accuracy score.
        """
        return np.mean(y_true == y_pred)
    
    def recall_score(self, y_true, y_pred):
        """
        Compute the recall score.
        Defined as the proportion of true positive labels that are correctly identified.
        
        Parameters
        ----------
        y_true : Pandas Series
            The true labels.
        y_pred : Pandas Series
            The predicted labels.

        Returns
        -------
        float
            The recall score.
            
        """
        tp = np.sum((y_true == '1') & (y_pred == '1'))
        fn = np.sum((y_true == '1') & (y_pred == '0'))
        return tp / (tp + fn)
    
    def precision_score(self, y_true, y_pred):
        """
        Compute the precision score.
        Defined as the proportion of true positive labels that are correctly identified.

        Parameters
        ----------
        y_true : Pandas Series
            The true labels.
        y_pred : Pandas Series
            The predicted labels.
        Returns
        -------
        float
            The precision score.
        """
        tp = np.sum((y_true == '1') & (y_pred == '1'))
        fp = np.sum((y_true == '0') & (y_pred == '1'))
        return tp / (tp + fp)

    def f1_score(self, y_true, y_pred):
        """
        Compute the F1 score.
        Defined as the harmonic mean of precision and recall.

        Parameters
        ----------
        y_true : Pandas Series
            The true labels.
        y_pred : Pandas Series
            The predicted labels.
        Returns
        -------
        float
            The F1 score.
        """
        recall = self.recall_score(y_true, y_pred)
        precision = self.precision_score(y_true, y_pred)
        return 2 * (precision * recall) / (precision + recall)
    
    def specificity_score(self, y_true, y_pred):
        """
        Compute the specificity score.
        Defined as the proportion of true negative labels that are correctly identified.
        
        Parameters
        ----------
        y_true : Pandas Series
            The true labels.
        y_pred : Pandas Series
            The predicted labels.
        Returns
        -------
        float
            The specificity score.
        """
        return np.sum((y_true == '0') & (y_pred == '0')) / np.sum(y_true == '0')
    
    def balanced_accuracy_score(self, y_true, y_pred):
        """
        Compute the balanced accuracy score.
        Defined as the average of recall and specificity scores.

        Parameters
        ----------
        y_true : Pandas Series
            The true labels.
        y_pred : Pandas Series
            The predicted labels.
        Returns
        -------
        float
            The balanced accuracy score.        
        """
        recall = self.recall_score(y_true, y_pred)
        specificity = self.specificity_score(y_true, y_pred)
        return (recall + specificity) / 2
    

    def evaluate(self, y_true, y_pred, experiment_number=0):
        """
        Evaluate the model performance using the specified metrics.

        Parameters
        ----------
        y_true : Pandas Series
            The true labels.
        y_pred : Pandas Series
            The predicted labels.
        experiment_number : int
            The experiment number (necessary for the indexation of the output DataFrame).

        Returns
        -------
        Pandas DataFrame
            A DataFrame with the evaluation metrics.

        """

        y_true = y_true.astype(str)
        y_pred = y_pred.astype(str)

        metric_dict = {}

        for m in self.kwargs.get('metrics'):
            metric_dict[m] = np.round(getattr(self, m)(y_true, y_pred), 3)

        return pd.DataFrame(metric_dict, index=[experiment_number])

