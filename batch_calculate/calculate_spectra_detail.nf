#!/usr/bin/env nextflow
 
params.files = "$baseDir/test_data/**/*.mzML"

Channel
    .fromPath( params.files )
    .ifEmpty { error "Cannot find any reads matching: ${params.files}" }
    .map { spectrumFile -> tuple("$spectrumFile", spectrumFile) }
    .set { files_ch }

process get_information {
    publishDir "$baseDir/nf_output/summary", mode: 'copy'
    errorStrategy 'ignore'
    //echo true

    maxForks 20

    input:
    set fullPath, file(filename) from files_ch
  
    output:
    file("*.json")
    file("*.png")
    file("*.tsv")
  
    """
    python $baseDir/bin/calculate_stats.py "${fullPath}" ${filename} $baseDir/bin/msaccess
    """

}
