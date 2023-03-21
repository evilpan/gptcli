#!/usr/bin/env python3

import cmd2
from cmd2 import argparse_custom, with_argparser
import argparse
from argparse import Namespace
from typing import List

class GptCli(cmd2.Cmd):
    prompt = "chat> "

    def __init__(self):
        super().__init__(allow_cli_args=False)
        self.doc_header = "gptcli commands (use '.help -v' for verbose/'.help <topic>' for details):"
        self.hidden_commands = [
            "._relative_run_script", ".run_script", ".run_pyscript",
            ".eof", ".history", ".macro", ".shell", ".shortcuts"]

    def _cmd_func_name(self, command: str) -> str:
        if command.startswith("."):
            command = command[1:]
        return super()._cmd_func_name(command)

    def get_all_commands(self) -> List[str]:
        return list(map(lambda c: f".{c}", super().get_all_commands()))

    def default(self, statement: cmd2.Statement):
        self.handle_input(statement.raw)

    def handle_input(self, content: str):
        print("input:", content)

    default_parser = argparse_custom.DEFAULT_ARGUMENT_PARSER(add_help=False)
    @with_argparser(default_parser)
    def do_multiline(self, *ignore):
        """Input multiple lines"""
        contents = []
        while True:
            try:
                line = input("> ")
            except EOFError:
                print("--- EOF ---")
                break
            except KeyboardInterrupt:
                print("^C")
                return
            contents.append(line)
        self.handle_input("\n".join(contents))

    parser_load = argparse_custom.DEFAULT_ARGUMENT_PARSER()
    parser_load.add_argument("file", help="file to save conversation")
    @with_argparser(parser_load)
    def do_save(self, args: Namespace):
        print("save")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", dest="config", help="path to config.json")
    args = parser.parse_args()
    app = GptCli()
    app.cmdloop()