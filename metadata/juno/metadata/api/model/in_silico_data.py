from dataclasses import dataclass


@dataclass
class InSilicoData:
    # This is likely to change as the GBS typer pipeline's main output report gets modified
    lane_id: str
    cps_type: str
    ST: str
    adhP: int
    pheS: int
    atr: int
    glnA: int
    sdhA: int
    glcK: int
    tkt: int
    twenty_three_S1: str
    twenty_three_S3: str
    CAT: str
    ERMB: str
    ERMT: str
    FOSA: str
    GYRA: str
    LNUB: str
    LSAC: str
    MEFA: str
    MPHC: str
    MRSA: str
    MSRD: str
    PARC: str
    RPOBGBS_1: str
    RPOBGBS_2: str
    RPOBGBS_3: str
    RPOBGBS_4: str
    SUL2: str
    TETB: str
    TETL: str
    TETM: str
    TETO: str
    TETS: str
    ALP1: str
    ALP23: str
    ALPHA: str
    HVGA: str
    PI1: str
    PI2A1: str
    PI2A2: str
    PI2B: str
    RIB: str
    SRR1: str
    SRR2: str
    GYRA_variant: str
    PARC_variant: str
