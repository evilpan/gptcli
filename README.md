Take chatGPT into command line.

[![stream](./stream.svg)][vid]

# Setup

1. clone this repo
2. pip3 install -U -r requirements.txt
3. copy `demo_config.json` to `config.json`
4. get your [OPENAI_API_KEY][key] and put it in `config.json`

# Run

```sh
$ ./gptcli.py -h
usage: gptcli.py [-h] [-c CONFIG]

options:
  -h, --help  show this help message and exit
  -c CONFIG   path to your config.json (default: config.json)
```

Sample `config.json`:
```json
{
    "api_key": "sk-xxx",
    "api_base": "https://chat.pppan.net/v1",
    "api_type": "open_ai",
    "api_version": null,
    "model": "gpt-3.5-turbo",
    "context": 2,
    "stream": true,
    "stream_render": true,
    "showtokens": false,
    "proxy": "socks5://localhost:1080",
    "prompt": [
        { "role": "system", "content": "If your response contains code, show with syntax highlight, for example ```js\ncode\n```" }
    ]
}
```

- (required) api_key: OpenAI's api key. will read from OPENAI_API_KEY envronment variable if not set
- (optional) api_base: OpenAI's api base url. Can set to a server reverse proxy, for example [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/chatgpt-quickstart) or [chatgptProxyAPI](https://github.com/x-dr/chatgptProxyAPI). By default it's from OPENAI_API_BASE or just <https://api.openai.com/v1>;
- (optional) api_type: OpenAI's api type, read from env OPENAI_API_TYPE by default;
- (optional) api_version: OpenAI's api version, read from env OPENAI_API_VERSION by default;
- (optional) model: OpenAI's chat model, by default it's `gpt-3.5-turbo`;
- (optional) context: Chat session context, choices are:
  - 0: no context provided for every chat request, cost least tokens, but AI don't kown what you said before;
  - 1: only use previous user questions as context;
  - 2: use both previous questions and answers as context, would cost more tokens;
- (optional) stream: Output in stream mode;
- (optional) stream_render: Render markdown in stream mode, you can disable it to avoid some UI bugs;
- (optional) showtokens: Print used tokens after every chat;
- (optional) proxy: Use http/https/socks4a/socks5 proxy for requests to `api_base`;
- (optional) prompt: Customize your prompt. This will appear in every chat request;

Supported model:

- [x] gpt-3.5-turbo
- [x] gpt-4
- [x] gpt-4-32k

Console help (with tab-complete):
```sh
$ ./gptcli.py
gptcli> .help -v

gptcli commands (use '.help -v' for verbose/'.help <topic>' for details):
======================================================================================================
.edit                 Run a text editor and optionally open a file with it
.help                 List available commands or provide detailed help for a specific command
.load                 Load conversation from Markdown/JSON file
.multiline            input multiple lines, end with ctrl-d(Linux/macOS) or ctrl-z(Windows). Cancel
                      with ctrl-c
.quit                 Exit this application
.reset                Reset session, i.e. clear chat history
.save                 Save current conversation to Markdown/JSON file
.set                  Set a settable parameter or show current settings of parameters
.usage                Tokens usage of current session / last N days, or print detail billing info
```

Run in Docker:

```sh
# build
$ docker build -t gptcli:latest .

# run
$ docker run -it --rm -v $PWD/.key:/gptcli/.key gptcli:latest -h

# for host proxy access:
$ docker run --rm -it -v $PWD/config.json:/gptcli/config.json --network host gptcli:latest -c /gptcli/config.json
```

# Feature

- [x] Single Python script
- [x] Session based
- [x] Markdown support with code syntax highlight
- [x] Stream output support
- [x] Proxy support (HTTP/HTTPS/SOCKS4A/SOCKS5)
- [x] Multiline input support (via `.multiline` command)
- [x] Save and load session from file (Markdown/JSON) (via `.save` and `.load` command)
- [x] Print tokens usage in realtime, and tokens usage for last N days, and billing details
- [ ] Integrate with `llama_index` to support chatting with documents

# LINK

- https://platform.openai.com/docs/introduction
- https://platform.openai.com/docs/api-reference/completions
- https://platform.openai.com/docs/models/overview
- https://platform.openai.com/account/api-keys

[vid]: https://asciinema.org/a/568859
[key]: https://platform.openai.com/account/api-keys
