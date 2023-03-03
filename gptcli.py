#!/usr/bin/env python3

import argparse
import readline
import openai

from rich.prompt import Prompt
from rich.console import Console
from rich.markdown import Markdown

c = Console()

def openai_create(prompt, history: dict):
    messages = [
        { "role": "system", "content": "If there're any code in your response, show it in markdown with syntax highlighting" },
    ]
    messages.extend([ 
        {"role": "user", "content": hist} for hist in 
        history + [prompt]
    ])
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response["choices"][0]["message"]["content"]


if __name__ == '__main__':

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-k", dest="key", help="path to api_key", default=".key")
    parser.add_argument("-p", dest="proxy", help="http/https proxy to use")
    args = parser.parse_args()

    c.print(f"Loading key from {args.key}")
    with open(args.key, "r") as f:
        openai.api_key = f.read().strip()
    if args.proxy:
        c.print(f"Using proxy: {args.proxy}")
        openai.proxy = args.proxy

    history = []
    while True:
        try:
            question = c.input("[bold green]Input:[/] ").strip()
            if not question:
                continue
            if question in ["q", "exit", "quit"]:
                break
            answer = openai_create(question, history)
        except KeyboardInterrupt:
            c.print("Bye!")
            break
        except EOFError as e:
            c.print("Bye!")
            break
        # print(answer)
        md = Markdown(answer)
        c.print(md)
        c.print()
        history.append(question)
