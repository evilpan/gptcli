#!/usr/bin/env python3

import os
import argparse
import openai

from rich.console import Console
from rich.markdown import Markdown

c = Console()
baseDir = os.path.dirname(os.path.realpath(__file__))

def openai_create(data: dict):
    messages = [
        { "role": "system", "content": "Use triple backticks with the language name for every code block in your markdown response, if any." },
    ]
    messages.extend(data)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response["choices"][0]["message"]["content"]

def print_help():
    c.print("""options:
  <        input multiline
  reset    reset session, i.e. clear chat history
  help     show this help message
  exit     exit console
""")

def setup_readline():
    def completer(text, state):
        options = ['reset', 'help', 'exit', '<<<']
        matches = [o for o in options if o.startswith(text)]
        if state < len(matches):
            return matches[state]
        else:
            return None
    readline.set_completer(completer)
    readline.parse_and_bind('tab:complete')

def read_multiline() -> str:
    contents = []
    c.print("Input multiline data, stop with ctrl-c/ctrl-d(Linux/macOS) or ctrl-z(Windows):")
    while True:
        try:
            line = input()
        except EOFError:
            c.print("--- EOF ---")
            break
        except KeyboardInterrupt:
            c.print("--- EOF ---")
            break
        contents.append(line)
    return "\n".join(contents)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-r", dest="response", action="store_true",
                        help="attach server response in request prompt, consume more tokens to get better results")
    parser.add_argument("-k", dest="key", help="path to api_key", default=os.path.join(baseDir, ".key"))
    parser.add_argument("-p", dest="proxy", help="http/https proxy to use")
    args = parser.parse_args()

    try:
        import readline
        setup_readline()
    except Exception:
        pass

    c.print(f"Loading key from {args.key}")
    with open(args.key, "r") as f:
        openai.api_key = f.read().strip()
    if args.proxy:
        c.print(f"Using proxy: {args.proxy}")
        openai.proxy = args.proxy
    c.print(f"Attach response in prompt: {args.response}")

    sep = Markdown("---")
    data = []
    while True:
        try:
            content = c.input("[bold yellow]Input:[/] ").strip()
            if not content:
                c.print()
                continue
            if content == "<":
                content = read_multiline()
            if content == "reset":
                data.clear()
                c.print("Session reset.")
                continue
            if content == "help":
                print_help()
                continue
            if content == "exit":
                break
            data.append({"role": "user", "content": content})
            answer = openai_create(data)
        except openai.error.RateLimitError as e:
            c.print(e)
            continue
        except KeyboardInterrupt:
            c.print("Bye!")
            break
        except EOFError as e:
            c.print("Bye!")
            break
        # print(answer)
        c.print(Markdown(answer), sep)
        if args.response:
            data.append({"role": "assistant", "content": answer})
