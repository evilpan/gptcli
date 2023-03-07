#!/usr/bin/env python3

import sys
import logging
import argparse
from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", dest="index", help="load index.json from disk")
    parser.add_argument("-d", dest="dir", help="directory to vector")
    parser.add_argument("-o", dest="out", default="index.json", help="save index file")
    args = parser.parse_args()

    if args.dir:
        documents = SimpleDirectoryReader('docs', recursive=True).load_data()
        index = GPTSimpleVectorIndex(documents)
        print("save index to", args.out)
        index.save_to_disk(args.out)
    elif args.index:
        index = GPTSimpleVectorIndex.load_from_disk(args.index)
    else:
        return
    while True:
        req = input("> ").strip()
        resp = index.query(req)
        print(resp)


if __name__ == "__main__":
    main()