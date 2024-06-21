---
title: "Report for BSUP-{{TICKET}}"
author: [{{AUTHOR}}]
date: "{{DATE}}"
keywords: [report]
titlepage: true,
titlepage-text-color: "FFFFFF"
titlepage-rule-color: "360049"
titlepage-rule-height: 0
titlepage-background: "assets/titlepageFig.pdf"
page-background: "assets/letterheadFig.pdf"
page-background-opacity: "1"
book: true
classoption: [oneside]
fontsize: 11pt
papersize: a4 
geometry:
- top=35mm
- bottom=30mm
- left=15mm
- right=15mm
- heightrounded
...
<!-- pandoc -V fontsize=12pt -V geometry:margin=1in -\-template eisvogel -\-listings -->

[[intro]]

\newpage 

# Ticket

Number   | {{issue_key}}
---------|-------
Summary  | {{summary}}
Reporter | {{reporter}}
Created  | {{created}}

{{desc}}

\newpage 

# Bioinformatics processing

## Data download

Raw dataset was downloaded on 2024-06-03 using a VM, and stored in a temporary location for QC

## Preliminary QC

**fastp 0.20** and **kraken 2.1.0** (using the `k2_nt_20230502` database) have been used to:

- Profile the overall quality of the input reads
- Ensure the integrity of the paired-end files, if present in the dataset
- Check the compatibility of the received sample with the sample type
  
> The output files are stored in the `BSUP-1955-RNA-Seq/qc` directory

## RNA-Seq mapping and quantification

The reads have been mapped against the reference genome (*Mus musculus*, Ensembl GRCm38) using the **nf-core/rnaseq** pipeline.

[nf-core](https://nf-co.re) provides a set of standard pipeline and can be cited as follow:

> Ewels PA, Peltzer A, Fillinger S, *et* *al*. 
> The nf-core framework for community-curated bioinformatics pipelines. *Nature Biotechnology*. 2020 10.1038/s41587-020-0439-x. 

**nf-core/rnaseq** is a bioinformatics pipeline that can be used to analyse RNA sequencing data obtained from organisms with a reference genome and annotation. It takes a samplesheet and FASTQ files as input, performs quality control (QC), trimming and (pseudo-)alignment, and produces a gene expression matrix and extensive QC report.
  
![RNA-Seq workflow map](assets/nf-core-rnaseq.png)

We ran the workflow on the [QIB Cloud](https://cloud.quadram.ac.uk) using Nextflow 23.10.1, and singularity containers.

<!--hide
```bash
nextflow run nf-core/rnaseq \
  --input list.csv --outdir rnaseq-mapping \
  -profile singularity -r 3.12.0 \
  --fasta Mus_musculus/Ensembl/GRCm38/Sequence/WholeGenomeFasta/genome.fa \
  --gtf Mus_musculus/Ensembl/GRCm38/Annotation/Genes/genes.gtf \
  -work-dir /volume/tmp-rna/BSUP-1955
```
-->

### Output files

The output files are stored in the `BSUP-1955-RNA-Seq/rnaseq-mapping` directory.

In particular you will find:

* A comprehensive report inside the `multiqc` folder.
* All the individual mappings in `mapping`.
* The quantification of transcripts per sample in `quantification`: the folder contains table with the expression levels of each gene in each sample (e.g. *salmon.merged.gene_counts_scaled.tsv* or *salmon.merged.gene_tpm.tsv* for the TPM (transcripts per million) values).

### Versions

| Tool                       | Version                      |
|----------------------------|------------------------------|
| bedtools                   | 2.30.0                       |
| python                     | 3.11.0                       |
| yaml                       | 6.0                          |
| getchromsizes              | 1.16.1                       |
| bioconductor-deseq2        | 1.28.0                       |
| r-base                     | 4.0.3                        |
| bioconductor-dupradar      | 1.28.0                       |
| r-base                     | 4.2.1                        |
| fastqc                     | 0.11.9                       |
| fq                         | 0.9.1 (2022-02-22)           |
| perl                       | 5.26.2                       |
| python                     | 3.9.5                        |
| rsem                       | 1.3.1                        |
| star                       | 2.7.10a                      |
| picard                     | 3.0.0                        |
| qualimap                   | 2.2.2-dev                    |
| rseqc                      | 3.0.1                        |
| salmon                     | 1.10.1                       |
| bioconductor-summarizedexperiment | 1.24.0                |
| r-base                     | 4.1.1                        |
| bioconductor-tximeta       | 1.12.0                       |
| samtools                   | 1.17                         |
| gawk                       | 5.1.0                        |
| star                       | 2.6.1d                       |
| stringtie                  | 2.2.1                        |
| subread                    | 2.0.1                        |
| cutadapt                   | 3.4                          |
| trimgalore                 | 0.6.7                        |
| ucsc                       | 377                          |


## Differential expression analysis

The output of `nf-core/rnaseq` was then passed to `differentialabundance`,  a bioinformatics pipeline that can be used to analyse data represented as matrices, comparing groups of observations to generate differential statistics and downstream analyses. The pipeline supports RNA-seq data such as that generated by the nf-core rnaseq workflow.

![Differential abundance workflow map](assets/nf-core-rnaseq.png)

<!--hide
```bash
nextflow run nf-core/differentialabundance \
 -r 1.5.0 -profile rnaseq,docker \
 --input demo.csv --matrix demo_counts.tsv \
 --contrasts  contrast_demo.csv \
 -work-dir /volume/tmp-rna/BSUP-1955/ \
  --gtf Mus_musculus/Ensembl/GRCm38/Annotation/Genes/genes.gtf\
  --outdir rnaseq-diffexp -with-tower
```
-->
### Output files

The output directory contains these subdirectories:

* `plots`, contains various graphical output files related to exploratory analysis, quality control, and differential expression, including multiple PNG images such as PCA plots, boxplots, and volcano plots, organized into subfolders by their specific type and condition
* `tables`, contains various tab-separated value (TSV) files with processed abundance data, gene annotations, and differential expression results, organized into subfolders for processed abundance, annotation, and differential analysis.
* `report` the final report of the DE analysis, in HTML format.
  
### Versions

| Tool                                   | Version      |
|----------------------------------------|--------------|
| r-base                                 | 4.1.3        |
| bioconductor-deseq2                    | 1.34.0       |
| atlas-gene-annotation-manipulation     | 1.1.1        |
| r-base                                 | 4.3.3        |
| r-shinyngs                             | 1.8.8        |

## Output files

> We recommend to check the presence of all the expected samples and output files.

Output files have been placed in the `BSUP-1955-RNA-Seq` directory in the Robinson lab shared folder

Windows users will typically access it typing, in a file explorer window:

```
\\qib-hpc-data\research-groups\Stephen-Robinson\BSUP-1955-RNA-Seq
```

From Linux (including the HPC), the path to the same directory is:

```
/qib/research-groups/Stephen-Robinson/BSUP-1955-RNA-Seq
```

### Raw reads

> We recommend checking the output files, including the raw reads. This will help spotting issues before the raw data is required for submission, for example.

The raw reads (dataset named by the external provider as `40-1009503826`) are stored in IRIDA, under the project 2417.

The project is accessible from the url: [https://irida.quadram.ac.uk/irida/projects/2417](https://irida.quadram.ac.uk/irida/projects/2417)

\newpage 

[[glossary]]