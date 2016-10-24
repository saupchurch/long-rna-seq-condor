#!/usr/bin/python3
"""Master DAG generator.

This is the script for automating generating the mapping, quantification,
and some quality control metrics.
"""
from __future__ import absolute_import

import argparse
from glob import glob
import os
import logging
import pandas

from woldrnaseq import make_star_rsem_dag
from woldrnaseq import models

from .common import (add_default_path_arguments,
                     add_debug_arguments,
                     configure_logging,
                     get_seperator,
                     validate_args)

logger = logging.getLogger(__name__)

def main(cmdline=None):
    parser = make_parser()
    args = parser.parse_args(cmdline)

    configure_logging(args)

    if not validate_args(args):
        parser.error("Please set required parameters")

    sep = get_seperator(args.sep)
    libraries = models.load_library_tables(args.libraries, sep)
    read1 = dict(find_fastqs(libraries, 'read_1'))
    if 'read_2' in libraries.columns:
        read2 = dict(find_fastqs(libraries, 'read_2'))
    else:
        read2 = {}

    dag = generate_star_rsem_analysis(args, libraries, read1, read2)
    print(dag)
    
    return 0

def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sep', choices=['TAB',','], default='TAB')
    parser.add_argument('libraries', nargs='+')
    make_star_rsem_dag.add_default_path_arguments(parser)
    make_star_rsem_dag.add_debug_arguments(parser)
    
    return parser

def find_fastqs(table, fastq_column):
    """Find fastqs for a library from a library table

    fastqs are a comma seperated glob pattern
    """
    if fastq_column in table.columns:
        for library_id in table.index:
            fastqs = find_fastqs_by_glob(
                table.loc[library_id, fastq_column].split(','))
            yield (library_id, list(fastqs))
    else:
        # eventually look up by library ID
        raise NotImplemented("Please specify fastq glob")
        
def find_fastqs_by_glob(fastq_globs):
    for fastq in fastq_globs:
        fastq_list = glob(fastq)
        if len(fastq_list) == 0:
            logger.warn("No fastqs matched: %s", fastq)
        for filename in fastq_list:
            if os.path.exists(filename):
                yield os.path.abspath(filename)
            else:
                logger.warn("Can't find fastq {}. skipping".format(filename))


def get_reference_prefix(libraries, library_id):
    """Get optional reference_prefix from model.

    Defaults to 'chr' if not present
    """
    prefix_name = 'reference_prefix'
    prefix_default = 'chr'
    if prefix_name not in libraries.columns:
        return prefix_default

    prefix = libraries.loc[library_id, prefix_name]
    if pandas.isnull(prefix):
        return prefix_default

    return prefix

def generate_star_rsem_analysis(args, libraries, read_1_fastqs, read_2_fastqs):
    dag = []
    for library_id in libraries.index:
        logger.debug("Creating script for %s", library_id)
        analysis = make_star_rsem_dag.AnalysisDAG()

        analysis.genome_dir = args.genome_dir
        analysis.star_dir = args.star_dir
        analysis.rsem_dir = args.rsem_dir
        analysis.georgi_dir = args.georgi_dir

        analysis.genome = libraries.loc[library_id, 'genome']
        analysis.annotation = libraries.loc[library_id, 'annotation']
        analysis.sex = libraries.loc[library_id, 'sex']
        analysis.job_id = library_id
        analysis.analysis_dir = libraries.loc[library_id, 'analysis_dir']
        analysis.analysis_name = libraries.loc[library_id, 'analysis_name']
        analysis.read_1_fastqs = read_1_fastqs[library_id]
        analysis.read_2_fastqs = read_2_fastqs.get(library_id, [])

        analysis.reference_prefix = get_reference_prefix(libraries, library_id)

        if analysis.is_valid():
            dag.append(str(analysis))
        else:
            raise ValueError("Unable to generate dagman script for {}".format(library_id))

    return os.linesep.join(dag)

if __name__ == '__main__':
    main()
    
