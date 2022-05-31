from dataclasses import dataclass


@dataclass
class QCData:
    # This is a minimal initial implementation, we expect to add many more QC values
    lane_id: str
    rel_abun_sa: float
