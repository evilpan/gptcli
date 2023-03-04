#!/usr/bin/env python3

import time
import asyncio
from rich.console import Console
from rich.markdown import Markdown, MarkdownIt
from rich.live import Live

text = """\
As an AI language model, I don't have the ability to directly perform syntax highlighting, but I can show you an example of how to use Markdown syntax for code blocks:

```python
def welcome(name):
    print(f"Hello, {name}!")

# Call the function
welcome("Alice")
```
This creates a code block with syntax highlighting for Python code.
To make this work, you need to include the name of the programming language immediately after the first set of backticks.
In this case, we've specified that we're writing Python code by including `python` after the backticks.
"""

c = Console()

def test_live():
    md = Markdown("")
    parser = MarkdownIt().enable("strikethrough")
    parts = [text[i:i+5] for i in range(0, len(text), 5)]
    with Live(md, refresh_per_second=4):  # update 4 times a second to feel fluid
        for part in parts:
            time.sleep(0.1)
            md.markup += part
            md.parsed = parser.parse(md.markup)



"""
First:
{
  "choices": [
    {
      "delta": {
        "role": "assistant"
      },
      "finish_reason": null,
      "index": 0
    }
  ],
  "created": 1677894010,
  "id": "chatcmpl-6qBAYUFOkHB47std83P0djYO1DZHq",
  "model": "gpt-3.5-turbo-0301",
  "object": "chat.completion.chunk"
}

Middle:
{
  "choices": [
    {
      "delta": {
        "content": " zipfile"
      },
      "finish_reason": null,
      "index": 0
    }
  ],
  ...
}

Last:
{
  "choices": [
    {
      "delta": {},
      "finish_reason": "stop",
      "index": 0
    }
  ],
  ...
}
"""
async def test_stream():
    import openai
    openai.api_key = open(".key").read().strip()
    # NOTE: aiohttp does not support socks5 proxy yet
    # openai.proxy = "http://127.0.0.1:1080"
    messages = [
        { "role": "system", "content": "Use triple backticks with the language name for every code block in your markdown response, if any." },
        { "role": "user", "content": "python example to unzip file to dir" },
    ]

    async for part in await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True
    ):
        finish_reason = part["choices"][0]["finish_reason"]
        if "content" in part["choices"][0]["delta"]:
            content = part["choices"][0]["delta"]["content"]
            print(content, end="")
        elif finish_reason:
            print(finish_reason)

if __name__ == '__main__':
    asyncio.run(test_stream())