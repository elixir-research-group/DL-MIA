#!/bin/sh

export DATABASE_URL=postgres://YOUR_DB_USER:YOUR_DB_PW@localhost:5432/YOUR_DB_NAME
export OTREE_ADMIN_USERNAME=admin
export OTREE_ADMIN_PASSWORD=YOUR_ADMIN_PW
export OTREE_AUTH_LEVEL=STUDY
export OTREE_PRODUCTION=1
export SECRET_KEY=YOUR_SECRET_KEY

export EXP_DATA=../data/exp_data.tsv
export EXP_QUERIES=../data/queries.tsv
export EXP_DOCS=../data/docs.tsv
export EXP_MAPPING=../data/qid_docid_mapping.tsv
export EXP_INTENT_CANDIDATES=../data/intent_candidates.tsv

export NUM_INTENT_FIELDS=5

cd otree_app
otree devserver 8000
