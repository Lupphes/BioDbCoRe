import os
import requests
from tqdm import tqdm
from urllib.parse import urlsplit

from .constants import ENA_READ_RUN_URL


class ENASearcher:
    """
    A class responsible for querying the ENA database for sequencing runs
    and downloading FASTQ files based on various criteria.
    """

    def __init__(
        self,
        taxonomy_id: int,
        library_strategy=None,
        instrument_platform=None,
        max_results: int = 10,
        min_coverage: int = None,
        max_coverage: int = None,
        assembly_quality=None,
        sort=False,
    ):
        self.taxonomy_id = taxonomy_id
        self.library_strategy = library_strategy
        self.instrument_platform = instrument_platform
        self.max_results = max_results
        self.min_coverage = min_coverage
        self.max_coverage = max_coverage
        self.assembly_quality = assembly_quality
        self.sort = sort

    def search_sequence_data(self, genome_size_ungapped: int = None) -> list:
        """
        Query the ENA database for sequencing runs based on taxonomy ID, study type,
        platform, genome size, and assembly quality.

        Returns:
        - list: Sorted list of results (dicts), limited to max_results.
        """
        query_parts = [f"tax_eq({self.taxonomy_id})"]

        if self.library_strategy and self.library_strategy != []:
            query_parts.append(
                " OR ".join(
                    f'library_strategy="{stype}"' for stype in self.library_strategy
                )
            )

        if self.instrument_platform and self.instrument_platform != []:
            query_parts.append(
                " OR ".join(
                    f'instrument_platform="{platform}"'
                    for platform in self.instrument_platform
                )
            )

        if self.min_coverage is not None and genome_size_ungapped is not None:
            query_parts.append(
                f"base_count>={genome_size_ungapped * self.min_coverage}"
            )

        if self.max_coverage is not None and genome_size_ungapped is not None:
            query_parts.append(
                f"base_count<={genome_size_ungapped * self.max_coverage}"
            )

        if self.assembly_quality and not self.assembly_quality == "":
            query_parts.append(f"assembly_quality={self.assembly_quality}")

        query = " AND ".join(f"({part})" for part in query_parts if part)

        # Define query parameters
        params = {
            "result": "read_run",
            "query": query,
            "fields": "run_accession,library_strategy,instrument_platform,base_count,"
            "read_count,description,last_updated,fastq_ftp,assembly_quality",
            "format": "json",
            "limit": 10000,
        }

        print(f"Sending query to ENA: {params['query']}")
        response = requests.get(ENA_READ_RUN_URL, params=params)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"HTTPError: {e}")
            print(f"Response Content: {response.text}")
            raise

        results = response.json()

        # Calculate coverage if genome_size is known
        for record in results:
            base_count = int(record.get("base_count", 0))
            record["coverage"] = (
                None
                if genome_size_ungapped is None or genome_size_ungapped == 0
                else base_count / genome_size_ungapped
            )

        # Define rankings for library strategies and platforms (lower rank = higher priority)
        library_strategy_rank = {"wgs": 1, "synthetic-long-read": 2, "hi-c": 3}
        instrument_platform_rank = {"pacbio": 1, "illumina": 2}

        # Sort results
        if self.sort:
            sorted_results = sorted(
                results,
                key=lambda x: (
                    library_strategy_rank.get(
                        x.get("library_strategy", "").lower(), float("inf")
                    ),
                    instrument_platform_rank.get(
                        x.get("instrument_platform", "").lower(), float("inf")
                    ),
                    -int(x.get("base_count", 0)),
                    x.get("last_updated", ""),
                ),
            )
        else:
            sorted_results = results

        return sorted_results[: self.max_results]

    def fetch_fastq_files(
        self, sequence_data: list, outdir: str = "data", max_files: int = None
    ) -> dict[str, list[str]]:
        """
        Download FASTQ files from the URLs provided in the sequence data, placing each run's files
        in a subfolder named after its run accession.

        Parameters:
        - sequence_data (list): List of dicts with run metadata (including 'fastq_ftp').
        - outdir (str): Base directory to save the downloaded FASTQ files.
        - max_files (int): Maximum number of total files to download. None = no limit.

        Returns:
        - dict[str, list[str]]: run_accession -> list of downloaded file paths
        """
        import requests
        from tqdm import tqdm
        from urllib.parse import urlsplit

        os.makedirs(outdir, exist_ok=True)
        downloaded_count = 0

        # This dict will store run_accession -> [list_of_downloaded_file_paths]
        run_to_files = {}

        with tqdm(total=len(sequence_data), desc="Downloading FASTQ records", unit="rec") as progress_bar:
            for record in sequence_data:
                fastq_ftp = record.get("fastq_ftp", None)
                run_accession = record.get("run_accession", "N/A")

                # Prepare a list to store all file paths for this run
                record_files = []

                if not fastq_ftp:
                    print(f"No FASTQ URL found for record: {run_accession}")
                    run_to_files[run_accession] = record_files
                    progress_bar.update(1)
                    continue

                # Split the FTP string into individual FASTQ URLs
                fastq_urls = fastq_ftp.split(";")

                # Create a subdirectory for this run
                run_dir = os.path.join(outdir, run_accession)
                os.makedirs(run_dir, exist_ok=True)

                for url in fastq_urls:
                    if max_files is not None and downloaded_count >= max_files:
                        print("Download limit reached. Stopping.")
                        return run_to_files

                    filename = os.path.basename(urlsplit(url).path)
                    file_path = os.path.join(run_dir, filename)

                    # If the file already exists, skip it
                    if os.path.exists(file_path):
                        print(f"File already exists: {file_path}. Skipping download.")
                        record_files.append(file_path)
                        continue

                    # Perform the download (ENA provides FTP; use http:// for direct GET)
                    print(f"Downloading {filename} from {url}...")
                    try:
                        response = requests.get(f"http://{url}", stream=True)
                        response.raise_for_status()

                        total_size = int(response.headers.get("content-length", 0))
                        with open(file_path, "wb") as f, tqdm(
                            desc=f"Downloading {filename}",
                            total=total_size,
                            unit="B",
                            unit_scale=True,
                            unit_divisor=1024,
                            leave=False
                        ) as file_bar:
                            for chunk in response.iter_content(chunk_size=1024):
                                f.write(chunk)
                                file_bar.update(len(chunk))

                        print(f"Downloaded {filename} to {file_path}")
                        record_files.append(file_path)
                        downloaded_count += 1

                    except requests.exceptions.RequestException as e:
                        print(f"Failed to download {filename} from {url}: {e}")

                # Store the file paths for this run
                run_to_files[run_accession] = record_files
                progress_bar.update(1)

        return run_to_files
