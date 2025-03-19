import os
import pandas as pd
import requests
from tqdm import tqdm

from .constants import REFSEQ_ASSEMBLY_SUMMARY_URL


class RefSeqRetriver:
    """
    A class responsible for handling RefSeq genome downloads and metadata.
    """

    def __init__(self, taxonomy_id: int, outdir: str):
        self.taxonomy_id = taxonomy_id
        self.outdir = outdir
        os.makedirs(self.outdir, exist_ok=True)

        self.assembly_summary_path = os.path.join(
            self.outdir, "assembly_summary_refseq.txt"
        )
        self.parsed_dataframe_path = os.path.join(
            self.outdir, "assembly_summary_refseq.parquet"
        )

    def get_refseq_genomes(self, taxonomy_id: int, redownload: bool = False):
        """
        Fetch and download RefSeq genome data for a given taxonomy ID using pandas.
        Optionally, use a locally saved parsed DataFrame to avoid re-parsing
        the assembly summary file.

        Returns:
        - tuple: (genome_file_path, genome_size, genome_size_ungapped)
        """
        # Prepare tax-specific directory
        tax_dir = os.path.join(self.outdir, str(taxonomy_id), "refseq")
        os.makedirs(tax_dir, exist_ok=True)

        # Download the assembly summary if needed
        if not os.path.exists(self.assembly_summary_path) or redownload:
            self._download_assembly_summary()

        # Load or parse the assembly summary DataFrame
        df = self._load_parsed_assembly_summary()

        # Filter rows for the given taxonomy ID and assembly levels
        filtered_df = df[
            (df["species_taxid"] == taxonomy_id)
            & (df["assembly_level"].isin(["Complete Genome", "Chromosome"]))
        ]

        if filtered_df.empty:
            raise ValueError(f"No RefSeq genomes found for Taxonomy ID {taxonomy_id}.")

        print(
            f"Found {len(filtered_df)} RefSeq genomes. "
            f"Checking files for the first genome..."
        )

        # Construct the FTP path for the first genome
        first_genome_path = filtered_df.iloc[0]["ftp_path"]
        annotation_name = first_genome_path.split("/")[-1]
        file_name = "genomic.fna.gz"
        full_path = f"{first_genome_path}/{annotation_name}_{file_name}"

        # Local genome path
        genome_file_path = os.path.join(tax_dir, os.path.basename(full_path))

        # If the genome file doesn't exist locally, download it
        if os.path.exists(genome_file_path):
            print(
                f"Genome file already exists at {genome_file_path}. Skipping download."
            )
        else:
            self._download_genome_file(full_path, genome_file_path)

        return (
            genome_file_path,
            filtered_df.iloc[0]["genome_size"],
            filtered_df.iloc[0]["genome_size_ungapped"],
        )

    def _download_assembly_summary(self):
        """
        Download the RefSeq assembly summary file.
        """
        print("Downloading the RefSeq assembly summary file...")
        response = requests.get(REFSEQ_ASSEMBLY_SUMMARY_URL, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        with open(self.assembly_summary_path, "wb") as f, tqdm(
            desc="Downloading Assembly Summary",
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
                bar.update(len(chunk))
        print(f"Assembly summary file saved to {self.assembly_summary_path}")

    def _load_parsed_assembly_summary(self) -> pd.DataFrame:
        """
        Load (or parse and save) the assembly summary DataFrame.
        """
        if os.path.exists(self.parsed_dataframe_path):
            print(f"Loading parsed DataFrame from {self.parsed_dataframe_path}...")
            return pd.read_parquet(self.parsed_dataframe_path)
        else:
            print("Loading assembly summary into pandas DataFrame...")
            columns = [
                "assembly_accession",
                "bioproject",
                "biosample",
                "wgs_master",
                "refseq_category",
                "taxid",
                "species_taxid",
                "organism_name",
                "infraspecific_name",
                "isolate",
                "version_status",
                "assembly_level",
                "release_type",
                "genome_rep",
                "seq_rel_date",
                "asm_name",
                "submitter",
                "gbrs_paired_asm",
                "paired_asm_comp",
                "ftp_path",
                "excluded_from_refseq",
                "relation_to_type_material",
                "asm_not_live_date",
                "assembly_type",
                "group",
                "genome_size",
                "genome_size_ungapped",
                "gc_percent",
                "replicon_count",
                "scaffold_count",
                "contig_count",
                "annotation_provider",
                "annotation_name",
                "annotation_date",
                "total_gene_count",
                "protein_coding_gene_count",
                "non_coding_gene_count",
                "pubmed_id",
            ]
            df = pd.read_csv(
                self.assembly_summary_path,
                sep="\t",
                comment="#",
                header=None,
                names=columns,
                low_memory=False,
            )
            print(f"Saving parsed DataFrame to {self.parsed_dataframe_path}...")
            df.to_parquet(self.parsed_dataframe_path, index=False)
            return df

    def _download_genome_file(self, url: str, output_path: str):
        """
        Download a single genome file from the given URL to output_path.
        """
        print(f"Downloading genome from {url}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        with open(output_path, "wb") as f, tqdm(
            desc="Downloading Genome File",
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
                bar.update(len(chunk))
        print(f"Genome downloaded and saved to {output_path}")
