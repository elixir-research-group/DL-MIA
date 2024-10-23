import pandas as pd
import json
from dexter.retriever.dense.ColBERT.colbert.infra.config.config import ColBERTConfig

import numpy as np
from typing import Dict
from dexter.data.datastructures.evidence import Evidence
from dexter.data.datastructures.question import Question

from dexter.retriever.dense.ColBERT.colbert.infra.config.config import ColBERTConfig

from dexter.utils.metrics.retrieval.RetrievalMetrics import RetrievalMetrics

from dexter.retriever.dense.TCTColBERT import TCTColBERT


config_instance = ColBERTConfig(doc_maxlen=256,ncells=500, kmeans_niters=4,bsize=4, gpus=0)

colbert_search = TCTColBERT(config_instance, checkpoint="colbert-ir/colbertv2.0")


def read_qrels() -> Dict:
    """read qrels

    Returns:
        Dict: qrel
    """    
    qrels = {}

    with open("DL-MIA/data/qrels.txt") as file:
        lines = [line.rstrip() for line in file]

    for line in lines:
        intent_pas_ids = line.split()
        if intent_pas_ids[0] not in qrels.keys():
            qrels[intent_pas_ids[0]]={}
        qrels[intent_pas_ids[0]][intent_pas_ids[2]] = int(intent_pas_ids[3])
    return qrels


def read_queries() -> Dict:
    """Reads queries

    Returns:
        Dict: returns query intents if ranking using intents 
        and queries if using original queries
    """ 

    query_data = pd.read_csv("DL-MIA/data/intent.tsv", sep="\t", header=None)
    queries = {}
    for index, row in query_data.iterrows():
        print(row[0],row[1])
        queries[row[0]] = row[1]
    return queries

if __name__=="__main__":
    qrels = read_qrels()
    queries = read_queries()

    with open("DL-MIA/src/baselines/intermediate_outputs/bm25_res.res") as file:
        lines = [line.rstrip() for line in file]
    bm25_resp = {}
    for line in lines:
        line_split = line.split()
        if line_split[0] not in bm25_resp:
            bm25_resp[line_split[0]] = {}
        bm25_resp[line_split[0]][line_split[2]] = line_split[4]

    response = {}
    corpus = pd.read_csv("DL-MIA/src/baselines/intermediate_outputs/bm25_docs.tsv", sep="\t", header=None)
    corpus_data = {}
    for index, row in corpus.iterrows():
        corpus_data[str(row[0])] = row[1]

    # Colbert ranking
    for query_id in list(queries.keys()):
        doc_ids_for_query = list(bm25_resp[str(query_id)].keys())
        print("doc_ids_for_query",len(doc_ids_for_query))
        docs = []
        for idx1 in doc_ids_for_query:
            docs.append((idx1,corpus_data[idx1]))
        processed_docs = []
        for doc in docs:
            processed_docs.append(Evidence(text=doc[1], title="", idx=doc[0]))
        query_response = colbert_search.retrieve(processed_docs, [Question(queries[query_id], idx=query_id)], top_k=1000)
        print("list(query_response.keys())[0]list(query_response.keys())[0]",len(list(query_response.keys())))
        if list(query_response.keys())[0] not in response:
            response[list(query_response.keys())[0]] = query_response[list(query_response.keys())[0]]

    metrics = RetrievalMetrics(k_values=[1, 10, 100])
    with open("runs/colbert_runfile.json","w") as f:
        json.dump(response, f)
    print("metrics", metrics.evaluate_retrieval(qrels=qrels, results=response))
