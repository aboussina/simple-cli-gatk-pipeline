#!/usr/bin/python3
# GATK Python Pipeline
import sys
import argparse
import subprocess
import tempfile
import os
__author__ = "Aaron Boussina"

def main():
    """ Parses args, then ... """
    args = parse_args()

    # Ensure Python 3 is Being Used
    if sys.version_info.major < 3:
        print("Python3 is Required to run this Pipeline.  Ending Program.")
        sys.exit();
    
        
    # Account for Different Handling of File Paths depending on OS
    if os.name != 'posix':
        args.refBWA = '"'+ args.refBWA + '"'
        args.r1 = '"'+ args.r1 + '"'      
        args.r0 = '"'+ args.r0 + '"'

        if str(args.r2 or ''):
            args.r2 = '"'+ args.r2 + '"'

        if str(args.dbSNP or ''):
            args.dbSNP = '"'+ args.dbSNP + '"'
    

    # Create a temporary directory to handle outputs
    # Define Output Files
    cd = os.getcwd()
    td = tempfile.mkdtemp()
    bwa = os.path.join(td, 'bwa.sam')
    sortSam = os.path.join(td, 'SortSam.bam')
    sortSamG = os.path.join(td, 'SsamG.bam')
    mdup = os.path.join(td, 'MarkDuplicates.bam')
    mdupM = os.path.join(td, 'MarkDuplicatesM.bam')
    BR = os.path.join(td, 'BR.table')
    BQSR = os.path.join(td, 'BQSR.bam')
    BQSRS = os.path.join(td, 'BQSRS.bam')
    HC = os.path.join(td, 'HC.vcf.gz')
    HCg = os.path.join(cd, 'HCg.vcf.gz')
    HCsnp = os.path.join(td, 'HCsnp.vcf.gz')

    # Output the Final VCF to the Current Directory
    vcSNP = os.path.join(cd, 'vcSNP.vcf.gz')

    # Perform BWA MEM Alignment.  Use both reads if provided, else just use the first.
    if str(args.r2 or ''):
        cmd = "bwa mem " + args.refBWA  + ' ' +  args.r1  + ' ' + args.r2
    else:
        cmd = "bwa mem " + args.refBWA  + ' ' + args.r1
    
    try:
        sam = subprocess.run(cmd, stdout=subprocess.PIPE, check=True, shell=True, text=True)
    except:
        print("Failure in BWA MEM.  Ending Program.")
        sys.exit()

   
    # Output BWA MEM SAM file
    open(bwa, 'w').write(sam.stdout)
    
    # Run SortSam 
    cmd = "gatk SortSam -I " + bwa + " -O " + sortSam + " -SO queryname"
    try:
        subprocess.run(cmd, shell=True, check=True)
    except:
        print("Failure in SortSam.  Ending Program.")
        sys.exit()

    
    # Add Read Group - Dummy values to satisfy BaseRecalibrator
    cmd = "gatk AddOrReplaceReadGroups -I " + sortSam + ' -O ' + sortSamG + ' -LB "LIB" -PL "illumina" -PU "A" -SM "A"'
    try: 
        subprocess.run(cmd, shell=True, text=True, check=True)
    except:
        print("Failure in AddOrReplaceGroups.  Ending Program.")
        sys.exit()
    
    
  
    # Run MarkDuplicates
    cmd = "gatk MarkDuplicates -I " + sortSamG + " -O " + mdup + " -M " + mdupM
    try:
        subprocess.run(cmd, shell=True, check=True)
    except:
        print("Failure in MarkDuplicates.  Ending Program.")
        sys.exit()
     

    # Perform base quality score recalibration
    if (args.dbSNP or ''):
        cmd = "gatk BaseRecalibrator -I " + mdup + " -O " + BR + " -R " + args.r0 + " -known-sites " + args.dbSNP  
        dbS = "-D " + args.dbSNP
        try:  

            subprocess.run(cmd, shell=True, text=True, check=True)

        except:
            print("Failure in Base Recalibrator.  Ending Program.")
            sys.exit()
   

        cmd = "gatk ApplyBQSR -I " + mdup + " -bqsr " + BR + " -O " + BQSR
        try:   
            subprocess.run(cmd, shell = True, check=True) 
        except:
            print(cmd)
            print("Failure in Applying Base Quality Score Recalibration.  Ending Program.")
            sys.exit()

    else:
        BQSR = mdup
        dbS = ""

    
    # Sort the Recalibrated BAM
    cmd = "gatk SortSam -I " + BQSR + " -O " + BQSRS + " -SO coordinate"
    try:
        subprocess.run(cmd, shell=True, check=True)
    except:
        print("Failure in SortSam.  Ending Program.")
        sys.exit()
    
    # Perform BAM Index
    cmd = "gatk BuildBamIndex -I " + BQSRS
    try:   
        subprocess.run(cmd, shell = True, check=True) 
    except:
        print("Failure in Indexing BAM.  Ending Program.")
        sys.exit()
        
    # Perform HaplotypeCaller for Variant Calling
    cmd = "gatk HaplotypeCaller -I " + BQSRS + " -O " + HC + " -R " + args.r0 + ' -ERC GVCF' + " -G StandardAnnotation -G AS_StandardAnnotation -G StandardHCAnnotation " + dbS
    try:   
        subprocess.run(cmd, shell = True, check=True) 
    except:
        print("Failure in HaplotypeCaller.  Ending Program.")
        sys.exit()

    # Perform Genotyping
    cmd = "gatk GenotypeGVCFs -V " + HC + " -O " + HCg + " -R " + args.r0 
    try:   
        subprocess.run(cmd, shell = True, check=True) 
    except:
        print("Failure in Genotyping GVCF.  Ending Program.")
        sys.exit()
      
    # Subset to SNPs
    cmd = "gatk SelectVariants -V " + HCg + " -select-type SNP" + " -O " + HCsnp 
    try:   
        subprocess.run(cmd, shell = True, check=True) 
    except:
        print("Failure in SelectVariants.  Ending Program.")
        sys.exit()

    
    # Perform VariantFiltration to Filter False Positives

    cmd = 'gatk VariantFiltration -V ' +  HCsnp + ' -filter "QD < 2.0" --filter-name "QD2" -filter "QUAL < 30.0" --filter-name "QUAL30" \
            -filter "SOR > 3.0" --filter-name "SOR3" -filter "FS > 60.0" --filter-name "FS60" -filter "MQ < 40.0" --filter-name "MQ40" \
            -filter "MQRankSum < -12.5" --filter-name "MQRankSum-12.5" -filter "ReadPosRankSum < -8.0" --filter-name "ReadPosRankSum-8" ' + '-O ' + vcSNP
    
    try:   
        subprocess.run(cmd, shell = True, check=True) 
    except:
        print("Failure in VariantFiltration.  Ending Program.")
        sys.exit()



        
def parse_args():
    """ Standard argument parsing """
    parser = argparse.ArgumentParser(description='PAD-G GATK Pipe:  This program outputs a VCF for SNP detection from a given reference (FASTA), read(s) (FASTQs), and dbSNP export.'
         + ' Specifically, it performs BWA MEM, marks the duplicate for removal, recalibrates the base quality scores, performs Haplotype Calling,'
         + 'and filters the resulting variants.  Software Dependecies:  BWA MEM, GATK, and Python3')
    
    parser.add_argument('-r1', '--r1' , type=str, required=True, help='FASTQ File 1')

    parser.add_argument('-r2', '--r2', type=str, help='FASTQ File 2')

    parser.add_argument('-refBWA', '--refBWA', type=str,
                    required=True, help='BWA Reference Genome Files')

    parser.add_argument('-r0', '--r0', type=str,
                required=True, help='Reference Genome (index must be present in directory)')

    parser.add_argument('-dbSNP', '--dbSNP', type=str,
             help='dbSNP of Known Polymorphic Sites (index must be present in directory).  Required for Baseline Recalibration.')
    

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())