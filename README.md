# Setup

1. clone this repo
2. pip3 install -U -r requirements.txt
3. get your apikey from <https://platform.openai.com/account/api-keys> and put it in `.key`

# Run

```sh
$ ./gptcli.py -h
usage: gptcli.py [-h] [-r] [-k KEY] [-p PROXY]

options:
  -h, --help  show this help message and exit
  -r          attach server response in request prompt, consume more tokens to get better results (default: False)
  -k KEY      path to api_key (default: /Users/pan/Projects/gptcli/.key)
  -p PROXY    http/https proxy to use (default: None)
```

Console help:

```
$ gptcli.py 
Loading key from .key
Attach response in prompt: False
Input: help
options:
  <        input multiline
  reset    reset session, i.e. clear chat history
  help     show this help message
  exit     exit console
```

# Feature

- [x] Session based
- [x] Markdown support
- [x] Syntax highlight
- [x] Proxy support
- [x] Multiline input
- [ ] Stream output

# Example

![demo](./demo.jpg)

# LINK

- https://platform.openai.com/docs/introduction
- https://platform.openai.com/docs/api-reference/completions
