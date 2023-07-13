import os
import json
from typing import List
from prompt_toolkit import prompt

import gpt
from CommandExcutor import CommandExecutor


def make_reply_prompt(goal: str, excuted_commands: List[str], terminal_output: List[str]) -> str:
        reply_prompt_filePath = os.path.join(os.path.dirname(__file__), "prompts", "reply_prompt.txt")
        with open(reply_prompt_filePath, "r") as file:
            content = file.read()

        excuted_commands_str = "\n".join([str(row) for row in excuted_commands])
        terminal_output_str = "\n".join([str(row) for row in terminal_output])

        content = content.replace("{goal}", f"{goal}")
        content = content.replace("{excuted_commands}", f"{excuted_commands_str}")
        content = content.replace("{output}", f"{terminal_output_str}")

        return content


def main():
    excuted_commands = []

    goal = input("こんにちは、あなたをサポートします。\n最終目標を入力してください: ")
    chat = gpt.ChatSession(goal)
    suggest_json = chat.send_msg()
    
    while True:
        chat.delete_msg()
        print("executed commands: ", excuted_commands)
        if suggest_json["was_Goal_achieved"] == "True":
            print("====================")
            print("以下の設定した目標が達成されました。プログラムを終了します。")
            print(f"{goal}")
            print("====================")
            break

        print("*********")
        print(suggest_json)
        print("*********")

        if suggest_json["isOutputError"] == "True":
            try:
                excuted_commands.pop()
            except:
                pass
            print("====================")
            print(suggest_json["explain_error"])
            print("====================")
            suggested_command= suggest_json["FixErrorOneCommand"]
            command = prompt("エラーを修正、回避する為に、次のコマンドを実行します(編集可能)。\n", default=suggested_command)
        else:
            print("====================")
            print(suggest_json["explain_command"])
            print("====================")
            suggested_command= suggest_json["oneCommand"]
            command = prompt("次のコマンドを実行します(編集可能)。\n", default=suggested_command)

        excuted_commands.append(command)
        executor = CommandExecutor(command.split(" "))
        output_lines = executor.execute()
        last_five_lines = output_lines[-5:]

        reply_content = make_reply_prompt(goal, excuted_commands, last_five_lines)
        reply_msg = {"role": "user", "content": reply_content}

        chat.append_msg(reply_msg)

        print("送信用Output----------")
        print(chat.messages)
        print("送信用Output^^^^^^^^^^")

        suggest_json = chat.send_msg()



if __name__ == "__main__":
    main()
