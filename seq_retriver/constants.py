# Supported
SUPPORTED_LIBRARY_STRATEGY = [
    "WGS",  # Whole Genome Sequencing
    "WGA",  # Whole Genome Amplification
    "WXS",  # Whole Exome Sequencing
    "RNA-Seq",  # Whole Transcriptome Shotgun Sequencing
    "ssRNA-seq",  # Strand-specific RNA sequencing
    "miRNA-Seq",  # Micro RNA sequencing
    "ncRNA-Seq",  # Non-coding RNA sequencing
    "FL-cDNA",  # Full-length cDNA sequencing
    "EST",  # Expressed Sequence Tag
    "Hi-C",  # Chromosome Conformation Capture
    "ATAC-seq",  # Assay for Transposase-Accessible Chromatin
    "WCS",  # Whole Chromosome Sequencing
    "RAD-Seq",  # Restriction Site-Associated DNA Sequencing
    "AMPLICON",  # Sequencing of PCR products
    "CLONE",  # Genomic clone-based sequencing
    "POOLCLONE",  # Pooled clone sequencing
    "CLONEEND",  # Clone end sequencing
    "FINISHING",  # Gap-closing sequencing
    "ChIP-Seq",  # Chromatin Immunoprecipitation sequencing
    "MNase-Seq",  # Micrococcal Nuclease sequencing
    "Ribo-Seq",  # Ribosome profiling
    "DNase-Hypersensitivity",  # Open chromatin sequencing
    "Bisulfite-Seq",  # DNA methylation sequencing
    "CTS",  # Concatenated Tag Sequencing
    "MRE-Seq",  # Methylation-sensitive sequencing
    "MeDIP-Seq",  # Methylated DNA Immunoprecipitation Sequencing
    "MBD-Seq",  # Methyl CpG Binding Domain Sequencing
    "Tn-Seq",  # Transposon insertion sequencing
    "VALIDATION",  # Variant validation
    "FAIRE-seq",  # Regulatory element sequencing
    "SELEX",  # Ligand selection sequencing
    "RIP-Seq",  # RNA immunoprecipitation sequencing
    "ChIA-PET",  # Chromatin interaction analysis
    "Synthetic-Long-Read",  # Long-read assembly
    "Targeted-Capture",  # Target enrichment sequencing
    "Tethered Chromatin Conformation Capture",  # Chromatin capture
    "OTHER",  # Unlisted library strategies
]

SUPPORTED_INSTRUMENT_PLATFORM = [
    "Illumina",  # Widely used for short-read sequencing
    "PacBio",  # Single Molecule Real-Time (SMRT) sequencing for long reads
    "Nanopore",  # Oxford Nanopore sequencing for long reads
    "IonTorrent",  # Ion semiconductor sequencing
    "BGISEQ",  # BGI sequencing technology
    "HiSeq",  # Illumina HiSeq platform
    "NextSeq",  # Illumina NextSeq platform
    "MiSeq",  # Illumina MiSeq platform
    "NovaSeq",  # Illumina NovaSeq platform
    "454",  # Pyrosequencing (discontinued but still in legacy data)
    "SOLiD",  # Sequencing by Oligonucleotide Ligation and Detection
]

# Database URLs
NCBI_REFSEQ_URL = "https://ftp.ncbi.nlm.nih.gov/genomes/refseq/"
ENA_READ_RUN_URL = "https://www.ebi.ac.uk/ena/portal/api/search"
ENA_QUERY_FIELDS = "run_accession,library_strategy,base_count,first_public"
REFSEQ_ASSEMBLY_SUMMARY_URL = (
    "https://ftp.ncbi.nlm.nih.gov/genomes/refseq/assembly_summary_refseq.txt"
)
