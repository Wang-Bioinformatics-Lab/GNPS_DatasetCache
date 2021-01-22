#!/usr/bin/env nextflow
 
params.files = "$baseDir/test_data/*.mzML"

Channel
    .fromPath( params.files )
    .ifEmpty { error "Cannot find any reads matching: ${params.files}" }
    .set { files_ch }

process get_information {
    publishDir "$baseDir/nf_output/summary", mode: 'copy'
    //errorStrategy 'ignore'
      
    input:
    file(filename) from files_ch
  
    output:
    file("*.json") into contigs_ch
  
    """
    echo ${filename}
    python $baseDir/bin/calculate_stats.py ${filename} ${filename}.json
    """

}
