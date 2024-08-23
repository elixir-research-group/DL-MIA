# User Intent Annotation

We use the [oTree](https://www.otree.org/) library to collect annotations (user intents for web search queries) from crowdsourcing workers. This repository contains the oTree application, i.e., the interface we created for our paper.

Please consult the [oTree documentation](https://otree.readthedocs.io/en/latest/) to learn more about how to use this app.

## Setting Up and Running the App

Install the requirements from `otree_app/requirements.txt` using `pip`. A PostgreSQL instance is required to run a production server. More information can be found [here](https://otree.readthedocs.io/en/latest/server/ubuntu.html#ubuntu-linux-server).

The easiest way to launch the app is using `start.sh`. This sets the necessary environment variables and starts the server. **Make sure to replace any placeholders in the script** (such as your database connection, passwords, and the secret key).

Furthermore, the app requires a number of `.tsv` files to run. Example files to demonstrate the format can be found in `data`:

- `data/docs.tsv`: Maps document IDs to document texts.
- `data/queries.tsv`: Maps query IDs to query texts.
- `data/intent_candidates.tsv`: Maps query IDs to intent candidates (these correspond to LLM-generated intents).
- `data/qid_docid_mapping.tsv`: Maps query IDs to IDs of relevant documents (these documents will be shown to the participants as a list).
- `data/exp_data.tsv`: Maps each combination of a participant ID and a round number to a query ID (this controls which queries are seen by which participants). Can be generated using `create_exp_data_v2.py`.

Finally, `NUM_INTENT_FIELDS` controls the number of text fields (for intent candidates and new intents) presented to the participants.

## Parsing the Results

After the annotations are complete, the resulting data can be downloaded from the oTree web interface as a plain `.csv` file. This file contains **one row for each participant**. The relevance assessments can be found in the following columns:

- `query_intents_v2.<ROUND>.player.result_assessments`
- `query_intents_v2.<ROUND>.player.result_<INTENT>`

For example, in round 2, the value of `query_intents_v2.2.player.result_assessments` may be `doc1:::i1 doc3:::i1 doc3:::i2`. This means that the participant selected the following:

- `doc1` and `doc3` are relevant for `i1`.
- `doc3` is relevant for `i2`.

The values of `i1` and `i2` can then be accessed using `query_intents_v2.2.player.result_i1` and `query_intents_v2.2.player.result_i2`, respectively.

## Data

The original data we used for the DL-MIA annotations can be downloaded [here](https://drive.google.com/file/d/16hjYJD4l4C37nov-vU0tIjP-Sb8nI3_8/view?usp=sharing). Note that `docs.tsv` and `queries.tsv` are not included. These need to be created using documents and queries from the [MS MARCO v2 passage ranking dataset](https://ir-datasets.com/msmarco-passage-v2.html#msmarco-passage-v2). Note that:

- Only queries and documents that appear in `qid_docid_mapping.tsv` need to be present in those files.
- Query IDs that contain an underscore (such as `12345_1`) are _subqueries_. As a result, the query IDs `12345`, `12345_1`, `12345_2`, and so on **all correspond to the same query**.
