#!/usr/bin/env python3

import os
import json
import argparse
import openai
from typing import List

from rich.console import Console
from rich.markdown import Markdown, MarkdownIt
from rich.live import Live

try:
    import rlcompleter
    import readline
except ImportError:
    pass

class Config:
    sep = Markdown("---")
    baseDir = os.path.dirname(os.path.realpath(__file__))
    default = os.path.join(baseDir, "config.json")

    def __init__(self) -> None:
        self.cfg = {}
        self.history = []

    def load(self, file):
        with open(file, "r") as f:
            self.cfg = json.load(f)

    def load_session(self, file):
        with open(file, "r") as f:
            self.history = json.load(f)
        print("Load {} records from {}".format(len(self.history), file))

    def save_session(self, file):
        print("Save {} records to {}".format(len(self.history), file))
        with open(file, "w") as f:
            json.dump(self.history, f, indent=2)

    @property
    def key(self):
        return self.cfg.get("key", os.environ.get("OPENAI_API_KEY", ""))
    
    @property
    def api_base(self):
        return self.cfg.get("api_base", os.environ.get("OPENAI_API_BASE", ""))

    @property
    def model(self):
        return self.cfg.get("model", "gpt-3.5-turbo")

    @property
    def prompt(self):
        return self.cfg.get("prompt", [])

    @property
    def stream(self):
        return self.cfg.get("stream", False)

    @property
    def response(self):
        return self.cfg.get("response", False)

    @property
    def proxy(self):
        return self.cfg.get("proxy", "")

c = Console()
kConfig = Config()

def query_openai(data: dict):
    messages = []
    messages.extend(kConfig.prompt)
    messages.extend(data)
    try:
        response = openai.ChatCompletion.create(
            model=kConfig.model,
            messages=messages
        )
        content = response["choices"][0]["message"]["content"]
        c.print(Markdown(content), Config.sep)
        return content
    except openai.error.OpenAIError as e:
        c.print(e)
    except Exception as e:
        c.print(e)
    return ""

def query_openai_stream(data: dict):
    messages = []
    messages.extend(kConfig.prompt)
    messages.extend(data)
    md = Markdown("")
    parser = MarkdownIt().enable("strikethrough")
    answer = ""
    try:
        response = openai.ChatCompletion.create(
            model=kConfig.model,
            messages=messages,
            stream=True)
        with Live(md, auto_refresh=False) as lv:
            for part in response:
                finish_reason = part["choices"][0]["finish_reason"]
                if "content" in part["choices"][0]["delta"]:
                    content = part["choices"][0]["delta"]["content"]
                    answer += content
                    md.markup = answer
                    md.parsed = parser.parse(md.markup)
                    lv.refresh()
                elif finish_reason:
                    pass
    except KeyboardInterrupt:
        c.print("Canceled")
    except openai.error.OpenAIError as e:
        c.print(e)
        answer = ""
    except Exception as e:
        c.print(e)
    c.print(Config.sep)
    return answer


class ChatConsole:

    def __init__(self) -> None:
        parser = argparse.ArgumentParser("Input", add_help=False)
        parser.add_argument('-help', action='help', default=argparse.SUPPRESS, help="show this help message")
        parser.add_argument("-reset", action='store_true',
                            help="reset session, i.e. clear chat history")
        parser.add_argument("-save", metavar="FILE", type=str,
                            help="save current conversation to file")
        parser.add_argument("-load", metavar="FILE", type=str,
                            help="load conversation from file")
        parser.add_argument("-exit", action='store_true',
                            help="exit console")
        parser.add_argument("-multiline", action='store_true',
                            help="input multiple lines, end with ctrl-d(Linux/macOS) or ctrl-z(Windows). cancel with ctrl-c")
        self.parser = parser
        try:
            self.init_readline([opt for action in parser._actions for opt in action.option_strings])
        except Exception as e:
            c.print("Failed to setup readline, autocomplete may not work:", e)

    def init_readline(self, options: List[str]):
        def completer(text, state):
            matches = [o for o in options if o.startswith(text)]
            if state < len(matches):
                return matches[state]
            else:
                return None
        readline.set_completer(completer)
        readline.set_completer_delims(readline.get_completer_delims().replace('-', ''))
        readline.parse_and_bind('tab:complete')

    def parse_input(self) -> str:
        # content = c.input("[bold yellow]Input:[/] ").strip()
        with c.capture() as capture:
            c.print("[bold yellow]Input:[/] ", end="")
        content = input(capture.get())
        if not content.startswith("-"):
            return content
        # handle console options locally
        try:
            args = self.parser.parse_args(content.split())
        except SystemExit:
            return ""
        except argparse.ArgumentError as e:
            print(e)
            return ""
        if args.reset:
            kConfig.history.clear()
            c.print("Session cleared.")
        elif args.save:
            kConfig.save_session(args.save)
        elif args.load:
            kConfig.load_session(args.load)
        elif args.multiline:
            return self.read_multiline()
        elif args.exit:
            raise EOFError
        else:
            print("???", args)
        return ""

    def read_multiline(self) -> str:
        contents = []
        while True:
            try:
                line = input("> ")
            except EOFError:
                c.print("--- EOF ---")
                break
            except KeyboardInterrupt:
                return ""
            contents.append(line)
        return "\n".join(contents)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", dest="config", help="path to config.json", default=Config.default)
    args = parser.parse_args()

    c.print(f"Loading config from {args.config}")
    kConfig.load(args.config)
    if kConfig.key:
        openai.api_key = kConfig.key
    if kConfig.api_base:
        c.print(f"Using api_base: {kConfig.api_base}")
        openai.api_base = kConfig.api_base
    if kConfig.proxy:
        c.print(f"Using proxy: {kConfig.proxy}")
        openai.proxy = kConfig.proxy
    c.print(f"Response in prompt: {kConfig.response}")
    c.print(f"Stream mode: {kConfig.stream}")

    chat = ChatConsole()
    while True:
        try:
            content = chat.parse_input().strip()
            if not content:
                continue
            hist = kConfig.history # alias
            hist.append({"role": "user", "content": content})
            if kConfig.stream:
                answer = query_openai_stream(hist)
            else:
                answer = query_openai(hist)
        except KeyboardInterrupt:
            c.print("Bye!")
            break
        except EOFError as e:
            c.print("Bye!")
            break
        if not answer:
            hist.pop()
        elif kConfig.response:
            hist.append({"role": "assistant", "content": answer})


if __name__ == '__main__':
    main()