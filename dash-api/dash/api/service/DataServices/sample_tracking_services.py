import logging
import urllib.error
import urllib.request
from collections import defaultdict
from copy import deepcopy
from datetime import datetime

import DataSources.metadata_download
import DataSources.pipeline_status
import DataSources.sample_metadata
import DataSources.sequencing_status
from dateutil.relativedelta import relativedelta

# This key indicates the error status for MLWH requests for sample status information for each institution
# (i.e. the queries made in DataSources.sequencing_status)
# If there is no error, the value will be `None`; on error the value will be a string (the error message).
API_ERROR_KEY = "_ERROR"

# ISO8601 date
FORMAT_DATE = "%Y-%m-%d"
# format of timestamp returned in MLWH queries
FORMAT_MLWH_DATETIME = f"{FORMAT_DATE}T%H:%M:%S%z"


class MonocleSampleTracking:
    """
    Provides wrapper for classes that query various data sources for Monocle data.
    This class exists to convert data between the form in which they are provided by the data sources,
    and whatever form is most convenient for rendering the dashboard.
    """

    sample_table_inst_key = "submitting_institution"
    # these are the sequencing QC flags from MLWH that are checked; if any are false the sample is counted as failed
    # keys are the keys from the JSON the API giuves us;  strings are what we display on the dashboard when the failure occurs.
    sequencing_flags = {
        "qc_lib": "library",
        "qc_seq": "sequencing",
    }

    def __init__(self, set_up=True):
        self.user_record = None
        self.current_project = None
        self.institutions_data = None
        self.institution_names = None
        self.samples_data = None
        self.sequencing_status_data = None
        self.institution_db_key_to_dict = {}  # see get_institutions for the purpose of this
        self.all_institutions_data_irrespective_of_user_membership = None
        # set_up flag causes data objects to be loaded on instantiation
        # only set to False if you know what you're doing
        if set_up:
            self.updated = datetime.now()
            self.sample_metadata = DataSources.sample_metadata.SampleMetadata()
            self.sequencing_status_source = DataSources.sequencing_status.SequencingStatus()

    # date from which progress is counted
    def get_day_zero(self):
        # HARDCODED TODO FIXME
        if self.current_project == "GPS":
            return datetime(2013, 2, 12)  # Earliest sample_creation_datetime
        # Default (JUNO)
        return datetime(2019, 9, 17)

    def get_progress(self):
        institutions_data = self.get_all_institutions_irrespective_of_user_membership()
        total_num_samples_received_by_month = defaultdict(int)
        total_num_lanes_sequenced_by_month = defaultdict(int)
        progress = {
            "date": [],
            "samples received": [],
            "samples sequenced": [],
        }
        # get number of samples received and number of lanes sequenced during each month counted from "day zero"
        for this_institution in institutions_data.keys():
            # samples received
            this_institution_num_samples_received_by_date = self._num_samples_received_by_date(this_institution)
            for this_date_string in this_institution_num_samples_received_by_date.keys():
                this_date = datetime.fromisoformat(this_date_string)
                # days_elapsed   = (this_date - self.get_day_zero()).days
                months_elapsed = ((this_date.year - self.get_day_zero().year) * 12) + (
                    this_date.month - self.get_day_zero().month
                )
                total_num_samples_received_by_month[months_elapsed] += this_institution_num_samples_received_by_date[
                    this_date_string
                ]
            # lanes sequenced
            this_institution_num_lanes_sequenced_by_date = self._num_lanes_sequenced_by_date(this_institution)
            for this_date_string in this_institution_num_lanes_sequenced_by_date.keys():
                this_date = datetime.fromisoformat(this_date_string)
                months_elapsed = ((this_date.year - self.get_day_zero().year) * 12) + (
                    this_date.month - self.get_day_zero().month
                )
                total_num_lanes_sequenced_by_month[months_elapsed] += this_institution_num_lanes_sequenced_by_date[
                    this_date_string
                ]
        # get cumulative numbers received/sequenced for *every* month from 0 to most recent month for which we found something
        num_samples_received_cumulative = 0
        num_lanes_sequenced_cumulative = 0
        project_months_elapsed = ((self.updated.year - self.get_day_zero().year) * 12) + (
            self.updated.month - self.get_day_zero().month
        )
        for this_month_elapsed in range(0, project_months_elapsed + 1, 1):
            if this_month_elapsed in total_num_samples_received_by_month:
                num_samples_received_cumulative += total_num_samples_received_by_month[this_month_elapsed]
            if this_month_elapsed in total_num_lanes_sequenced_by_month:
                num_lanes_sequenced_cumulative += total_num_lanes_sequenced_by_month[this_month_elapsed]
            # progress['date'].append( this_month_elapsed )
            progress["date"].append((self.get_day_zero() + relativedelta(months=this_month_elapsed)).strftime("%b %Y"))
            progress["samples received"].append(num_samples_received_cumulative)
            progress["samples sequenced"].append(num_lanes_sequenced_cumulative)
        return progress

    def get_institutions(self):
        """
        Returns a dict of institutions.

        {  institution_1   => { 'name':     'the institution name',
                                'db_key':   'db key'
                                }
           institution_2...
           }

        If .user_record is defined, it will be used to filter the institutions for those the user belongs to.

        Dict keys are alphanumeric-only and safe for HTML id attr. The monocle db keys are not
        suitable for this as they are full institution names.   It's useful to be able to lookup
        a dict key from a db key (i.e. institution name) so institution_db_key_to_dict()
        is provided.

        ***IMPORTANT / FIXME***
        Institution IDs (`cn`) are now in LDAP, as are their names.
        We need to stop reading institutions from monocledb, and read the names and IDs from LDAP
        The IDs from LDAP will be used as the dict keys in the code in this module, and we can
        then deprecate `institution_name_to_dict_key()`
        *During the transition* the IDs used in LDAP will be the same as the values returned by
        `institution_name_to_dict_key()`

        The data are cached so this can safely be called multiple times without
        repeated monocle db queries being made.
        """
        if self.institutions_data is not None:
            return self.institutions_data

        names = self.get_institution_names()
        institutions = {}
        for this_name in names:
            dict_key = self.institution_name_to_dict_key(this_name, institutions.keys())
            this_db_key = this_name
            institutions[dict_key] = {"name": this_name, "db_key": this_db_key}
            # this allows lookup of the institution dict key from a db key
            self.institution_db_key_to_dict[this_db_key] = dict_key

        self.institutions_data = institutions
        return self.institutions_data

    def get_institution_names(self):
        """
        Return a list of institution names.
        If `user_record` is defined, returns only those institutions that the user is a member of.
        """
        if self.institution_names is not None:
            return self.institution_names

        institution_names = None
        if self.user_record is not None:
            institution_names = [inst["inst_name"] for inst in self.user_record.get("memberOf", [])]
        else:
            institution_names = self.sample_metadata.get_institution_names(self.current_project)

        self.institution_names = institution_names
        return institution_names

    def get_all_institutions_irrespective_of_user_membership(self):
        """
        Returns a dict of  ALL INSTITUTIONS REGARDLESS OF USER MEMBERSHIP.

        In almost every case, you want to call get_institutions() instead -- hence
        the silly name, which is intended to put you off using this without
        figuring out what it is all about.

        If this method is used in the wrong context, then it will bypass the
        authorization that should be required to see institutions' data.

        YOU HAVE BEEN WARNED.  Only use this method if you are REALLY CERTAIN that
        you know what you are doing.

        See the documentation for get_institions for details of the dict that is
        returned.
        """
        if self.all_institutions_data_irrespective_of_user_membership is not None:
            return self.all_institutions_data_irrespective_of_user_membership

        # save .user_record, and temporarily assign None
        temporary_copy_of_user_record = self.user_record
        self.user_record = None
        # get_institutions() will return all institutions when .user_record is None
        self.all_institutions_data_irrespective_of_user_membership = self.get_institutions()
        # CRITICAL:  reset .user_record
        self.user_record = temporary_copy_of_user_record

        return self.all_institutions_data_irrespective_of_user_membership

    def get_samples(self):
        """
        Returns a dict of all samples for each institution in the dict.

        {  institution_1   => [sanger_sample_id_1, sanger_sample_id_2...],
           institution_2...
           }

        All institutions are included in the top level dict, even if they have no
        has no samples in the monocle db; the value will be an empty list.

        Note that samples in the monocle db derive from an inventory of those that are expected;
        they are not necessarily all present in MLWH, so certain samples may not be found
        in the data returned methods that look for sequencing or pipeline status data.  Think
        of the lists returned by this method as being "all samples IDs that you MIGHT be able to
        retrieve data for".

        The data are cached so this can safely be called multiple times without
        repeated monocle db queries being made.
        """
        if self.samples_data is not None:
            return self.samples_data
        if self.institutions_data is None:
            self.institutions_data = self.get_institutions()
        # work on copy of samples dict, as it will be modified in loop below
        all_juno_samples = deepcopy(self.sample_metadata.get_samples(self.current_project))
        samples = {i: [] for i in list(self.institutions_data.keys())}
        for this_sample in all_juno_samples:
            try:
                this_institution_key = self.institution_db_key_to_dict[this_sample[self.sample_table_inst_key]]
                this_sample.pop(self.sample_table_inst_key, None)
                samples[this_institution_key].append(this_sample)
            except KeyError:
                logging.info(
                    "samples excluded because {} is not in current user's institutions list".format(
                        this_sample[self.sample_table_inst_key]
                    )
                )
        self.samples_data = samples
        return self.samples_data

    def get_sequencing_status(self):
        """
        Returns dict with sequencing data for each institution the user is a member of; data are in
        a dict, keyed on the sample ID

        Note that these are sample IDs that were found in MLWH, and have therefore
        been processed at Sanger; some samples that are in the monocle db may not
        be present here.

        {  institution_1: {  sanger_sample_id_1: { seq_data_1 => 'the value',
                                            seq_data_2 => 'the value',
                                            seq_data_3...
                                            },
                             sanger_sample_id_2...
                             },
           institution_2...
           }

        All institutions are included in the top level dict, even if they have no
        has no samples in the monocle db; the sequencing data for these in an empty dict.
        If a sample from the monocle db has no sequencing data available, that sample's
        ID will not appear as a key in the dict of sequencing data for its institution.

        The data are cached so this can safely be called multiple times without
        repeated MLWH queries being made.
        """
        if self.sequencing_status_data is not None:
            return self.sequencing_status_data
        samples_data = self.get_samples()
        institutions_data = self.get_institutions()
        sequencing_status = {}
        for this_institution in institutions_data.keys():
            sequencing_status[this_institution] = {}
            sanger_sample_id_list = [s["sanger_sample_id"] for s in samples_data[this_institution]]
            if len(sanger_sample_id_list) - 1 > 0:  # sanger_sample_id_list must be -1 to discount _ERROR entry
                logging.debug(
                    "{}.get_sequencing_status() requesting sequencing status for samples {}".format(
                        __class__.__name__, sanger_sample_id_list
                    )
                )
                try:
                    sequencing_status[this_institution] = self.sequencing_status_source.get_multiple_samples(
                        sanger_sample_id_list
                    )
                except urllib.error.HTTPError:
                    logging.warning(
                        "{}.get_sequencing_status() failed to collect {} samples for unknown reason".format(
                            __class__.__name__, len(sanger_sample_id_list)
                        )
                    )
                    logging.info(
                        "{}.get_sequencing_status() failed to collect these {} samples: {}".format(
                            __class__.__name__, len(sanger_sample_id_list), sanger_sample_id_list
                        )
                    )
                    sequencing_status[this_institution][
                        API_ERROR_KEY
                    ] = "Server Error: Records cannot be collected at this time. Please try again later."
            if API_ERROR_KEY not in sequencing_status[this_institution]:
                sequencing_status[this_institution][API_ERROR_KEY] = None
        self.sequencing_status_data = sequencing_status
        return self.sequencing_status_data

    def get_batches(self):
        """
        Returns dict with details of batches delivered.

        TODO:  find out a way to get the genuine total number of expected samples for each institution
        """
        samples = self.get_samples()
        institutions_data = self.get_institutions()
        sequencing_status_data = self.get_sequencing_status()
        batches = {i: {} for i in institutions_data.keys()}
        for this_institution in institutions_data.keys():
            # this ought to be the totalnumber of samples expected from an institution during the JUNO project
            # but currently all we know are the number of samples for which we have metadata; this will be
            # a subset of the total expected samples (until the last delivery arrives) so it isn't what we really want
            # but we have no other data yet
            # this is a check to make sure the data for this institution has actually been found
            if sequencing_status_data[this_institution][API_ERROR_KEY] is not None:
                batches[this_institution] = {
                    API_ERROR_KEY: "Server Error: Records cannot be collected at this time. Please try again later."
                }
                continue
            num_samples_expected = len(samples[this_institution])
            # this is a list of the samples actually found in MLWH; it is not necessarily the same as
            # the list of sample IDs in the monocle db
            samples_received = sequencing_status_data[this_institution].keys()
            # this is a dict of the number of samples received on each date; keys are YYYY-MM-DD
            num_samples_received_by_date = self._num_samples_received_by_date(this_institution)
            # work out the number of samples in each delivery
            # assumption: treat all samples received on a given date as single delivery
            #             this is an approximation: one actual batch might have dates that span two (or a few?) days?
            deliveries = []
            delivery_counter = 0
            for this_date in num_samples_received_by_date.keys():
                delivery_counter += 1
                deliveries.append(
                    {
                        "name": "Batch {}".format(delivery_counter),
                        "date": this_date,
                        "number": num_samples_received_by_date[this_date],
                    },
                )
            batches[this_institution] = {
                API_ERROR_KEY: None,
                "expected": num_samples_expected,
                "received": len(samples_received) - 1,
                "deliveries": deliveries,
            }
        return batches

    def sequencing_status_summary(self):
        """
        Returns dict with a summary of sequencing outcomes for each institution.

        {  institution_1: {  'received':    <int>,
                             'completed':   <int>,
                             'success':     <int>,
                             'failed':      <int>,
                             'fail_messages':  [  {  'lane':  lane_id_1,
                                                     'stage': 'name of QC stage where issues was detected',
                                                     'issue': 'string describing the issue'
                                                     },
                                                  ...
                                                  ],
                             },
           institution_2...
           }

        TODO:  improve 'failed' dict 'issue' strings
        """
        sequencing_status_data = self.get_sequencing_status()
        status = {}
        for this_institution in sequencing_status_data.keys():
            logging.debug(
                "{}.sequencing_status_summary() received sample key pairs {} for institution {}".format(
                    __class__.__name__, sequencing_status_data[this_institution].keys(), this_institution
                )
            )
            if sequencing_status_data[this_institution][API_ERROR_KEY] is not None:
                status[this_institution] = {
                    API_ERROR_KEY: "Server Error: Records cannot be collected at this time. Please try again later."
                }
                continue
            sanger_sample_id_list = sequencing_status_data[this_institution].keys()
            status[this_institution] = {
                API_ERROR_KEY: None,
                "received": len(sanger_sample_id_list) - 1,
                "completed": 0,
                "success": 0,
                "failed": 0,
                "fail_messages": [],
            }
            if len(sanger_sample_id_list) - 1 > 0:  # sanger_sample_id_list must be -1 to discount _ERROR entry
                this_sequencing_status_data = sequencing_status_data[this_institution]
                for this_sanger_sample_id in sanger_sample_id_list:
                    if this_sanger_sample_id == API_ERROR_KEY:
                        continue
                    # if a sample is in MLWH but there are no lane data, it means sequencing hasn't been done yet
                    # i.e. only samples with lanes need to be looked at by the lines below
                    for this_lane in this_sequencing_status_data[this_sanger_sample_id]["lanes"]:

                        this_lane_completed, this_lane_success, fail_messages = self.get_sequencing_outcome_for_lane(
                            this_sanger_sample_id, this_lane
                        )
                        if this_lane_completed:
                            status[this_institution]["completed"] += 1
                        if this_lane_success:
                            status[this_institution]["success"] += 1
                        else:
                            status[this_institution]["failed"] += 1
                            status[this_institution]["fail_messages"] += fail_messages
        return status

    def get_sequencing_outcome_for_lane(self, this_sample_id, this_lane):
        """
        Pass a sample ID and a dict representing a lane, as returned by sequencing_status_data()
        Returns tuple with
        - True/False to indicate if a lane completed sequencing
        - True/False to indicate if sequencing succeeded
        - List of dicts describing any failures
          {   'lane':  lane_id_1,
              'stage': 'name of QC stage where issues was detected',
              'issue': 'string describing the issue'
              }
        """
        this_lane_completed = False
        this_lane_success = True
        fail_messages = []

        # According to the annotation in the MLWH iseq_product_metrics table, qc_lib can be 0, 1, or NULL
        # If it is NULL the QC status defaults back to qc_seq, for historic reasons
        if "qc_lib" in this_lane and "qc_seq" in this_lane and this_lane["qc_lib"] is None:
            this_lane["qc_lib"] = this_lane["qc_seq"]

        if (
            "qc complete" == this_lane["run_status"]
            and this_lane["qc_complete_datetime"]
            and 1 == this_lane["qc_started"]
        ):
            # lane has completed, whether success or failure
            this_lane_completed = True
            # look for any failures; note one lane could have more than one failure
            for this_flag in self.sequencing_flags.keys():
                if not 1 == this_lane[this_flag]:
                    this_lane_success = False
                    # record details of this failure
                    fail_messages.append(
                        {
                            "lane": "{} (sample {})".format(this_lane["id"], this_sample_id),
                            "stage": self.sequencing_flags[this_flag],
                            "issue": "sorry, failure messages cannot currently be seen here",
                        }
                    )
        logging.debug(
            "\nsequencing_is_success({},{}) returns {}".format(
                this_sample_id, this_lane, (this_lane_completed, this_lane_success, fail_messages)
            )
        )
        return (this_lane_completed, this_lane_success, fail_messages)

    def project_information(self):
        if self.current_project is None:
            logging.error("project_information: The current project is not set")
            raise ValueError("The current project is not set")
        return self.sample_metadata.get_project_information(self.current_project)

    def pipeline_status_summary(self):
        """
        Returns dict with summary of the pipeline outcomes for each institution.

        {  institution_1: {  'running':      <int>,
                                    'success':      <int>
                                    'failed':        <int>,
                                    'completed':    <int>,
                                    'fail_messages':  [  {  'lane':  lane_id_1,
                                                                    'stage': 'name of QC stage where issues was detected',
                                                                    'issue': 'string describing the issue'
                                                                    },
                                                                ...
                                                                ],
                                    },
            institution_2...
            }

        Note that when `pipeline_status` is instantiated it creates a dataframe with
        the data, rather than querying an API, there is no separate method to "get" pipeline
        data and it isn't cached -- which is a bit dofferent to how institution/samples/sequencing data
        are handled in this class.

        TODO:  decide what to do about about 'failed' dict 'issue' strings
        """
        institutions_data = self.get_institutions()
        sequencing_status_data = self.get_sequencing_status()
        pipeline_status = DataSources.pipeline_status.PipelineStatus(self.current_project)
        status = {}
        for this_institution in institutions_data.keys():
            if sequencing_status_data[this_institution][API_ERROR_KEY] is not None:
                status[this_institution] = {
                    API_ERROR_KEY: "Server Error: Records cannot be collected at this time. Please try again later."
                }
                continue
            status[this_institution] = {
                API_ERROR_KEY: None,
                "running": 0,
                "completed": 0,
                "success": 0,
                "failed": 0,
                "fail_messages": [],
            }
            sanger_sample_id_list = sequencing_status_data[this_institution].keys()
            for this_sanger_sample_id in sanger_sample_id_list:
                if this_sanger_sample_id == API_ERROR_KEY:
                    continue
                this_sample_lanes = sequencing_status_data[this_institution][this_sanger_sample_id]["lanes"]
                for this_lane_id in [lane["id"] for lane in this_sample_lanes]:
                    this_pipeline_status = pipeline_status.lane_status(this_lane_id)
                    # if the lane failed, increment failed and completed counter
                    if this_pipeline_status["FAILED"]:
                        status[this_institution]["failed"] += 1
                        status[this_institution]["completed"] += 1
                        # check each stage of the pipeline...
                        for this_stage in pipeline_status.pipeline_stage_fields:
                            # ...and if the stage failed...
                            if this_pipeline_status[this_stage] == pipeline_status.stage_failed_string:
                                # ...record a message for the failed stage
                                status[this_institution]["fail_messages"].append(
                                    {
                                        "lane": "{} (sample {})".format(this_lane_id, this_sanger_sample_id),
                                        "stage": this_stage,
                                        # currently have no way to retrieve a failure report
                                        "issue": "sorry, failure messages cannot currently be seen here",
                                    },
                                )
                    # if not failed, but succeded, increment success and completed counter
                    elif this_pipeline_status["SUCCESS"]:
                        status[this_institution]["success"] += 1
                        status[this_institution]["completed"] += 1
                    # if neither succeeded nor failed, must still be running
                    else:
                        status[this_institution]["running"] += 1
        return status

    def institution_name_to_dict_key(self, name, existing_keys):
        """
        Private method that creates a shortened, all-alphanumeric version of the institution name
        that can be used as a dict key and also as an HTML id attr
        """
        key = ""
        for word in name.split():
            if word[0].isupper():
                key += word[0:3]
            if 12 < len(key):
                break
        # almost certain to be unique, but...
        while key in existing_keys:
            key += "_X"
        return key

    def convert_mlwh_datetime_stamp_to_date_stamp(self, datetime_stamp):
        return datetime.strptime(datetime_stamp, FORMAT_MLWH_DATETIME).strftime(FORMAT_DATE)

    def _num_samples_received_by_date(self, institution):
        sequencing_status_data = self.get_sequencing_status()
        samples_received = sequencing_status_data[institution].keys()
        if sequencing_status_data[institution][API_ERROR_KEY] is not None:
            return {}
        num_samples_received_by_date = defaultdict(int)
        for this_sanger_sample_id in samples_received:
            if this_sanger_sample_id == API_ERROR_KEY:
                continue
            received_date = self.convert_mlwh_datetime_stamp_to_date_stamp(
                sequencing_status_data[institution][this_sanger_sample_id]["creation_datetime"]
            )
            num_samples_received_by_date[received_date] += 1
        return num_samples_received_by_date

    def _num_lanes_sequenced_by_date(self, institution):
        sequencing_status_data = self.get_sequencing_status()
        if sequencing_status_data[institution][API_ERROR_KEY] is not None:
            return {}
        samples_received = sequencing_status_data[institution].keys()
        num_lanes_sequenced_by_date = defaultdict(int)

        for this_sanger_sample_id in samples_received:
            if this_sanger_sample_id == API_ERROR_KEY:
                continue
            # get each lane (some samples may have non lanes yet)
            for this_lane in sequencing_status_data[institution][this_sanger_sample_id]["lanes"]:
                # get timestamp for completion (some lanes may not have one yet)
                if "complete_datetime" in this_lane:
                    this_lane["complete_datetime"]
                    sequenced_date = self.convert_mlwh_datetime_stamp_to_date_stamp(this_lane["complete_datetime"])
                    num_lanes_sequenced_by_date[sequenced_date] += 1
        return num_lanes_sequenced_by_date
