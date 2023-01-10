from unittest import TestCase
from models import Fit
from pandas import DataFrame, read_json #type: ignore 
from .Mockups import MockupCollection, MockupSettingsSource

class FitTest(TestCase):
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
        self.f = Fit("TestFit", df, 1.0, 1.0, MockupSettingsSource(), MockupCollection())

        self.emited_name: str | None
        self.f.name_changed.connect(self.set_emited_name)

        self.df_changed_emits: int = 0
        self.f.df_changed.connect(self.count_df_changed_emits)

        self.df_point_deleted_emits: int = 0
        self.f.df_point_deleted.connect(self.count_df_point_deleted)

        self.deletion_imposible_emits: int = 0
        self.f.deletion_imposible.connect(self.count_deletion_imposible_emits)

    def tearDown(self):
        self.f.name_changed.disconnect()
        self.f.df_changed.disconnect()
        self.f.df_point_deleted.disconnect()

    def set_emited_name(self, name: str):
        self.emited_name = name

    def count_df_changed_emits(self):
        self.df_changed_emits += 1

    def count_df_point_deleted(self):
        self.df_point_deleted_emits += 1

    def count_deletion_imposible_emits(self):
            self.deletion_imposible_emits += 1

    def test_set_name(self):
        old_name: str = "TestFit"
        new_name: str = "NewMeasurementName"

        self.f.set_name(new_name)
        self.assertEqual(self.f.name, new_name, "Wrong name after change")
        self.assertEqual(self.emited_name, new_name, "Wrong name emitted")

        self.f.undo()
        self.assertEqual(self.f.name, old_name, "Action can not be undone")
        self.f.redo()
        self.assertEqual(self.f.name, new_name, "Action can not be redone")

    def test_hide_point(self):
        self.f.hide_point(1, "ChiPrime")

        self.assertEqual(self.df_changed_emits, 1, "Signal not emitted after point hidence")
        self.assertEqual(self.f._df["Hidden"][0], True, "Point is still visible.") 

        self.f.undo()
        self.assertEqual(self.f._df["Hidden"][0], False, "Action can not be undone")
        self.f.redo()
        self.assertEqual(self.f._df["Hidden"][0], True, "Action can not be redone")

        self.f.hide_point(1, "ChiPrime")
        self.assertEqual(self.f._df["Hidden"][0], False, "Point is still hidden")

    def test_delete_point(self):
        self.f.delete_point(1, "ChiPrime")
        self.assertEqual(self.df_point_deleted_emits, 1, "Signal not emitted after point deletion")
        self.assertEqual(self.f._df.shape[0], 4, "Point was not deleted")
        self.assertEqual(set(self.f._df["ChiPrime"].values.tolist()), set([2, 3, 4, 5]), "Wrong point was deleted")

        self.f.undo()
        self.assertEqual(set(self.f._df["ChiPrime"].values.tolist()), set([1, 2, 3, 4, 5]), "Action can to be undone")
        self.f.redo()
        self.assertEqual(set(self.f._df["ChiPrime"].values.tolist()), set([2, 3, 4, 5]), "Action can to be redone")
        self.f.delete_point(1, "ChiPrime")
        self.f.delete_point(2, "ChiPrime")
        self.f.delete_point(3, "ChiPrime")

        self.assertRaises(IndexError, self.f._delete_point, 4, "ChiPrime")
        self.f.delete_point(4, "ChiPrime")
        self.assertEqual(set(self.f._df["ChiPrime"].values.tolist()), set([4, 5]), "Deletion should not be possible")
        self.assertEqual(self.deletion_imposible_emits, 1, "Signal not emitted after deletionw as stopped")


    def test_get_jsonable(self):
        jsonable:dict = self.f.get_jsonable()
        f2: Fit = Fit(jsonable["name"], read_json(jsonable["df"]), jsonable["tmp"], jsonable["field"], MockupSettingsSource, MockupCollection)
        self.assertEqual(self.f._df.to_string(), f2._df.to_string(), "Incorrect DataFrame JSON marshaling")
        self.assertEqual(self.f._name, f2.name, "Incorrect name JSON marshaling")
        self.assertEqual(self.f._tmp, f2._tmp, "Incorrect temperature JSON marshaling")
        self.assertEqual(self.f._field, f2._field, "Incorrect field JSON marshaling")

