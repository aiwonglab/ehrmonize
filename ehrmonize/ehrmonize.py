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
        return text.lower()
    
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
        

    def clean_route(self, route):

        prompt = f" \
            You are a well trained clinician doing data cleaning and harmonization. \
            You are given a raw route name, below, within squared brackets[]. \
            Please classify [{route}] into one of the following categories: \
            - intravenous (which includes IV, intraven, or other mispelled variations) \
            - oral (which includes PO) \
            - other (which includes all other routes) \
            Please output nothing more than the category name. \
        "

        output = self._prompt(
            prompt=('\nHuman: ' + prompt + '\nAssistant:')
        )

        return self._clean_text(output)
    
    def get_generic(self, drugname):

        prompt = f" \
            You are a well trained clinician doing data cleaning and harmonization. \
            You are given a raw drug name out of EHR, below, within squared brackets[]. \
            Please give me this drug's generic name: [{drugname}] \
            Please output nothing more than the generic name. \
        "

        output = self._prompt(
            prompt=('\nHuman: ' + prompt + '\nAssistant:')
        )

        return self._clean_text(output)

        
        
