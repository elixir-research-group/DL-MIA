# Baselines

Here we provide the implementation of the baseline rankers we used, specifically, in the following tables (taken from the paper):

<details>
  <summary>Original queries, user intent QRels</summary>

|      | nDCG@10 | $\alpha$-nDCG@10 |
| :--- | :-----: | :--------------: |
| BM25 |  0.073  |      0.144       |
| BERT |  0.060  |      0.114       |

</details>
<details>
  <summary>User intents as queries, user intent QRels</summary>

|           | nDCG@10 | $\alpha$-nDCG@10 |
| :-------- | :-----: | :--------------: |
| BM25      |  0.116  |      0.250       |
| BERT      |  0.169  |      0.375       |
| ColBERTv2 |  0.261  |      0.532       |

</details>

## Requirements

Install the packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Rankers

The following describes how to reproduce the individual results in the table. The output TREC run(s) corresponding to each ranker can be found in the `runs` directory.

### BM25

BM25 results are obtained using PyTerrier. We use the provided MS MARCO v2 (passage) index. The code is available in `pyterrier_bm25.ipynb`.

### BERT

(Coming soon)

### ColBERTv2

(Coming soon)

## Evaluation

(Coming soon)
