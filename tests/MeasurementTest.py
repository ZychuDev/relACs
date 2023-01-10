from unittest import TestCase
from models import Measurement
from pandas import DataFrame, read_json #type: ignore 
from .Mockups import MockupCollection, MockupSettingsSource

class MeasurementTest(TestCase):
    def setUp(self):
        df: DataFrame = DataFrame({
            "ChiPrime": [1,2,3,4,5],
            "ChiPrimeMol": [1,2,3,4,5],
            "ChiBis": [1,2,3,4,5],
            "ChiBisMol": [1,2,3,4,5],
            "Frequency": [1,2,3,4,5],
            "Omega": [1,2,3,4,5],
            "OmegaLog": [1,2,3,4,5],
            "Frequency": [1,2,3,4,5],
            "FrequencyLog": [1,2,3,4,5],
            "Hidden": [False, False, False, False, False]
        })
        self.m = Measurement("TestMeasuremnt", df, 1.0, 1.0, MockupSettingsSource(), MockupCollection())

        self.emited_name: str | None = None
        self.m.name_changed.connect(self.set_emited_name)

        self.df_changed_emits: int = 0
        self.m.df_changed.connect(self.count_df_changed_emits)

        self.deletion_imposible_emits: int = 0
        self.m.deletion_imposible.connect(self.count_deletion_imposible_emits)

    def tearDown(self):
        self.m.df_changed.disconnect()
        self.m.name_changed.disconnect()
        
    def set_emited_name(self, name: str):
        self.emited_name = name

    def count_df_changed_emits(self):
        self.df_changed_emits = self.df_changed_emits + 1

    def count_deletion_imposible_emits(self):
        self.deletion_imposible_emits = self.deletion_imposible_emits + 1

    def test_set_name(self):
        old_name: str = "TestMeasuremnt"
        new_name: str = "NewMeasurementName"

        self.m.set_name(new_name)
        self.assertEqual(self.m.name, new_name, "Wrong name after change")
        self.assertEqual(self.emited_name, new_name, "Wrong name emitted")

        self.m.undo()
        self.assertEqual(self.m.name, old_name, "Action can not be undone")
        self.m.redo()
        self.assertEqual(self.m.name, new_name, "Action can not be redone")

    def test_hide_point(self):
        self.m.hide_point(1, "ChiPrime")
        self.assertEqual(self.df_changed_emits, 1, "Signal not emitted after point hidence")
        self.assertEqual(self.m._df["Hidden"][0], True, "Point is still visible.") 

        self.m.undo()
        self.assertEqual(self.m._df["Hidden"][0], False, "Action can not be undone")
        self.m.redo()
        self.assertEqual(self.m._df["Hidden"][0], True, "Action can not be redone")

        self.m.hide_point(1, "ChiPrime")
        self.assertEqual(self.m._df["Hidden"][0], False, "Point is still hidden")

    def test_delete_point(self):
        self.m.delete_point(1, "ChiPrime")
        self.assertEqual(self.df_changed_emits, 1, "Signal not emitted after point deletion")
        self.assertEqual(self.m._df.shape[0], 4, "Point was not deleted")
        self.assertEqual(set(self.m._df["ChiPrime"].values.tolist()), set([2, 3, 4, 5]), "Wrong point was deleted")

        self.m.undo()
        self.assertEqual(set(self.m._df["ChiPrime"].values.tolist()), set([1, 2, 3, 4, 5]), "Action can to be undone")
        self.m.redo()
        self.assertEqual(set(self.m._df["ChiPrime"].values.tolist()), set([2, 3, 4, 5]), "Action can to be redone")

        self.m.delete_point(1, "ChiPrime")
        self.m.delete_point(2, "ChiPrime")
        self.m.delete_point(3, "ChiPrime")

        self.assertRaises(IndexError, self.m._delete_point, 4, "ChiPrime")
        self.m.delete_point(4, "ChiPrime")
        self.assertEqual(set(self.m._df["ChiPrime"].values.tolist()), set([4, 5]), "Deletion should not be possible")
        self.assertEqual(self.deletion_imposible_emits, 1, "Signal not emitted after deletionw as stopped")

    def test_get_jsonable(self):
        jsonable:dict = self.m.get_jsonable()
        m2: Measurement = Measurement(jsonable["name"], read_json(jsonable["df"]), jsonable["tmp"], jsonable["field"], MockupSettingsSource, MockupCollection)
        self.assertEqual(self.m._df.to_string(), m2._df.to_string(), "Incorrect DataFrame JSON marshaling")
        self.assertEqual(self.m._name, m2.name, "Incorrect name JSON marshaling")
        self.assertEqual(self.m._tmp, m2._tmp, "Incorrect temperature JSON marshaling")
        self.assertEqual(self.m._field, m2._field, "Incorrect field JSON marshaling")


            


