import unittest

from utils.preprocess import FIELD_MAP, build_feature_frame


class BuildFeatureFrameTests(unittest.TestCase):
    def test_senior_citizen_is_encoded_as_numeric_for_model_features(self):
        form_data = {"senior_citizen": "Yes"}

        frame = build_feature_frame(form_data, {}, ["SeniorCitizen"])

        self.assertEqual(frame.loc[0, "SeniorCitizen"], 1)

    def test_senior_citizen_field_is_mapped_to_model_feature_name(self):
        self.assertEqual(FIELD_MAP["SeniorCitizen"], "senior_citizen")


if __name__ == "__main__":
    unittest.main()
