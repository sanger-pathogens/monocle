import io
import os
import tarfile
from django.conf import settings


def get_renamings(lane_id):
    read1 = lane_id + "_1.fastq.gz"
    read2 = lane_id + "_2.fastq.gz"
    annotation = "spades_assembly/annotation/" + lane_id + ".gff"
    return {
        read1: read1,
        read2: read2,
        "spades_assembly/contigs.fa": "spades_contigs.fa",
        annotation: "spades_annotation.gff",
    }


def make_tarfile(lane_id):
    if settings.USE_MOCK_LANE_DATA:
        mock_lane_id = "31663_7#113"
        lane_dir = os.path.abspath(
            os.path.join(settings.DATA_DIR, mock_lane_id)
        )
        filenames = get_renamings(mock_lane_id)
    else:
        lane_dir = os.path.abspath(os.path.join(settings.DATA_DIR, lane_id))
        filenames = get_renamings(lane_id)

    out_file = io.BytesIO()
    with tarfile.open(fileobj=out_file, mode="w|gz") as tar:
        for file in filenames:
            file_path = lane_dir + "/" + file
            tar.add(file_path, arcname=filenames[file])
    return out_file
