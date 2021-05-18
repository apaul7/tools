#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import argparse
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument(
    "--samples",
    dest="samples",
    help="comma separated sample names",
    required=True,
    action="store",
)
parser.add_argument(
    "--bams",
    dest="bams",
    help="comma separated paths to bams(order matching input sample names)",
    required=True,
    action="store",
)
parser.add_argument(
    "--output",
    dest="output",
    help="output filename",
    required=False,
    action="store",
    default="igv_session.xml",
)

args = parser.parse_args()
samples = args.samples.split(",")
bam_paths = args.bams.split(",")
output_name = args.output

bams = dict(zip(samples, bam_paths))
# load 'blank' xml
script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
print(script_dir + "/blank.xml")
tree = ET.ElementTree(file=script_dir + "/blank.xml")
root = tree.getroot()
# add resource
resources = root.find("Resources")
for sample in samples:
    print(sample)
    sample_bam = bams[sample]
    f, ext = os.path.splitext(sample_bam)
    if ext == ".cram":
        sample_index = sample_bam + ".crai"
    elif ext == ".bam":
        sample_index = sample_bam + ".bai"
    else:
        sys.exit("Error: sample file, " + sample_bam + ", is not in bam/cram format")
    sample_attributes = {"index": sample_index, "name": sample, "path": sample_bam}
    sample_resource = ET.SubElement(resources, "Resource", attrib=sample_attributes)
    sample_panel = ET.SubElement(root, "Panel", attrib={"name": sample + "_panel"})
    junction_attributes = {
        "attributeKey": sample + " Junctions",
        "clazz": "org.broad.igv.sam.SpliceJunctionTrack",
        "fontSize": "10",
        "height": "10",
        "id": sample_bam + "_junctions",
        "name": sample + " Junctions",
        "visible": "false",
    }
    junction_track = ET.SubElement(sample_panel, "Track", attrib=junction_attributes)
    coverage_attributes = {
        "attributeKey": sample + " Coverage",
        "autoScale": "true",
        "clazz": "org.broad.igv.sam.CoverageTrack",
        "color": "175,175,175",
        "fontSize": "10",
        "id": sample_bam + "_coverage",
        "name": sample + " Coverage",
        "snpThreshold": "0.2",
        "visible": "true",
    }
    coverage_track = ET.SubElement(sample_panel, "Track", attrib=coverage_attributes)
    data_range = ET.SubElement(
        coverage_track,
        "DataRange",
        attrib={
            "baseline": "0.0",
            "drawBaseline": "true",
            "flipAxis": "false",
            "maximum": "60",
            "minimum": "0.0",
            "type": "LINEAR",
        },
    )
    alignment_attributes = {
        "attributeKey": sample,
        "clazz": "org.broad.igv.sam.AlignmentTrack",
        "displayMode": "EXPANDED",
        "fontSize": "10",
        "id": sample_bam,
        "name": sample,
        "visible": "true",
    }
    alignment_track = ET.SubElement(sample_panel, "Track", attrib=alignment_attributes)
    render_options = ET.SubElement(alignment_track, "RenderOptions")
tree.write(output_name)
