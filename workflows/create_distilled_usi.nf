#!/usr/bin/env nextflow
nextflow.enable.dsl=2

TOOL_FOLDER = "$baseDir/bin_local"

process getcachefiles {
    publishDir "./nf_output", mode: 'copy'

    conda "$TOOL_FOLDER/conda_env.yml"

    input:
    val x

    output:
    file 'all_dataset_files.csv'

    """
    wget 'http://gnps-datasetcache-datasette:5234/datasette/database/filename.csv?_stream=on&_size=max' -O all_dataset_files.csv
    """
}

process processUniqueUSI {
    publishDir "./nf_output", mode: 'copy'

    conda "$TOOL_FOLDER/conda_env.yml"

    input:
    file 'all_dataset_files.csv'

    output:
    file 'all_unique_mri.tsv'

    """
    python $TOOL_FOLDER/subset_GNPS2chache_to_MS_files.py \
    --input_path "all_dataset_files.csv" \
    --output_path all_unique_mri.tsv
    """
}

workflow {
    all_dataset_files_ch = getcachefiles(1)
    processUniqueUSI(all_dataset_files_ch)
}
