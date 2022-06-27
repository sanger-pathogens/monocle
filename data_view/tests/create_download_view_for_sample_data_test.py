from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from bin.create_download_view_for_sample_data import create_download_view_for_sample_data

PROJECT = "juno"
DATA_DIR = "/abs/path/data"
OUTPUT_DIR = "/abs/path/to/output"
INSTITUTION_NAME_TO_ID = {
    "Faculty of Pharmacy, Suez Canal University": "FacPhaSueCanUni",
    "Laboratório Central do Estado do Paraná": "LabCenEstPar",
    "Ministry of Health, Central Laboratories": "MinHeaCenLab",
    "The Chinese University of Hong Kong": "TheChiUniHonKon",
    "Universidade Federal do Rio de Janeiro": "UniFedRioJan",
    "Wellcome Sanger Institute": "WelSanIns",
}
SAMPLE_IDS = ["a", "b", "c", "d", "e"]
PUBLIC_NAMES = list(map(lambda sanger_sample_id: sanger_sample_id * 2, SAMPLE_IDS))
INSTITUTION_WITHOUT_LANES = {
    "name": "Laboratório Central do Estado do Paraná",
    "id": INSTITUTION_NAME_TO_ID["Laboratório Central do Estado do Paraná"],
    "samples": [{"public_name": PUBLIC_NAMES[4], "sanger_sample_id": SAMPLE_IDS[4]}],
}
INSTITUTIONS_WITH_PUBLIC_NAMES = [
    {
        "name": "Ministry of Health, Central Laboratories",
        "id": INSTITUTION_NAME_TO_ID["Ministry of Health, Central Laboratories"],
        "samples": [
            {"public_name": PUBLIC_NAMES[0], "sanger_sample_id": SAMPLE_IDS[0]},
            {"public_name": PUBLIC_NAMES[1], "sanger_sample_id": SAMPLE_IDS[1]},
        ],
    },
    {
        "name": "Wellcome Sanger Institute",
        "id": INSTITUTION_NAME_TO_ID["Wellcome Sanger Institute"],
        "samples": [
            {"public_name": PUBLIC_NAMES[2], "sanger_sample_id": SAMPLE_IDS[2]},
            {"public_name": PUBLIC_NAMES[3], "sanger_sample_id": SAMPLE_IDS[3]},
        ],
    },
    INSTITUTION_WITHOUT_LANES,
]
INSTITUTIONS_WITHOUT_PUBLIC_NAMES = [
    {
        "name": "Universidade Federal do Rio de Janeiro",
        "id": INSTITUTION_NAME_TO_ID["Universidade Federal do Rio de Janeiro"],
        "samples": [],
    }
]
INSTITUTIONS = INSTITUTIONS_WITH_PUBLIC_NAMES + INSTITUTIONS_WITHOUT_PUBLIC_NAMES
LANES = ["x", "y", "z"]
SEQUENCING_STATUS_DATA = {
    SAMPLE_IDS[0]: {SAMPLE_IDS[0]: {"lanes": [{"id": LANES[0]}, {"id": LANES[1]}]}},
    SAMPLE_IDS[1]: {},
    SAMPLE_IDS[2]: {SAMPLE_IDS[2]: {"lanes": [{"id": LANES[2]}]}},
    SAMPLE_IDS[3]: {SAMPLE_IDS[3]: {"lanes": []}},
    SAMPLE_IDS[4]: {SAMPLE_IDS[4]: {"lanes": []}},
}


class CreateDownloadViewForSampleDataTest(TestCase):
    @classmethod
    def setUpClass(cls):
        patch(
            "bin.create_download_view_for_sample_data._get_sequencing_status_data", get_sequencing_status_data
        ).start()
        patch("bin.create_download_view_for_sample_data._cd").start()

    def setUp(self):
        self.db = DB()

        create_symlink_patch = patch("bin.create_download_view_for_sample_data._create_symlink_to")
        self.create_symlink_to = create_symlink_patch.start()
        mkdir_patch = patch("bin.create_download_view_for_sample_data._mkdir")
        self.mkdir = mkdir_patch.start()

    def test_create_folder_per_institute_with_public_name(self):
        create_download_view_for_sample_data(self.db, INSTITUTION_NAME_TO_ID, PROJECT, DATA_DIR, OUTPUT_DIR)

        for institution in INSTITUTIONS_WITH_PUBLIC_NAMES:
            self.mkdir.assert_any_call(institution["id"])
        for institution in INSTITUTIONS_WITHOUT_PUBLIC_NAMES:
            self.assert_mkdir_not_called_with(institution["id"])

    def test_create_public_name_folder_for_each_institute(self):
        create_download_view_for_sample_data(self.db, INSTITUTION_NAME_TO_ID, PROJECT, DATA_DIR, OUTPUT_DIR)

        for public_name in PUBLIC_NAMES:
            self.mkdir.assert_any_call(public_name)

    def test_create_symlink_per_data_file(self):
        data_files = list(map(lambda lane: Path(f"{lane}.vcf"), LANES))
        data_files.append(Path(f"{LANES[0]}.fastq"))
        patch("bin.create_download_view_for_sample_data._get_data_files", return_value=data_files).start()

        create_download_view_for_sample_data(self.db, INSTITUTION_NAME_TO_ID, PROJECT, DATA_DIR, OUTPUT_DIR)

        self.assertEqual(self.create_symlink_to.call_count, len(data_files) * len(LANES))
        for data_file in data_files:
            data_file.resolve()
            self.create_symlink_to.assert_any_call(data_file, data_file.name)

    def assert_mkdir_not_called_with(self, institution_id):
        try:
            self.mkdir.assert_any_call(institution_id)
        except AssertionError:
            return
        raise AssertionError(f'Expected `mkdir` to not have been called w/ "{institution_id}".')


def get_sequencing_status_data(sanger_sample_ids):
    return SEQUENCING_STATUS_DATA[sanger_sample_ids[0]]


class DB:
    def get_institution_names(self, project):
        return map(lambda institution: institution["name"], INSTITUTIONS)

    def get_samples(self, project, institutions):
        if institutions[0] == INSTITUTIONS[0]["name"]:
            return INSTITUTIONS[0]["samples"]
        elif institutions[0] == INSTITUTIONS[1]["name"]:
            return INSTITUTIONS[1]["samples"]
        elif institutions[0] == INSTITUTIONS[2]["name"]:
            return INSTITUTIONS[2]["samples"]
        return []
