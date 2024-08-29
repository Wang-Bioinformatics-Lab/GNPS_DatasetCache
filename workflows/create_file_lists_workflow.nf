#!/usr/bin/env nextflow
nextflow.enable.dsl=2

params.mtblstoken = ""

TOOL_FOLDER = "$baseDir/bin"

process mwbFiles {
    errorStrategy 'ignore'

    publishDir "./nf_output", mode: 'copy'

    conda "$TOOL_FOLDER/conda_env.yml"

    input:
    val x
    file existing_datasets

    output:
    file 'MWBFilePaths_ALL.tsv'

    """
    python $TOOL_FOLDER/getAllWorkbench_file_paths.py \
    --study_id ALL \
    --output_path MWBFilePaths_ALL.tsv \
    --existing_datasets $existing_datasets
    """
}

process mtblsFiles {
    errorStrategy 'ignore'

    publishDir "./nf_output", mode: 'copy'

    conda "$TOOL_FOLDER/conda_env.yml"

    input:
    val x
    file existing_datasets

    output:
    file 'MetabolightsFilePaths_ALL.tsv'

    """
    python $TOOL_FOLDER/getAllMetabolights_file_paths.py \
    --output_filename "MetabolightsFilePaths_ALL.tsv" \
    --user_token $params.mtblstoken \
    --existing_datasets $existing_datasets
    """
}

process gnpsFiles {
    errorStrategy 'ignore'

    publishDir "./nf_output", mode: 'copy'

    conda "$baseDir/bin_local/conda_env.yml"

    input:
    val x
    file existing_datasets

    output:
    file 'GNPSFilePaths_ALL.tsv'

    """
    python $baseDir/bin_local/getAllGNPS_file_paths.py \
    --output_path "GNPSFilePaths_ALL.tsv" \
    --existing_datasets $existing_datasets \
    --completeness newsubset
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
    #wget 'https://datasetcache.gnps2.org/datasette/database/filename.csv?_stream=on&_size=max' -O all_dataset_files.csv
    python $baseDir/bin_local/get_current_cache_files.py \
    all_dataset_files.csv
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

process getUniqueDatasets {
    publishDir "./nf_output", mode: 'copy'

    conda "$baseDir/bin_local/conda_env.yml"

    input:
    file input_all_files

    output:
    file 'all_datasets.tsv'

    """
    python $baseDir/bin_local/calculate_unique_datasets.py \
    --input_path $input_all_files \
    --output_path all_datasets.tsv
    """
}

process removeRedundantMRI {
    publishDir "./nf_output", mode: 'copy'

    conda "$baseDir/bin_local/conda_env.yml"

    input:
    file 'all_unique_mri.tsv'

    output:
    file 'all_nonredundant_mri.tsv'
    file 'all_redundantremoved_mri.tsv'

    """
    python $baseDir/bin_local/calculate_filtered_nonredundant_mri.py \
    all_unique_mri.tsv \
    all_nonredundant_mri.tsv \
    all_redundantremoved_mri.tsv
    """
}

process createDownloadMRI {
    publishDir "./nf_output", mode: 'copy'

    conda "$baseDir/bin_local/conda_env.yml"

    input:
    file 'all_nonredundant_mri.tsv'
    file 'all_mri.csv'

    output:
    file 'download_mri.tsv'
    file 'download_thermoraw_mri.tsv'

    """
    python $baseDir/bin_local/create_download_mri.py \
    all_nonredundant_mri.tsv \
    all_mri.csv \
    download_mri.tsv \
    download_thermoraw_mri.tsv
    """
}

workflow {
    // Getting Existing Files
    // all_dataset_files_ch = getcachefiles(1)
    all_dataset_files_ch = file("all_dataset_files.csv") // For Easy Debugging
    
    // Getting unique datasets
    all_datasets_ch = getUniqueDatasets(all_dataset_files_ch)

    // Making the unique MRI Files
    unique_mri = processUniqueUSI(all_dataset_files_ch)

    // Removing Redundant MRI
    (nonredundant_mri, _) = removeRedundantMRI(unique_mri)

    // Creating the download file
    createDownloadMRI(nonredundant_mri, all_dataset_files_ch)

    // Getting all the files that can be used by webapp to update the database
    mwbFiles(1, all_datasets_ch)
    mtblsFiles(1, all_datasets_ch)
    gnpsFiles(1, all_datasets_ch)
    
}
