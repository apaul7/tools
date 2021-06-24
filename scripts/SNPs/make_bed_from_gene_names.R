# This script helps simplify the process of pulling out variants in 
# candidate genes. Input is a list of genes, output is a bed file. 
# Starts by querying biomart for start/stop of genes based on gene name,
# adds padding, then generates a bed file to be used on the raw vcf. 

# alex.paul@wustl.edu
# v1.0

biomart_gene_start_stop <- function(genes){
  start_length <- length(unique(genes))
  ensembl <- biomaRt::useMart("ensembl", "hsapiens_gene_ensembl")
  results <- biomaRt::getBM(attributes = c("external_gene_name",
                                           "chromosome_name",
                                           "transcript_start", 
                                           "transcript_end",
                                           "ensembl_transcript_id_version"),
                            filters = "external_gene_name",
                            values = genes,
                            mart = ensembl)
  result_genes = unique(results$external_gene_name)
  if(length(result_genes) != start_length) {
    warning("Not all query genes had a return value")
  }
  results
}

gene_names <- c("VCP", "HNRNPA2B1", "HNRNPA1","SQSTM1", "MATR3",
                "ANXA11", "TIA1", "HNRNPDL", "ANO5", "SMPX", "DNAJB6","TNPO3")
results <- biomart_gene_start_stop(gene_names)

padding_length <- 5000


#results.bak <- results
results <- results.bak

# remove non 1-22,x,y chromosomes
# sort
# add "chr"
# add padding
valid_chr = c(1:22, "X","Y")
results <- results[results$chromosome_name %in% valid_chr,]
results$chromosome_name <- factor(as.character(results$chromosome_name),levels = valid_chr)
results <- results[order(results$chromosome_name, results$transcript_start, results$transcript_end),]
results$chromosome_name <- paste0("chr", results$chromosome_name)
results$transcript_start <- results$transcript_start  + padding_length
results$transcript_end <- results$transcript_end  + padding_length

# format for bed file
# chrom,start,end,name (with tabs not commas)
bed <- results[,c("chromosome_name","transcript_start", "transcript_end","ensembl_transcript_id_version")]
readr::write_tsv(bed, "~/tmp/test.bed", col_names = FALSE)

