import pandas as pd
import json
from dotenv import load_dotenv
import os

load_dotenv()

class LLM_API:

    def __init__(self,
                 model_id, 
                 temperature=0.1,
                 max_tokens=32):
        
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


    def _invoke_bedrock(self,
                        prompt):
        
        body = json.dumps({
            "prompt": "\n\nHuman:" + prompt + "\n\nAssistant:",
            # "max_tokens_to_sample": self.max_tokens, # this seems to be a bug that is not solved
            "temperature": self.temperature,
            "top_p": 0.9,
        })
        
        response = self.client.invoke_model(body = body,
                                            modelId = self.model_id,
                                            accept = 'application/json',
                                            contentType =  'application/json'
                                            )
        response_body = json.loads(response.get('body').read())
        print(response_body)

        return response_body.get('generation')
    
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
    
    def prompt(self, prompt):

        if self.model_id in ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o']:
            return self._invoke_openai(prompt=prompt)

        # elif self.model_id in ['anthropic.claude-v2','meta.llama3-8b-instruct-v1:0']:
        else:
            return self._invoke_bedrock(prompt=prompt)