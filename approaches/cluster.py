# conda env bert_test
import argparse
import pandas as pd

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
    Generate clusters from pair entailment data.

    Args:
        entailment_out (str): Path to the pair entailment data file.
        thres (float, optional): Threshold value for clustering. Defaults to 0.5.
        is_sbert (bool, optional): Flag indicating whether the data is from SBERT. Defaults to False.

    Returns:
        pandas.DataFrame: DataFrame containing the clusters generated from the pair entailment data.
    """
    df_final = pd.DataFrame()

    # Load entailment data
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
    Perform clustering on the entailment output.

    Args:
        entailment_out (str): Path to the entailment output file.
        thres (float): Threshold value for clustering.
        is_sbert (bool): Flag indicating whether the entailment output is generated using SBERT.
        cluster_outfile (str): Path to save the resulting clustered intents.

    Returns:
        pandas.DataFrame: DataFrame containing the clustered intents.
    """
    # Generate clusters from the pair entailment data
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


if __name__ == '__main__':
    # Initialize argument parser
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    # Add arguments
    ap.add_argument('--entail_file', type=str, required=True, help='Path to the entailment output file')
    ap.add_argument('--cluster_outfile', type=str, required=True, help='Path to save the cluster output file')
    ap.add_argument('--threshold', type=float, default=0.5, help='Threshold for clustering')
    ap.add_argument('--is_sbert', action='store_true', help='Flag to indicate if the entailment output is generated using SBERT')
    
    # Parse arguments
    args = ap.parse_args()
    
    # Run clustering function with provided arguments
    clustering(args.entail_file, args.threshold, args.is_sbert, args.cluster_outfile)
