#!/usr/bin/env python3

import os
import json
import argparse
from argparse import Namespace
from typing import List

from rich.console import Console
from rich.markdown import Markdown, MarkdownIt
from rich.live import Live

import cmd2
from cmd2 import argparse_custom, with_argparser, Settable

import openai

class Config:
    sep = Markdown("---")
    baseDir = os.path.dirname(os.path.realpath(__file__))
    default = os.path.join(baseDir, "config.json")

    def __init__(self, file=None) -> None:
        self.cfg = {}
        if file:
            self.load(file)

    def load(self, file):
        with open(file, "r") as f:
            self.cfg = json.load(f)
        self.key = self.cfg.get("key", openai.api_key)
        self.api_base = self.cfg.get("api_base", openai.api_base)
        self.model = self.cfg.get("model", "gpt-3.5-turbo")
        self.prompt = self.cfg.get("prompt", [])
        self.stream = self.cfg.get("stream", False)
        self.response = self.cfg.get("response", False)
        self.proxy = self.cfg.get("proxy", "")

    def get(self, key, default=None):
        return self.cfg.get(key, default)


class GptCli(cmd2.Cmd):
    prompt = "gptcli> "

    def __init__(self, config):
        super().__init__(allow_cli_args=False)
        self.doc_header = "gptcli commands (use '.help -v' for verbose/'.help <topic>' for details):"
        self.hidden_commands = [
            "._relative_run_script", ".run_script", ".run_pyscript",
            ".eof", ".history", ".macro", ".shell", ".shortcuts", ".alias"]
        for sk in ["allow_style", "always_show_hint", "echo", "feedback_to_output",
                  "max_completion_items", "quiet", "timing"]:
            self.remove_settable(sk)
        self.console = Console()
        self.session = []
        # Init config
        self.config = Config(config)
        self.api_key = self.config.key
        self.api_base = self.config.api_base
        self.api_model = self.config.model
        self.api_prompt = self.config.prompt
        self.api_stream = self.config.stream
        self.api_response = self.config.response
        self.proxy = self.config.proxy
        openai.api_key = self.api_key
        openai.api_base = self.api_base
        if self.proxy:
            self.print("Proxy:", self.proxy)
            openai.proxy = self.proxy
        self.print("Response in prompt:", self.api_response)
        self.print("Stream mode:", self.api_stream)
        # Init settable
        # NOTE: proxy is not settable in runtime since openai use pre-configured session
        self.add_settable(Settable("api_key", str, "OPENAI_API_KEY", self, onchange_cb=self.openai_set))
        self.add_settable(Settable("api_base", str, "OPENAI_API_BASE", self, onchange_cb=self.openai_set))
        self.add_settable(Settable("response", bool, "Attach response in prompt", self, settable_attrib_name="api_response"))
        self.add_settable(Settable("stream", bool, "Enable stream mode", self, settable_attrib_name="api_stream"))
        self.add_settable(Settable("model", str, "OPENAI model", self, settable_attrib_name="api_model"))
        # MISC
        with self.console.capture() as capture:
            self.print(f"[bold yellow]{self.prompt}[/]", end="")
        self.prompt = capture.get()

    def openai_set(self, param, old, new):
        self.print(f"openai.{param} = {new}")
        setattr(openai, param, new)

    def _cmd_func_name(self, command: str) -> str:
        if command.startswith("."):
            command = command[1:]
        return super()._cmd_func_name(command)

    def get_all_commands(self) -> List[str]:
        return list(map(lambda c: f".{c}", super().get_all_commands()))

    def default(self, statement: cmd2.Statement):
        self.handle_input(statement.raw)

    def print(self, *msg, **kwargs):
        self.console.print(*msg, **kwargs)

    def handle_input(self, content: str):
        if not content:
            return
        self.session.append({"role": "user", "content": content})
        if self.api_stream:
            answer = self.query_openai_stream(self.session)
        else:
            answer = self.query_openai(self.session)
        if not answer:
            self.session.pop()
        elif self.api_response:
            self.session.append({"role": "assistant", "content": answer})

    def load_session(self, file):
        with open(file, "r") as f:
            self.session = json.load(f)
        self.print("Load {} records from {}".format(len(self.session), file))

    def save_session(self, file):
        self.print("Save {} records to {}".format(len(self.session), file))
        with open(file, "w") as f:
            json.dump(self.session, f, indent=2)
    
    def query_openai(self, data: dict) -> str:
        messages = []
        messages.extend(self.api_prompt)
        messages.extend(data)
        try:
            response = openai.ChatCompletion.create(
                model=self.api_model,
                messages=messages
            )
            content = response["choices"][0]["message"]["content"]
            self.print(Markdown(content), Config.sep)
            return content
        except openai.error.OpenAIError as e:
            self.print("OpenAIError:", e)
        return ""

    def query_openai_stream(self, data: dict) -> str:
        messages = []
        messages.extend(self.api_prompt)
        messages.extend(data)
        md = Markdown("")
        parser = MarkdownIt().enable("strikethrough")
        answer = ""
        try:
            response = openai.ChatCompletion.create(
                model=self.api_model,
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
            self.print("Canceled")
        except openai.error.OpenAIError as e:
            self.print("OpenAIError:", e)
            answer = ""
        self.print(Config.sep)
        return answer

    parser_ml = argparse_custom.DEFAULT_ARGUMENT_PARSER(add_help=False)
    @with_argparser(parser_ml)
    def do_multiline(self, args):
        """input multiple lines, end with ctrl-d(Linux/macOS) or ctrl-z(Windows).
        cancel with ctrl-c"""
        contents = []
        while True:
            try:
                line = input("> ")
            except EOFError:
                self.print("--- EOF ---")
                break
            except KeyboardInterrupt:
                self.print("^C")
                return
            contents.append(line)
        self.handle_input("\n".join(contents))

    parser_reset = argparse_custom.DEFAULT_ARGUMENT_PARSER(add_help=False)
    @with_argparser(parser_reset)
    def do_reset(self, args):
        "Reset session, i.e. clear chat history"
        self.session.clear()
        self.print("session cleared.")

    parser_save = argparse_custom.DEFAULT_ARGUMENT_PARSER()
    parser_save.add_argument("file", help="target file to save",
                            completer=cmd2.Cmd.path_complete)
    @with_argparser(parser_save)
    def do_save(self, args: Namespace):
        "Save current conversation to file"
        self.save_session(args.file)

    parser_load = argparse_custom.DEFAULT_ARGUMENT_PARSER()
    parser_load.add_argument("file", help="target file to load",
                            completer=cmd2.Cmd.path_complete)
    @with_argparser(parser_load)
    def do_load(self, args: Namespace):
        "Load conversation from file"
        self.load_session(args.file)

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", dest="config", help="path to config.json", default=Config.default)
    args = parser.parse_args()

    app = GptCli(args.config)
    app.cmdloop()

if __name__ == '__main__':
    main()
