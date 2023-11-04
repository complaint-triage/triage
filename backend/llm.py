import json
import re
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from criteria import basic_criteria

def parse_json(json_string: str) -> dict:
    """
    strip extra stuff around the json results
    """
    match = re.search(r"```(json)?(.*?)```", json_string, re.DOTALL)
    if match is None:
        json_str = json_string
    else:
        json_str = match.group(2)

    json_str = json_str.strip()

    parsed = json.loads(json_str, strict=False)

    return parsed


class Stage1:
    def __init__(self, deployment: str):
        self._chat_model = AzureChatOpenAI(temperature=0, deployment_name=deployment)
        self._chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("""
You are a lawyer who specializes in reading client who have complaints against other people,
and triaging them.                                                      
            """),
            HumanMessagePromptTemplate.from_template("""
You have been given a complaint by a client. A number of different organisations handle complaints
but they each have criteria for the types of complaints they will handle. Compare the client's
complaint against the given basic criteria for each of these organisations, and list the
organisations that may be able to handle the client's complaint.
                                                     
The basic criteria for each of the bodies is given in a JSON array. Return a list of id values. Use the
following JSON format:                               

```json
[
  {{
    "basic_id": String \ "basic_id of the complaint body"
  }}
]
```
                                                     
<<< Basic Criteria >>>
{basic_criteria}

<<< Complaint >>>
{user_input}
            """)
        ])

    def query(self, user_input: str) -> list:
        prompt = self._chat_prompt.format_prompt(
            user_input=user_input,
            basic_criteria=basic_criteria
        )
        j = self._chat_model(prompt.to_messages()).content
        try:
            matches = parse_json(j)
            ids = [ matched['basic_id'] for matched in matches ]
            return (ids)
        except:
            print(f'bad json for user_input: {user_input}\n\n    json: {j}')
            return ([])

class Stage2:
    def __init__(self, deployment: str):
        self._chat_model = AzureChatOpenAI(temperature=0, deployment_name=deployment)
        self._chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("""
You are a lawyer who checks complaints against legal requirements.
            """),

            HumanMessagePromptTemplate.from_template("""
You have been given a complaint, and the requirements for one legal body.
State whether the body can handle that complaint. Use this JSON format:

```json
{{
"valid": Boolean \ "True if the complaint can be sent to that body, false otherwise"
"reason": String \ "Explanation of why the complaint can or cannot be sent to that body"
}}
```
                <<< Complaint >>> 
                {user_input}
  
                <<< Legal Requirements >>>  
                {legal_requirements}
            """)
        ])

    def query(self, user_input, id, legal_requirements: str) -> tuple:
        j: str = self._chat_model(self._chat_prompt.format_prompt(
            user_input=user_input,
            legal_requirements=legal_requirements
        ).to_messages()).content
        try:
            j2 = parse_json(j)
            return (j2['valid'], j2['reason'])
        except:
            print(f'bad json for user_input: {user_input}\n    id: {id}\n    json: {j}')
            return (False, 'bad json')

class Generator:
    def __init__(self, deployment: str):
        self._chat_model = AzureChatOpenAI(temperature=0, deployment_name=deployment)
        self._chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("""
You are a lawyer who writes complaints on behalf of clients.
            """),

            HumanMessagePromptTemplate.from_template("""
You have been given a description of a client's complaint, and the guidance for writing a formal complaint.
Write a formal complaint for that client.

                <<< Complaint >>> 
                {user_input}
  
                <<< Guidance >>>  
                {guidance}
            """)
        ])

    def generate(self, user_input: str, guidance: str) -> tuple:
        result = self._chat_model(self._chat_prompt.format_prompt(
            user_input=user_input,
            guidance=guidance
        ).to_messages())
        return result.content
