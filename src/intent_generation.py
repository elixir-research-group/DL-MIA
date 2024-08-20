from openai import OpenAI
import pandas as pd
import time
from typing import Any, Dict, Generator
import timeit
import argparse
from pathlib import Path

class LLMRewriter:
    def __init__(self, data_file: str, hparams: Dict[str, Any]) -> None:
        """
        LLMRewriter class to generate intents from queries and documents using LLM.
        
        Args:
            data_file (str): Path to the data file.
            hparams (Dict[str, Any]): Hyperparameters for the model.
        """
        self.client = OpenAI(api_key=hparams.get("api_key", "<add api key here>"))
        self.skip_row = hparams.get("skip_row", 0)
        self.model_name = hparams["model_name"]
        self.temperature = hparams.get("temperature", 0.7)
        self.top_p = hparams.get("top_p", 1.0)
        self.max_tokens = hparams.get("max_tokens", 100)
        self.frequency_penalty = hparams.get("frequency_penalty", 0.0)
        self.presence_penalty = hparams.get("presence_penalty", 0.0)
        self.final_out_file = hparams["final_out_file"]
        self.is_chatgpt = hparams.get("is_chatgpt", False)
        
        print(f"Model: {self.model_name}, data_file: {data_file}, is_ChatGPT: {self.is_chatgpt}")
        
        self.df_final = pd.read_csv(data_file, delimiter="\t", header=None, skiprows=self.skip_row,
                                    names=["q_id", "doc_id", "query", "doc"])
        print(f"Number of queries: {self.df_final.q_id.nunique()}")

    def model_prompts(self, query: str, doc: str) -> Any:
        """Generates a prompt for the model and retrieves the response."""
        if self.is_chatgpt:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an intelligent system and your job is to predict the intention behind the user question given a list of documents."
                    },
                    {
                        "role": "user",
                        "content": f"A person wants to find out the distinct intention behind the question '{query}'. Provide five distinct and descriptive (max. 15 words) intentions that are easy to understand. Consider all documents in your response. Response should be in this format: Intention:: <intention> , Doc_list::<list of documents with the intention>\n\nDocuments: {doc}"
                    },
                ]
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model_name,
                prompt=f"A person wants to find out the distinct intention behind the question '{query}'. Provide five distinct and descriptive (max. 15 words) intentions that are easy to understand. Consider all documents in your response. Response should be in this format: Intention:: <intention> , Doc_list::<list of documents with the intention>\n\nDocuments: {doc}",
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty
            )
        return response

    @staticmethod
    def chunk(seq: pd.DataFrame, size: int) -> Generator[pd.DataFrame, None, None]:
        """Yields chunks of a DataFrame."""
        for pos in range(0, len(seq), size):
            yield seq[pos:pos + size]

    def get_gpt3_completions(self) -> pd.DataFrame:
        """
        Retrieves LLM completions for each query in the dataset.

        Returns:
            final_df (pd.DataFrame): DataFrame containing the query ID, query, and LLM completion for each query.
        """
        job_data = {"q_id": [], "doc_id": [], "query": [], "description": []}
        i, index = 0, 0
        n = 10
        start = timeit.default_timer()
        qid_list = self.df_final.q_id.unique()

        for qid in qid_list:
            df_query = self.df_final[self.df_final["q_id"] == qid]
            for df_chunk in self.chunk(df_query, n):
                str_doc_ids = ",".join(df_chunk.doc_id)
                query_str = df_query["query"].iloc[0]
                df_chunk["doc_merge"] = df_chunk["doc_id"] + ": " + df_chunk["doc"]
                str_final_doc = "\n".join(df_chunk.doc_merge)

                job_data["q_id"].append(qid)
                job_data["doc_id"].append(str_doc_ids)
                job_data["query"].append(query_str)

                try:
                    if index % 20 == 0 and index != 0:
                        print(f"Processed {index} chunks.")
                    response = self.model_prompts(query_str, str_final_doc)
                except Exception as e:
                    print("Error encountered:", e)
                    time.sleep(60)
                    response = self.model_prompts(query_str, str_final_doc)

                if self.is_chatgpt:
                    llm_response = response.choices[0].message.content.strip().replace("\n", "").replace("\t", "")
                else:
                    llm_response = response["choices"][0]["text"].strip()

                print(f"q_id: {qid}, query: {query_str}, Response: {llm_response}")

                job_data["description"].append(llm_response)
                final_df = pd.DataFrame(job_data)
                final_df.to_csv(self.final_out_file, sep="\t", index=False)

                if i % 10000 == 0:
                    print(f"Queries completed: {i}")
                if i % 100 == 0:
                    print(f"Time for {i} requests: {timeit.default_timer() - start:.2f} seconds")

                i += 1
                index += 10

        return final_df

def main() -> None:
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument('DATA_DIR', help='Folder with all preprocessed files')
    ap.add_argument('--data_file', type=str, default="pass_all_train_query_car_12k.tsv", help='dataset file name')
    ap.add_argument('--model_name', type=str, default="text-davinci-003", help='llm model name')
    ap.add_argument('--final_out_file', type=str, default="pass_rewrite_query_davinci_car_12k.tsv", help='out file_name')
    ap.add_argument('--temperature', type=float, default=0.6)
    ap.add_argument('--top_p', type=float, default=1.0)
    ap.add_argument('--frequency_penalty', type=float, default=0.0)
    ap.add_argument('--presence_penalty', type=float, default=0.0)
    ap.add_argument('--max_tokens', type=int, default=512)
    ap.add_argument('--skip_row', type=int, default=0)
    ap.add_argument('--is_chatgpt', action='store_true', help='if model is chatgpt')
    ap.add_argument('--only_query', action='store_true', help='if generating only from query')
    ap.add_argument('--if_groundtruth', action='store_true', help='for groundtruth generation')
    args = ap.parse_args()

    data_dir = Path(args.DATA_DIR)
    data_file = data_dir / args.data_file

    print("Final out file:{}".format(args.final_out_file))
    if args.if_groundtruth:
        llm_rewriter = LLMRewriter(data_file,vars(args))
        df = llm_rewriter.get_gpt3_completions()
    else:
        llm_rewriter = LLMRewriter(data_file,vars(args))
        if args.only_query:
            df_query = pd.read_csv(data_file, delimiter="\t", header=None,skiprows=1,
                                        names=["q_id", "query"])
            df = llm_rewriter.get_gpt3_completions_query(df_query)
        else:
            df = llm_rewriter.get_gpt3_completions()
    print(df.head())

if __name__ == '__main__':
    main()
