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
```js
{
    "key": "",                  // your api-key, will read from OPENAI_API_KEY envronment variable if empty
    "api_base": "",             // your api_base, will read from OPENAI_API_BASE envronment variable if empty
    "model": "gpt-3.5-turbo",   // GPT Model
    "stream": true,             // Stream mode
    "stream_render": false,     // Render live markdown in stream mode
    "response": true,           // Attach response in prompt, consume more tokens to get better results
    "proxy": "",                // Use http/https/socks4a/socks5 proxy for requests to api.openai.com
    "prompt": [                 // Customize your prompt
        { "role": "system", "content": "If your response contains code, show with syntax highlight, for example ```js\ncode\n```" }
    ]
}
```

Supported model:

- [x] gpt-3.5-turbo
- [x] gpt-4
- [x] gpt-4-32k

Console help (with tab-complete):
```
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
- [ ] Integrate with `llama_index` to support chatting with documents

# LINK

- https://platform.openai.com/docs/introduction
- https://platform.openai.com/docs/api-reference/completions
- https://platform.openai.com/docs/models/overview
- https://platform.openai.com/account/api-keys

[vid]: https://asciinema.org/a/568859
[key]: https://platform.openai.com/account/api-keys
