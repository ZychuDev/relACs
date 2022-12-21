from unittest import TestCase
from models import Parameter

class ParameterTest(TestCase):

    def setUp(self):
        self.p = Parameter("alpha", -1, 1, False)
        self.value_emited: float|None = None
        self.p.error_changed.connect(self.set_value_emited)

    def tearDown(self):
        self.p.error_changed.disconnect()

    def test_default_error(self):
        self.assertEqual(self.p.error, 0.0, "incorrect default error")

    def test_set_error(self):
        self.p.set_error(2.5, silent=False)
        self.assertEqual(self.p.error, 2.5, "wrong error after change")
        self.assertEqual(self.value_emited, 2.5, "wrong value emitted")

    def test_set_error_silent(self):
        self.p.set_error(0.9, silent=True)
        self.assertEqual(self.p.error, 0.9, "wrong error after change")
        self.assertEqual(self.value_emited, None, "value emited in silent mode")

    def set_value_emited(self, v: float):
        self.value_emited = v
