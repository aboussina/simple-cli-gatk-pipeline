# GATKpipe

GATKpipe is a simple command line program based on the GATK best practices workflow that takes a reference genome, up to two FASTQs, and a dbSNP export and outputs a VCF specific to SNP detection.

Pre-Processing Steps:
(based on https://gatk.broadinstitute.org/hc/en-us/articles/360035535912-Data-pre-processing-for-variant-discovery)

<img alt="GATK Graphic for data pre-processing" src="https://i.imgur.com/0o4k4Vu.png" width=20%>

Step | Description | Tool
-----|-------------|-----
1 | BWA MEM alignment is performed with the input reference and FASTQ(s) | BWA MEM
2 | The resulting SAM file is sorted (and compressed) | SortSam
3 | A dummy read group is added to the BAM to allow for use of BaseRecalibrator | AddOrReplaceReadGroups
4 | Duplicates are marked | MarkDuplicates
5 | Base quality scores are recalibrated using known sites (dbSNP) | BaseRecalibrator
6 | Base recalibration parameters are applied | ApplyBQSR
7 | The recalibrated BAM is sorted | SortSam
8 | The sorted BAM is indexed by coordinate | BuildBamIndex

<br/>
<br/>
Variant Discovery:
(based on https://gatk.broadinstitute.org/hc/en-us/articles/360035535932-Germline-short-variant-discovery-SNPs-Indels- and https://gatk.broadinstitute.org/hc/en-us/articles/360035531112--How-to-Filter-variants-either-with-VQSR-or-by-hard-filtering)

<br/>
<br/>

Step | Description | Tool
-----|-------------|-----
1 | Variant calling is performed on the pre-processed BAM | HaplotypeCaller
2 | The resulting VCF is filtered down to SNPs | SelectVariants
3 | The SNP variants are then filtered based on hard-set filter parameters | VariantFiltration

<br/>

# Dependencies
Software:  Python 3, GATK, BWA MEM. <br/>
Inputs: FASTQ(s), indexed reference genome and BWA-indexed reference genome. <br/>
Optional Input: Directory of dbSNP and corresponding index (required for Baseline Recalibration). <br/>
<br/>
For testing, the tiny-test-data repo can be used (https://github.com/roryk/tiny-test-data).  Specifically, git clone this repo and the tiny-test-data repo, add GATKpipe.py and GATK to the path variable and enter the following command into the bash (or cmd) shell from the tiny-test-data directory: 
```bash
python GATKpipe.py -refBWA "genomes/Hsapiens/hg19/bwa/hg19.fa" -r0 "genomes/Hsapiens/hg19/seq/hg19.fa" -r1 "wgs/mt_1.fq.gz" -r2 "wgs/mt_2.fq.gz"
```
