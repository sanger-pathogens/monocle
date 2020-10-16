import io
import os
import tarfile
from django.conf import settings


def get_read1_fastq_download_name(lane_id):
    """ The file name that will be downloaded """
    return lane_id + "_1.fastq.gz"


def get_read1_fastq_file_path(lane_id):
    """ The path to the S3 bucket file """
    return os.path.join(os.path.abspath(settings.DATA_DIR), "reads", lane_id + "_1.fastq.gz")


def get_read2_fastq_download_name(lane_id):
    """ The file name that will be downloaded """
    return lane_id + "_2.fastq.gz"


def get_read2_fastq_file_path(lane_id):
    """ The path to the S3 bucket file """
    return os.path.join(os.path.abspath(settings.DATA_DIR), "reads", lane_id + "_2.fastq.gz")


def get_spades_assembly_contigs_download_name(lane_id):
    """ The file name that will be downloaded """
    return lane_id + ".fa"


def get_spades_assembly_contigs_file_path(lane_id):
    """ The path to the S3 bucket file """
    return os.path.join(os.path.abspath(settings.DATA_DIR), "assembly", lane_id + ".contigs_spades.fa")


def get_spades_annotation_gff_download_name(lane_id):
    """ The file name that will be downloaded """
    return lane_id + ".gff"


def get_spades_annotation_gff_file_path(lane_id):
    """ The path to the S3 bucket file """
    return os.path.join(os.path.abspath(settings.DATA_DIR), "annotation", lane_id + ".spades.gff")


def get_renamings(lane_id):

    return {
        get_read1_fastq_file_path(lane_id):               get_read1_fastq_download_name(lane_id),
        get_read2_fastq_file_path(lane_id):               get_read2_fastq_download_name(lane_id),
        get_spades_assembly_contigs_file_path(lane_id):   get_spades_assembly_contigs_download_name(lane_id),
        get_spades_annotation_gff_file_path(lane_id):     get_spades_annotation_gff_download_name(lane_id),
    }


def make_tarfile(lane_id):

    if settings.USE_MOCK_LANE_DATA:
        mock_lane_id = "31663_7#113"
        file_renamings = get_renamings(mock_lane_id)
    else:
        file_renamings = get_renamings(lane_id)

    out_file = io.BytesIO()
    with tarfile.open(fileobj=out_file, mode="w:gz") as tar:
        for file in file_renamings:
            tar.add(file, arcname=file_renamings[file])
    return out_file
