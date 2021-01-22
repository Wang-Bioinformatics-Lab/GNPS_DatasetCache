run-local:
	nextflow run calculate_spectra_detail.nf

run-conda-cluster-test:
	nextflow run -with-conda '/Users/miw023/miniconda3/envs/antismash' assemble_antismash.nf -resume --reads "/data/ccms-data/uploads/tferreir/ENA_reads/ERR3958150_{1,2}.fastq.gz"

run-conda-cluster-full:
	nextflow run -c cluster.config assemble_antismash.nf -with-report "nf_report.html" -with-trace "nf_trace.html" -resume --reads "/data/ccms-data/uploads/tferreir/ENA_reads/*_{1,2}.fastq.gz"