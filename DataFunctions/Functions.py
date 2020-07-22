import sys
sys.path.append("DataFunctions")
sys.path.append("../DataFunctions")
import defaults
import EDAFunctions as eda
# imports

import re
import pandas as pd
import json
from elasticsearch import Elasticsearch, helpers

def getInputParagraphs():
    es = Elasticsearch(['http://' + defaults.credentials["username"] + ':' + defaults.credentials["password"] + '@' + defaults.credentials["ip_and_port"]], timeout=600)
    doc = {
        'size' : 10000,
        'query': {
            'match_all' : {}
        }
    }
    result = es.search(index="patent-paragraphs", body=doc)
    paragraphs = []
    for paragraph in result["hits"]["hits"]:
        paragraphs.append(paragraph["_source"]["originalParagraph"])
    return paragraphs

    # return defaults.paragraphs


def preProcessParagraphs(paragraphs):
    preProcessedParagraphs = []
    for paragraph in paragraphs:
        # remove stopwords
        paragraphWords = paragraph.split(" ")
        paragraphWordsWithoutStopWords = eda.remove_stopwords(paragraphWords)
        # lemmatize
        paragraphWordsLemmatized = eda.lemmatize(paragraphWordsWithoutStopWords)
        paragraphWordsLemmatizedString = " ".join(paragraphWordsLemmatized)
        preProcessedParagraphs.append((paragraph, paragraphWordsLemmatizedString))
    return preProcessedParagraphs


def search(data):
    results = []
    field = "originalParagraph"
    # field = "preProcessedParagraph"
    for d in data:
        es = Elasticsearch(['http://' + defaults.credentials["username"] + ':' + defaults.credentials["password"] + '@' + defaults.credentials["ip_and_port"]], timeout=600)
        doc = {
            "size" : 500,
                "query": {
                "multi_match" : {
                    # "query": d[0], 
                    "query": d[1], 
                    "fields": [
                        field
                    ]
                }
            }
        }
        result = es.search(index="technical-paragraphs", body=doc)
        result["inputParagraph"] = d[0]
        result["preProcessedInputParagraph"] = d[1]
        results.append(result)
    return {"searchResults": results}


def getWordsToHighlight(data):
    for d in data["searchResults"]:
        # inputParagraph = d["inputParagraph"]
        inputParagraph = d["preProcessedInputParagraph"]
        paragraphWordsLemmatized = inputParagraph.split(" ")
        for hit in d["hits"]["hits"]:
            wordsToHighlight = []
            # resultWords = hit["_source"]["originalParagraph"].split(" ")
            resultWords = hit["_source"]["preProcessedParagraph"].split(" ")
            for word in paragraphWordsLemmatized:
                if word in resultWords:
                    wordsToHighlight.append(word)
            hit["wordsToHighlight"] = list(set(wordsToHighlight))
    return data