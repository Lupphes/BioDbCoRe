#!/usr/bin/env python

import argparse
import os
import json

from seq_retriver.pipeline import Pipeline


def parse_args():
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Run genome downloader pipeline.")

    parser.add_argument(
        "--mode",
        choices=["refseq", "ena", "both"],
        required=True,
        help="Mode of operation: 'refseq' to download reference genome, 'ena' to download sequencing data.",
    )

    # Arguments for both RefSeq genome and ENA sequencing data download
    parser.add_argument(
        "--taxonomy_id",
        type=int,
        required=True,
        help="Taxonomy ID (e.g., 4932) (required)",
    )
    parser.add_argument(
        "--outdir",
        required=True,
        type=str,
        help="Path to store downloaded sequences (required)",
    )

    # Arguments for RefSeq genome download
    parser.add_argument(
        "--genome_file",
        default=None,
        type=str,
        help="Path local reference genome (optional)",
    )

    # Arguments for ENA sequencing data download
    parser.add_argument(
        "--genome_size_ungapped",
        default=None,
        type=int,
        help="Reference ungapped genome size (required for 'ena' mode)",
    )
    parser.add_argument(
        "--sequences_dir",
        default=None,
        type=str,
        help="Path to the local downloaded sequences (optional)",
    )

    parser.add_argument(
        "--library_strategy",
        default=[],
        nargs="+",
        help="Library strategy (e.g., wgs synthetic-long-read hi-c)",
    )
    parser.add_argument(
        "--instrument_platform",
        default=[],
        nargs="+",
        help="Instrument platform (e.g., illumina pacbio)",
    )
    parser.add_argument(
        "--minimum_coverage", type=int, help="Minimum coverage (e.g., 40)"
    )
    parser.add_argument(
        "--maximum_coverage", type=int, help="Maximum coverage (e.g., 70)"
    )
    parser.add_argument(
        "--max_results",
        type=int,
        default=1,
        help="Max results to retrieve (default: 1)",
    )
    parser.add_argument(
        "--assembly_quality",
        default=None,
        type=str,
        help="Assembly quality filter (optional)",
    )

    return parser.parse_args()


def save_results_as_json(results, output_dir, mode):
    """
    Saves the results dictionary as a JSON file in the output directory.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{mode}_results.json")

    with open(output_file, "w") as json_file:
        json.dump(results, json_file, indent=4)

    print(f"Results saved to {output_file}")


def main():
    """Main function to run the genome downloader pipeline."""
    args = parse_args()
    args.outdir = os.path.abspath(args.outdir)

    pipeline = Pipeline(**vars(args))

    results = pipeline.run()
    if results:
        save_results_as_json(
            results, f"{args.outdir}/{args.taxonomy_id}", args.mode
        )


if __name__ == "__main__":
    main()
