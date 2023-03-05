#!/usr/bin/env python3

import readline
import openai
from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

documents = SimpleDirectoryReader('data').load_data()
index = GPTSimpleVectorIndex(documents)

while True:
    req = input("> ").strip()
    resp = index.query(req)
    print(resp)