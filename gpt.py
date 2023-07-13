import os
import sys
import json
import openai
import transformers
from dotenv import load_dotenv



env_path = os.path.join(os.path.dirname(__file__), ".env")

if os.path.exists(env_path):
    load_dotenv(env_path)
    print("info: .env file exists.")

if "OPENAI_API_KEY" not in os.environ:
    print("ERROR: Set OPENAI_API_KEY into .env file at the top of directory. \n\
          or export OPENAI_API_KEY environmental variables")
    sys.exit(1)

openai.organization = os.environ["Organization_ID"]
openai.api_key = os.environ["OPENAI_API_KEY"]


class ChatSession:
    def __init__(self, goal):
        system_prompt_filePath = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.txt")
        with open(system_prompt_filePath, "r") as file:
            content = file.read()

        self.goal = goal
        self.content = content.replace("{goal}", f"{goal}")
        self.messages = [
            {"role": "system", "content": self.content}
        ]

    def append_msg(self, msg):
        self.messages.append(msg)

    def delete_msg(self):
        if self.messages:
            self.messages.pop()

    def send_msg(self):
        functions = [
            {
                "name": "get_json_for_goal",
                "description": "[Goal]を達成するような、Linuxコマンドをjsonで返します。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "string",
                            "description": "[Goal]を格納せよ。"
                        },
                        "was_Goal_achieved": {
                            "type": "string",
                            "description": "初期値はFalse。"
                        },
                        "oneCommand": {
                            "type": "string",
                            "description": "goalを達成するような、Linuxコマンドを一つ、格納する。"
                        },
                        "explain_command": {
                            "type": "string",
                            "description": "コマンドの説明等を格納する。"
                        },
                        "isOutputError": {
                            "type": "string",
                            "description": "初期値はFalse。"
                        },
                        "oneCommand_to_fix_error": {
                            "type": "string",
                            "description": "エラーを修正、または回避するような別のコマンドを格納する。"
                        },
                        "explain_oneCommand_to_fix_error": {
                            "type": "string",
                            "description": "oneCommand_to_fix_errorの説明等を格納する。"
                        }
                    },
                    "required": ["goal",
                                 "was_Goal_achieved",
                                 "oneCommand",
                                 "explain_command",
                                 "oneCommand_to_fix_error",
                                 "explain_oneCommand_to_fix_error",
                                 "isOutputError"]
                }
            }
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=self.messages,
            functions=functions,
            function_call={"name": "get_json_for_goal"}
        )
        print(self.messages)
        print("<<<<<<<<<")
        print(response)
        print("<<<<<<<<<")
        message = response["choices"][0]["message"]
        print(message)
        try:
            arguments = json.loads(message["function_call"]["arguments"])
        except:
            print("connection error")
            exit(1)

        return arguments
    
    def estimate_num_of_torkens(self):
        transformers.OpenAIGPTTokenizer()


        

if __name__ == "__main__":
    chat = ChatSession("nvm環境をインストールする")
    # chat.send_msg()

