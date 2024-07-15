#!/usr/bin/env nextflow
nextflow.enable.dsl=2

params.mtblstoken = ""

TOOL_FOLDER = "$baseDir/bin"

process mwbFiles {
    publishDir "./nf_output", mode: 'copy'

    conda "$TOOL_FOLDER/conda_env.yml"

    input:
    val x

    output:
    file 'MWBFilePaths_ALL.tsv'

    """
    python $TOOL_FOLDER/getAllWorkbench_file_paths.py \
    --study_id ALL \
    --output_path MWBFilePaths_ALL.tsv
    """
}

process mtblsFiles {
    publishDir "./nf_output", mode: 'copy'

    conda "$TOOL_FOLDER/conda_env.yml"

    input:
    val x

    output:
    file 'MetabolightsFilePaths_ALL.tsv'

    """
    python $TOOL_FOLDER/getAllMetabolights_file_paths.py \
    --output_filename "MetabolightsFilePaths_ALL.tsv" \
    --user_token $params.mtblstoken
    """
}

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

    conda "$baseDir/bin_local/conda_env.yml"

    input:
    file 'all_dataset_files.csv'

    output:
    file 'all_unique_mri.tsv'

    """
    python $baseDir/bin_local/subset_GNPS2chache_to_MS_files.py \
    --input_path "all_dataset_files.csv" \
    --output_path all_unique_mri.tsv
    """
}

process processUniqueDatasets {
    publishDir "./nf_output", mode: 'copy'

    conda "$baseDir/bin_local/conda_env.yml"

    input:
    file 'all_dataset_files.csv'

    output:
    file 'all_datasets.tsv'

    """
    python $baseDir/bin_local/calculate_unique_datasets.py \
    --input_path "all_dataset_files.csv" \
    --output_path all_datasets.tsv
    """
}

workflow {
    // Getting Existing Files
    all_dataset_files_ch = getcachefiles(1)
    all_datasets_ch = processUniqueDatasets(all_dataset_files_ch)

    // Making the unique MRI Files
    processUniqueUSI(all_dataset_files_ch)

    // Getting all the files
    mwbFiles(1)
    mtblsFiles(1)

    // TODO: We should include the GNPS/MassIVE unique files here

    // TODO: Aggregate them together

    // Sometime these files are imported into the database

    
}
