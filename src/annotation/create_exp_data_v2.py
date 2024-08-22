import argparse
import csv
import random
from collections import defaultdict
from math import ceil
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("Q_IDS", nargs="+", help="A list of query IDs to allocate")
    ap.add_argument(
        "--max_num_rounds",
        type=int,
        default=2,
        help="Maximum number of rounds (tasks) per participant",
    )
    ap.add_argument(
        "--out_file",
        type=Path,
        default="exp_data.tsv",
        help="Result file (.tsv)",
    )
    ap.add_argument("--seed", type=int, default=123, help="Random seed")
    args = ap.parse_args()
    random.seed(args.seed)

    num_participants = ceil(len(args.Q_IDS) / args.max_num_rounds)
    print("Number of participants required:", num_participants)
    num_rounds = ceil(len(args.Q_IDS) / num_participants)
    print("Number of rounds required:", num_rounds)

    allocation = defaultdict(list)
    for i, q_id in enumerate(args.Q_IDS):
        participant_id = i % num_participants + 1
        allocation[participant_id].append(q_id)

    # shuffle everything
    for participant_id in allocation:
        random.shuffle(allocation[participant_id])

    print("Writing", args.out_file)
    with open(args.out_file, "w", encoding="utf-8", newline="") as fp:
        writer = csv.writer(fp, delimiter="\t")
        header = ["participant_id", "round", "q_id"]
        writer.writerow(header)
        for participant_id, items in allocation.items():
            for round, q_id in enumerate(items, start=1):
                writer.writerow([participant_id, round, q_id])


if __name__ == "__main__":
    main()
