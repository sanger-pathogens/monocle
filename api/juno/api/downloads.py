import tarfile, io, os
from django.conf import settings

# TODO: replace fixed mock file with actual file for lane
DATA_DIR = os.path.join(
    os.path.join(getattr(settings, "BASE_DIR", None), os.pardir),
    "mock-data/" + "31663_7#113",
)


def make_tarfile(lane_id):
    lane_dir = os.path.abspath(DATA_DIR)
    # TODO: change this list to take in lane id
    filenames = {
        "31663_7#113_1.fastq.gz": "31663_7#113_1.fastq.gz",
        "31663_7#113_2.fastq.gz": "31663_7#113_2.fastq.gz",
        "spades_assembly/contigs.fa": "spades_contigs.fa",
        "spades_assembly/annotation/31663_7#113.gff": "spades_annotation.gff",
    }
    out_file = io.BytesIO()
    with tarfile.open(fileobj=out_file, mode="w:gz") as tar:
        for file in filenames:
            file_path = lane_dir + "/" + file
            tar.add(file_path, arcname=filenames[file])
    return out_file
