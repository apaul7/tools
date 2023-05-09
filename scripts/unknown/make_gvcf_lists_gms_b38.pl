#!/usr/bin/perl

use strict;

# input will be a file with paths to the results directory of the cwl runs to do joint analysis on


my $cwl_paths=$ARGV[0];
open(FILE, $cwl_paths);
my @ids=<FILE>;
close FILE;


#If gvcf.chr.list files all ready exist, delete them so as not to append to them
for(my $i=1; $i<25; ++$i) {
    my $j=$i;
    if($i==23) {$j='X';}
    elsif($i==24) {$j='Y';}
    my $file='gvcf.c'.$j.'.list';
    system("rm -r -f $file");
}


for my $id (@ids) {
  chomp $id;

  my $dir=`pwd`;
  chomp $dir;
  for(my $i=1; $i<25; ++$i) {
    my $j=$i;
    if($i==23) {$j='X';}
    elsif($i==24) {$j='Y';}
    my $chr_file='gvcf.c'.$j.'.list';
    open(CHR_FILE, '>>', $chr_file);
    print CHR_FILE "${id}/chr${j}.g.vcf.gz\n";
  }
}
exit;
