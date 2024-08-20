# conda env bert_test
import argparse
import pandas as pd
import torch
import pandas as pd
import argparse
import time
from sentence_transformers import SentenceTransformer, util

def get_cluster_per_query(df, thres):
    """
    Assigns cluster numbers to queries based on their main and mac intents.

    Args:
        df (DataFrame): The input DataFrame containing query information.
        thres (float): The threshold score for assigning cluster numbers.

    Returns:
        dict: A dictionary mapping query IDs to their respective cluster numbers.
    """
    dict_doc_cluster = {}
    clus_num = 0
    
    for _, row in df.iterrows():
        main_intent = row['main_intent']
        mac_intent = row['mac_intent']
        score = row['score']
        
        if main_intent not in dict_doc_cluster:
            clus_num += 1
            dict_doc_cluster[main_intent] = clus_num
        
        main_intent_clus = dict_doc_cluster[main_intent]
        
        if mac_intent not in dict_doc_cluster:
            dict_doc_cluster[mac_intent] = main_intent_clus if score > thres else clus_num + 1
            if score <= thres:
                clus_num += 1
        elif score > thres:
            dict_doc_cluster[mac_intent] = main_intent_clus
    
    return dict_doc_cluster


def get_clusters_from_pair_entailment(entailment_out, thres=0.5, is_sbert=False):
    """
    Generate clusters from pair similarity data.

    Args:
        entailment_out (str): Path to the pair similarity data file.
        thres (float, optional): Threshold value for clustering. Defaults to 0.5.
        is_sbert (bool, optional): Flag indicating whether the data is from SBERT. Defaults to False.

    Returns:
        pandas.DataFrame: DataFrame containing the clusters generated from the pair similarity data.
    """
    df_final = pd.DataFrame()

    # Load similarity data
    df_entail = pd.read_csv(entailment_out, sep='\t')
    
    # Calculate the score based on SBERT flag
    df_entail['score'] = df_entail['sentence_sim'] if is_sbert else df_entail['score1'] + df_entail['score2']
    
    # Iterate over unique query IDs and generate clusters
    for query_id in df_entail['q_id'].unique():
        df_query = df_entail[df_entail['q_id'] == query_id]
        dict_doc_cluster = get_cluster_per_query(df_query, thres)
        
        df_temp = pd.DataFrame(dict_doc_cluster.items(), columns=['machine_intent', 'cluster'])
        df_temp['q_id'] = query_id
        df_final = pd.concat([df_final, df_temp], ignore_index=True)
    
    df_final = df_final[['q_id', 'machine_intent', 'cluster']]
    
    print("Clustering Done!!")
    return df_final


def clustering(entailment_out, thres, is_sbert, cluster_outfile):
    """
    Perform clustering on the similarity output.

    Args:
        entailment_out (str): Path to the similarity output file.
        thres (float): Threshold value for clustering.
        is_sbert (bool): Flag indicating whether the similarity output is generated using SBERT.
        cluster_outfile (str): Path to save the resulting clustered intents.

    Returns:
        pandas.DataFrame: DataFrame containing the clustered intents.
    """
    # Generate clusters from the pair similarity data
    df_clusters = get_clusters_from_pair_entailment(entailment_out, thres, is_sbert)
    
    # Group by 'q_id' and 'cluster', and concatenate 'machine_intent' values
    df_clus = df_clusters.groupby(['q_id', 'cluster'])['machine_intent'].apply(','.join).reset_index()
    
    # Sort the clustered DataFrame
    df_clus = df_clus.sort_values(by=['q_id', 'cluster'], ascending=[True, True])
    
    # Assign unique 'intent_id' to each (q_id, cluster) pair
    df_clus['intent_id'] = df_clus.groupby('q_id').ngroup().add(1)
    df_clus['intent_id'] = "22_" + df_clus['intent_id'].astype(str)
    
    # Calculate the number of machine intents in each cluster
    df_clus['num_intents'] = df_clus['machine_intent'].str.count(',').add(1)
    
    # Calculate total number of intents per query (q_id)
    df_total_intents = df_clus.groupby('q_id')['num_intents'].sum().reset_index(name='total_intents')
    
    # Merge total intents back into the clustered DataFrame
    df_clus = df_clus.merge(df_total_intents, on='q_id', how='left')
    
    # Calculate the percentage of intents in each cluster
    df_clus['percentage'] = round(df_clus['num_intents'] * 100 / df_clus['total_intents'], 2)
    
    # Save the result to the specified file
    df_clus.to_csv(cluster_outfile, sep='\t', index=False)
    
    print(f"Clustering complete. {len(df_clus)} clusters created.")
    
    return df_clus

class Similarity:
    """Calculates similarity between intents."""

    def __init__(self, base_model: str = "distilbert-base-nli-mean-tokens") -> None:
        """Initializes the Similarity class with a specified Sentence-BERT model.

        Args:
            base_model (str, optional): The base model to use. Defaults to "distilbert-base-nli-mean-tokens".
        """
        self.sentence_model = SentenceTransformer(base_model)

    def sentence_bert_similarity(self, sentence1: str, sentence2: str) -> float:
        """Calculates similarity between two sentences using Sentence-BERT embeddings.

        Args:
            sentence1 (str): The first sentence.
            sentence2 (str): The second sentence.

        Returns:
            float: Similarity score between the two sentences.
        """
        embeddings1 = self.sentence_model.encode(sentence1)
        embeddings2 = self.sentence_model.encode(sentence2)
        result = util.pytorch_cos_sim(embeddings1, embeddings2)
        return round(result.item(), 3)

    def get_all_pair_similarity(self, df_llm: pd.DataFrame, entailment_out: str) -> None:
        """Computes similarity scores for all pairs of queries in the dataframe.

        Args:
            df_llm (pd.DataFrame): Dataframe containing query information.
            entailment_out (str): Filepath to save the similarity scores.
        """
        print(f"# rows: {len(df_llm)}, #queries: {df_llm['query'].nunique()}")
        query_ids = set(df_llm.q_id.to_list())
        entailment_data = {
            "q_id": [], 
            "main_intent": [], 
            "mac_intent": [], 
            "sentence_sim": []
        }

        start_time = time.time()
        for i, qid in enumerate(query_ids):
            df_query = df_llm[df_llm["q_id"] == qid].reset_index()
            for index, row in df_query.iterrows():
                main_intent = row["machine_intent"]
                df_compare = df_query.iloc[index + 1:]
                for _, srow in df_compare.iterrows():
                    sentence_sim = self.sentence_bert_similarity(main_intent, srow["machine_intent"])
                    entailment_data["q_id"].append(srow["q_id"])
                    entailment_data["main_intent"].append(main_intent)
                    entailment_data["mac_intent"].append(srow["machine_intent"])
                    entailment_data["sentence_sim"].append(sentence_sim)

            if (i + 1) % 100 == 0:
                print(f"Processed 100 records in {time.time() - start_time:.3f} seconds")
                start_time = time.time()

        entailment_df = pd.DataFrame(entailment_data)
        entailment_df.to_csv(entailment_out, index=False)


if __name__ == '__main__':
    # Initialize argument parser
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    # Add arguments
    ap.add_argument('--cluster_outfile', type=str, required=True, help='Path to save the cluster output file')
    ap.add_argument('--threshold', type=float, default=0.5, help='Threshold for clustering')
    ap.add_argument('--is_sbert', action='store_true', help='Flag to indicate if the similarity output is generated using SBERT')
    ap.add_argument("--llm_file", type=str, required=True, help="Path to the CSV file with LLM data.")
    ap.add_argument("--similarity_out", type=str, required=True, help="Output path for the similarity results.")
    
    
    # Parse arguments
    args = ap.parse_args()
    
    print("Fetching similarity pairs...")
    df_llm = pd.read_csv(args.llm_file)
    sim = Similarity()
    sim.get_all_pair_similarity(df_llm, args.similarity_out)

    # Run clustering function with provided arguments
    clustering(args.similarity_out, args.threshold, args.is_sbert, args.cluster_outfile)
