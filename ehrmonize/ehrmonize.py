import pandas as pd
import json
from dotenv import load_dotenv
import os

load_dotenv()

class EHRmonize:

    def __init__(self,
                 model_id, 
                 temperature=0.1,
                 max_tokens=8):
        
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens

        if self.model_id in ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o']:
            import openai
            openai.api_key = str(os.getenv('OPENAI_API_KEY'))

            self.client = openai.OpenAI(
                api_key = openai.api_key,
            )

        # elif self.model_id in ['anthropic.claude-v2','meta.llama3-8b-instruct-v1:0']:
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


    def _invoke_bedrock_llama(self,
                        prompt):
        
        body = json.dumps({
            "prompt": "\n\nHuman:" + prompt + "\n\nAssistant: ",
            "max_gen_len": self.max_tokens, # this seems to be a bug that is not solved
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
            "max_tokens": self.max_tokens, # this seems to be a bug that is not solved
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
            return self._clean_text(self._invoke_openai(prompt=prompt))
        
        elif self.model_id in ['meta.llama2-13b-chat-v1', 'meta.llama2-70b-chat-v1', 'meta.llama3-70b-instruct-v1:0']:
            return self._clean_text(self._invoke_bedrock_llama(prompt=prompt))
        
        elif self.model_id in ['anthropic.claude-v2:1', 'anthropic.claude-instant-v1']:
            return self._clean_text(self._invoke_bedrock_claude(prompt=prompt))
        
        elif self.model_id in ['mistral.mistral-7b-instruct-v0:2', 'mistral.mixtral-8x7b-instruct-v0:1']:
            return self._clean_text(self._invoke_bedrock_mistral(prompt=prompt))

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
            return results, max(set(results), key = results.count), consistency

    def _run_agentic(self, previous_prompt, n_attempts, results):

        consistency = results.count(max(set(results), key = results.count)) / len(results)

        prompt = f" \
            You are a well trained, senior clinician who is reviewing the work done by your more junior colleagues\
            who are doing data cleaning and harmonization. This was the task that they received:\
            {previous_prompt}\
            After asking {n_attempts} different colleagues, these were their responses:\
            {results}\
            Please decide the final answer to this task.\
            Output nothing more than the final answer, without explaining anything,\
            and write 'unsure' if there is a tie or you are unable to decide.\
        "

        output = self._prompt(
            prompt=('\nHuman: ' + prompt + '\nAssistant:')
        )

        return results, self._clean_text(output), consistency
        

    def _generate_route_prompt(self, route, classes, nshots):    

        if len(nshots) == 0:
            prompt = f" \
            You are a well trained clinician doing data cleaning and harmonization. \
            You are given a raw route name, which may contain spelling typos and variations, below within squared brackets[]. \
            Please classify [{route}] into one of the following categories: \
            {classes} \
            Please output nothing more than the category name. \
        "

        else:
            prompt = f" \
            You are a well trained clinician doing data cleaning and harmonization. \
            You are given a raw route name, which may contain spelling typos and variations, below within squared brackets[]. \
            Please classify [{route}] into one of the following categories: \
            {classes} \
            Consider the following example(s): \
            {nshots} \
            Please output nothing more than the category name. \
        "
            

        return prompt

    def _get_clean_route(self, route, classes, nshots):

        prompt = self._generate_route_prompt(route, classes, nshots)

        output = self._prompt(
            prompt=('\nHuman: ' + prompt + '\nAssistant:')
        )

        return self._clean_text(output)

    def clean_route(self, route, classes, n_attempts=5, agentic=False, nshots=[]):

        results = []

        for i in range(n_attempts):
            results.append(self._get_clean_route(route, classes, nshots))

        # if only one attempt, simply return the result
        if n_attempts == 1:
            return results[0]

        # if more than one attempt, return the most common result, or let another agent decide
        else:  
            # first, rule-based approach, return the most common result
            if not agentic:
                return self._run_rule_based(results)

            # second, agentic approach, return the result that another LLM decides
            elif agentic:
                previous_prompt = self._generate_route_prompt(route, classes, nshots)
                return self._run_agentic(previous_prompt, n_attempts, results)

                

    def _generate_generic_name_prompt(self, drugname, nshots):

        if len(nshots) == 0:
            prompt = f" \
            You are a well trained clinician doing data cleaning and harmonization. \
            You are given a raw drug name out of EHR, below, within squared brackets[]. \
            Please give me this drug's generic name: [{drugname}] \
            Please output nothing more than the generic name. \
        "
        else:
            prompt = f" \
            You are a well trained clinician doing data cleaning and harmonization. \
            You are given a raw drug name out of EHR, below, within squared brackets[]. \
            Please give me this drug's generic name: [{drugname}] \
            Consider the following example(s): \
            {nshots} \
            Please output nothing more than the generic name. \
        "

        return prompt
    
    def _get_generic_name(self, drugname, nshots):

        prompt = self._generate_generic_name_prompt(drugname, nshots)

        output = self._prompt(
            prompt=('\nHuman: ' + prompt + '\nAssistant:')
        )

        return self._clean_text(output)

    def get_generic_name(self, drugname, n_attempts=5, agentic=False, nshots=[]):
        results = []

        for i in range(n_attempts):
            results.append(self._get_generic_name(drugname, nshots))

        if n_attempts == 1:
            return results[0]

        else:  
            if not agentic:
                return self._run_rule_based(results)

            elif agentic:
                previous_prompt = self._generate_generic_name_prompt(drugname, nshots)
                return self._run_agentic(previous_prompt, n_attempts, results)


    def _generate_drug_classification_prompt(self, drugname, route, classes, nshots):

        if len(nshots) == 0:
            
            prompt = f" \
                You are a well trained clinician doing data cleaning and harmonization. \
                You are given a raw drug name and administration route out of EHR, below, within squared brackets as [drugname, route]. \
                Please classify [{drugname}, {route}] into one of the following categories: \
                {classes} \
                Please output nothing more than the category name. \
            "
        else:
            prompt = f" \
                You are a well trained clinician doing data cleaning and harmonization. \
                You are given a raw drug name and administration route out of EHR, below, within squared brackets as [drugname, route]. \
                Please classify [{drugname}, {route}] into one of the following categories: \
                {classes} \
                Consider the following example(s): \
                {nshots} \
                Please output nothing more than the category name. \
            "
        return prompt

    def _get_drug_classification(self, drugname, route, classes, nshots):

        prompt = self._generate_drug_classification_prompt(drugname, route, classes, nshots)
    
        output = self._prompt(
            prompt=('\nHuman: ' + prompt + '\nAssistant:')
        )

        return self._clean_text(output)


    def classify_drug(self, drugname, route, classes, n_attempts=5, agentic=False, nshots=[]):

        results = []

        for i in range(n_attempts):
            results.append(self._get_drug_classification(drugname, route, classes, nshots))

        if n_attempts == 1:
            return results[0]

        else:  
            if not agentic:
                return self._run_rule_based(results)

            elif agentic:
                previous_prompt = self._generate_drug_classification_prompt(drugname, route, classes, nshots)
                return self._run_agentic(previous_prompt, n_attempts, results)
        
