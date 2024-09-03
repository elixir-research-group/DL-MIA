# DL-MIA
DL-MIA  is an intent-document ranking datasets which consists of high quality user intents annotated over a small yet challenging set of
24 queries from the TREC-DL ’21 and ’22 datasets. Towards this we used a combination of LLM-generated query-specific intents and sub-intents that is post-processed through a carefully designed  crowd sourcing process to ensure human oversight and quality control. ML-DIA mainly aims to measuring the gap between user intent with query intent by fine-grained intent annotation.
# Folder structure
```
├── README.md
├── data
│   ├── intent.tsv
│   ├── qid_iid_qrel.txt
│   ├── qrels.txt
│   └── query.tsv
├── output.txt
└── src
    ├── annotation
    │   ├── LICENSE
    │   ├── README.md
    │   ├── create_exp_data_v2.py
    │   ├── data
    │   │   ├── docs.tsv
    │   │   ├── exp_data.tsv
    │   │   ├── intent_candidates.tsv
    │   │   ├── qid_docid_mapping.tsv
    │   │   └── queries.tsv
    │   ├── otree_app
    │   │   ├── Procfile
    │   │   ├── README.md
    │   │   ├── _static
    │   │   │   ├── img
    │   │   │   │   ├── example-1.png
    │   │   │   │   ├── example-2.png
    │   │   │   │   ├── example-3.png
    │   │   │   │   ├── example-4.png
    │   │   │   │   └── example-5.png
    │   │   │   └── js
    │   │   │       └── itempage_v2.js
    │   │   ├── query_intents_v2
    │   │   │   ├── ConsentPage.html
    │   │   │   ├── FeedbackPage.html
    │   │   │   ├── FinalPage.html
    │   │   │   ├── InstructionsPage.html
    │   │   │   ├── ItemPage.html
    │   │   │   └── __init__.py
    │   │   ├── requirements.txt
    │   │   └── settings.py
    │   └── start.sh
    ├── baselines
    │   ├── README.md
    │   ├── pyterrier_bm25.ipynb
    │   ├── requirements.txt
    │   └── runs
    │       ├── BM25 (intents as queries).res.gz
    │       └── BM25 (intents with original queries).res.gz
    ├── clustering.py
    └── intent_generation.py
```
## The Dataset consist of the following files:
1. intent.tsv : intent_id and intent mapping file
2. query.tsv : query_id and query mapping file.
3. qrel.tsv : intent_id,passage_id,relevance pairs. The passage_id is taken from msmarco_v2_passage corpus (https://microsoft.github.io/msmarco/TREC-Deep-Learning-2022.html)
4. qid_iid_qrel.txt: query_id, intent_id, passage_id, relevance pairs.

## Tasks and Evaluation:
The nature of the DL-MIA dataset allows it to be used not just for traditional ranking evaluation, but also for a number of additional tasks. Some possible example tasks are the following:

***Intent-based ranking*** aims at improving the document ranking by understanding different user intents and ensuring that the returned documents are relevant to the intent. This can be evaluated using standard web search metrics, such as nDCG@10.
    
***Diversity of search results*** aims at ensuring that document rankings provide diverse sets of responses that cover various aspects of the query to satisfy users information needs. Diversity may be evaluted using, for example, alpha-nDCG@10.

***Intent-based summarization*** aims at generating a summary that covers multiple intents of a query. This can be evaluated using metrics such as ROUGE or BLEU.

