#!/usr/bin/env python3

import os
import asyncio
import argparse
import openai

from rich.console import Console
from rich.markdown import Markdown, MarkdownIt
from rich.live import Live
from aiohttp import ClientSession

import readline
try:
    import rlcompleter
except ImportError:
    pass

c = Console()
systemPrompt = {
    "role": "system",
    "content": "Use triple backticks with the language name for every code block in your markdown response, if any."
}

class Config:
    base_dir = os.path.dirname(os.path.realpath(__file__))
    default_key = os.path.join(base_dir, ".key")
    aio_socks_proxy = None
    sep = Markdown("---")

def query_openai(data: dict):
    messages = [ systemPrompt ]
    messages.extend(data)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        content = response["choices"][0]["message"]["content"]
        c.print(Markdown(content), Config.sep)
        return content
    except openai.error.RateLimitError as e:
        c.print(e)
        return ""

async def query_openai_stream(data: dict):
    messages = [ systemPrompt ]
    messages.extend(data)
    md = Markdown("")
    parser = MarkdownIt().enable("strikethrough")
    if Config.aio_socks_proxy:
        try:
            from aiohttp_socks import ProxyConnector
            connector = ProxyConnector.from_url(Config.aio_socks_proxy)
            openai.aiosession.set(ClientSession(connector=connector))
        except ImportError:
            c.print("aiohttp_socks not installed, socks proxy for aiohttp won't work")
            Config.aio_socks_proxy = None
    answer = ""
    try:
        with Live(md, auto_refresh=False) as lv:
            async for part in await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages,
                stream=True
            ):
                finish_reason = part["choices"][0]["finish_reason"]
                if "content" in part["choices"][0]["delta"]:
                    content = part["choices"][0]["delta"]["content"]
                    answer += content
                    md.markup = answer
                    md.parsed = parser.parse(md.markup)
                    lv.refresh()
                elif finish_reason:
                    pass
    except openai.error.RateLimitError as e:
        c.print(e)
        answer = ""
    c.print(Config.sep)
    if Config.aio_socks_proxy:
        await openai.aiosession.get().close()
    return answer


def print_help():
    c.print("""options:
  <        input multiline, end with ctrl-d(Linux/macOS) or ctrl-z(Windows)
  reset    reset session, i.e. clear chat history
  help     show this help message
  exit     exit console
""")

def setup_readline():
    def completer(text, state):
        options = ['reset', 'help', 'exit', '<']
        matches = [o for o in options if o.startswith(text)]
        if state < len(matches):
            return matches[state]
        else:
            return None
    readline.set_completer(completer)
    readline.parse_and_bind('tab:complete')

def read_multiline() -> str:
    contents = []
    c.print("Input multiline data, cancel with ctrl-c:")
    while True:
        try:
            line = input()
        except EOFError:
            c.print("--- EOF ---")
            break
        except KeyboardInterrupt:
            return ""
        contents.append(line)
    return "\n".join(contents)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-n", dest="no_stream", action="store_true", help="query openai in non-stream mode")
    parser.add_argument("-r", dest="response", action="store_true",
                        help="attach server response in request prompt, consume more tokens to get better results")
    parser.add_argument("-k", dest="key", help="path to api_key", default=Config.default_key)
    parser.add_argument("-p", dest="proxy", help="http/https proxy to use")
    args = parser.parse_args()

    try:
        setup_readline()
    except Exception:
        pass

    c.print(f"Loading key from {args.key}")
    with open(args.key, "r") as f:
        openai.api_key = f.read().strip()
    stream = not args.no_stream
    if args.proxy:
        c.print(f"Using proxy: {args.proxy}")
        if stream and args.proxy.startswith("socks"):
            Config.aio_socks_proxy = args.proxy
        else:
            openai.proxy = args.proxy
    c.print(f"Response in prompt: {args.response}")
    c.print(f"Stream mode: {stream}")

    data = []
    while True:
        try:
            # content = c.input("[bold yellow]Input:[/] ").strip()
            with c.capture() as capture:
                c.print("[bold yellow]Input:[/] ", end="")
            content = input(capture.get())
            if content == "<":
                content = read_multiline()
            content = content.strip()
            if not content:
                continue
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
            if stream:
                answer = asyncio.run(query_openai_stream(data))
            else:
                answer = query_openai(data)
        except KeyboardInterrupt:
            c.print("Bye!")
            break
        except EOFError as e:
            c.print("Bye!")
            break
        if not answer:
            data.pop()
        elif args.response:
            data.append({"role": "assistant", "content": answer})
