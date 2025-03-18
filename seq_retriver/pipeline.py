import os
import gzip

from .refseq_retriver import RefSeqRetriver
from .ena_searcher import ENASearcher


class Pipeline:
    """
    A main pipeline class to run all steps:
    1. Fetch reference genome from RefSeq.
    2. Search ENA for sequencing runs.
    3. Download FASTQ files.
    """

    def __init__(
        self,
        taxonomy_id: int,
        outdir: str,
        mode: str,
        genome_file: str = None,
        sequences_dir: str = None,
        genome_size_ungapped: int = None,
        **kwargs,
    ):
        self.taxonomy_id = taxonomy_id
        self.outdir = os.path.abspath(outdir)
        self.mode = mode
        self.genome_file = genome_file
        self.sequences_dir = sequences_dir
        self.genome_size_ungapped = genome_size_ungapped

        os.makedirs(self.outdir, exist_ok=True)

        self.refseq_retriver = RefSeqRetriver(
            taxonomy_id=self.taxonomy_id, outdir=self.outdir
        )

        self.ena_searcher = ENASearcher(
            taxonomy_id=self.taxonomy_id,
            library_strategy=(
                [x.lower() for x in kwargs.get("library_strategy", [])]
                if kwargs.get("library_strategy")
                else None
            ),
            instrument_platform=(
                [x.lower() for x in kwargs.get("instrument_platform", [])]
                if kwargs.get("instrument_platform")
                else None
            ),
            max_results=kwargs.get("max_results", 10),
            min_coverage=kwargs.get("minimum_coverage"),
            max_coverage=kwargs.get("maximum_coverage"),
            assembly_quality=kwargs.get("assembly_quality"),
            sort=True,
        )

    def run(self):
        """Runs the appropriate pipeline based on the selected mode."""
        if self.mode == "refseq":
            return self.run_refseq()
        elif self.mode == "ena":
            return self.run_ena()
        elif self.mode == "both":
            refseq_results = self.run_refseq()
            self.genome_size = refseq_results.get("genome_size", self.genome_size)
            self.genome_size_ungapped = refseq_results.get(
                "genome_size_ungapped", self.genome_size_ungapped
            )
            self.genome_file = refseq_results.get("genome_file", self.genome_file)
            self.run_ena()
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")

    def run_refseq(self) -> dict[str, str]:
        """Fetches the reference genome from RefSeq."""
        if self.genome_file:
            print(f"Using local reference genome: {self.genome_file}")
            self.genome_size, self.genome_size_ungapped = (
                self.calculate_genome_size_from_file(self.genome_file)
            )
        else:
            print("Fetching RefSeq genome data...")
            self.genome_file, self.genome_size, self.genome_size_ungapped = (
                self.refseq_retriver.get_refseq_genomes(self.taxonomy_id)
            )

        print(f"Genome size: {self.genome_size} bp")
        print(f"Ungapped genome size: {self.genome_size_ungapped} bp")
        print(f"RefSeq genome saved to: {self.genome_file}")

        # relative_genome_file_path = os.path.relpath(self.genome_file, start=os.path.dirname(self.outdir))

        return {
            "genome_file": self.genome_file,
            "genome_size": self.genome_size,
            "genome_size_ungapped": self.genome_size_ungapped,
        }

    def run_ena(self):
        """Executes the ENA search and FASTQ file download pipeline."""
        if self.sequences_dir:
            # If user provided a local directory, we skip downloading
            print(f"Using local sequences from directory: {self.sequences_dir}")
            files = self.list_sequence_files(self.sequences_dir)
            return {"sequences_dir": self.sequences_dir, "sequence_files": files}
        else:
            self.sequences_dir = os.path.join(
                self.outdir,
                str(self.taxonomy_id),
                "sequences"
            )

        print("Searching for sequence data in ENA...")
        # If no genome_size_ungapped is provided, or the user gave us a genome_file:
        if not self.genome_size_ungapped and self.genome_file:
            self.genome_size, self.genome_size_ungapped = self.calculate_genome_size_from_file(self.genome_file)
        elif self.genome_size_ungapped:
            print(f"Using provided ungapped genome size: {self.genome_size_ungapped}")
        else:
            print("Genome size not provided. The coverage filter may not be optimal without it.")

        sequence_data = self.ena_searcher.search_sequence_data(genome_size_ungapped=self.genome_size_ungapped)
        if not sequence_data:
            print("No sequence data found.")
            return {"sequences_dir": self.sequences_dir, "sequence_data": []}

        print("Downloading FASTQ files...")
        # We now capture the returned dict {run_accession -> list of file paths}
        run_accession_to_files = self.ena_searcher.fetch_fastq_files(sequence_data, self.sequences_dir)

        # Optionally, you can still call list_sequence_files if you want a quick flat listing
        # But your main structure is in run_accession_to_files
        # This list won't show the pairing, just the total files in self.sequences_dir
        all_downloaded = self.list_sequence_files(self.sequences_dir, print_files=False)

        # Return both the base directory and the run-accession->files mapping
        return {
            "sequences_dir": self.sequences_dir,
            "run_accession_to_files": run_accession_to_files,
            "all_files_flat": all_downloaded
        }


    def list_sequence_files(self, directory: str, print_files: bool = True) -> list[str]:
        """
        Recursively lists all files under 'directory' and returns a list of full paths.
        """
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist.")
            return []

        file_paths = []
        for root, dirs, files in os.walk(directory):
            for name in files:
                file_paths.append(os.path.join(root, name))

        if not file_paths:
            print("No sequence files found in the directory.")
            return []

        if print_files:
            print("\nSequence files found in the directory:")
            for fp in file_paths:
                print(f"- {fp}")

        return file_paths


    def calculate_genome_size_from_file(self, genome_file: str) -> tuple[int, int]:
        """Calculates genome size by summing sequence lengths from a genome file (handles both .gz and plain text)."""
        genome_size = 0
        genome_size_ungapped = 0

        # Determine if file is gzipped
        open_func = gzip.open if genome_file.endswith(".gz") else open

        with open_func(
            genome_file, "rt", encoding="utf-8"
        ) as f:  # 'rt' ensures reading text mode
            for line in f:
                if not line.startswith(">"):
                    sequence = line.strip()
                    genome_size += len(sequence)
                    genome_size_ungapped += len(sequence.replace("N", ""))

        return genome_size, genome_size_ungapped
