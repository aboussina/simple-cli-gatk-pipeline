# GATKpipe.py

GATKpipe.py is a simple command line program based on the GATK best practices workflow that takes a reference genome, up to two FASTQs, and a dbSNP export and outputs a VCF specific to SNP detection.

Pre-Processing Steps:
(based on https://gatk.broadinstitute.org/hc/en-us/articles/360035535912-Data-pre-processing-for-variant-discovery)

1. BWA MEM alignment is performed with the input reference and FASTQ(s) [BWA MEM]
2. The resulting SAM file is sorted (and compressed) [SortSam]
3. A dummy read group is added to the BAM to allow for use of BaseRecalibrator [AddOrReplaceReadGroups]
4. Duplicates are marked [MarkDuplicates]
5. Base quality scores are recalibrated using known sites (dbSNP) [BaseRecalibrator]
6. Base recalibration parameters are applied [ApplyBQSR]
7. The recalibrated BAM is sorted [SortSam]
8. The sorted BAM is indexed by coordinate [BuildBamIndex]

Variant Discovery:
(based on https://gatk.broadinstitute.org/hc/en-us/articles/360035535932-Germline-short-variant-discovery-SNPs-Indels- and https://gatk.broadinstitute.org/hc/en-us/articles/360035531112--How-to-Filter-variants-either-with-VQSR-or-by-hard-filtering)

1. Variant calling is performed on the pre-processed BAM [HaplotypeCaller]
2. The resulting VCF is filtered down to SNPs [SelectVariants]
3. The SNP variants are then filtered based on hard-set filter parameters [VariantFiltration]

# Dependencies
Software:  Python 3, GATK, BWA MEM
Inputs: FASTQ, reference genome.  For testing, the tiny-test-data repo can be used (https://github.com/roryk/tiny-test-data).
