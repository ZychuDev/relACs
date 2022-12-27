from typing_extensions import Protocol
from pandas import DataFrame # type: ignore

class ExtenralHeadingsSettingsReader(Protocol):
    def get_external_headings(self) -> dict[str, str]:
        """Return headings for ... used in Magnetometer."""

class DataReader:
    def __init__(self, setting_reader: ExtenralHeadingsSettingsReader ):
        external_headings: dict[str, str] = setting_reader.get_external_headings()
        print("External", external_headings)
    
    def get_raw_dataframe(self) -> DataFrame:
        pd: DataFrame = DataFrame(columns=["Temperature", "MagneticField",  "Frequency", "ChiPrime", "ChiBis"])
        return pd



    