import unittest
import os
import csv
from main import read_json, match_operator, calculate_risk_score, generate_csv

phone_json_string_test = ''' {
  "data\": [
    {
      "type": "call",
      "id": "1",
      "attributes": {
        "riskScore": 0.25002742711675567,
        "greenList": false,
        "redList": false,
        "date": "2024-04-28T10:30:00Z"
      }
    },
    {
      "type": "call",
      "id": 2,
      "attributes": {
        "date": "2024-04-28T11:00:00Z",
        "number": "+441000000000",
        "greenList": false,
        "redList": true,
        "riskScore": 0.5
      }
    },
    {
      "type": "call",
      "id": 3,
      "attributes": {
        "date": "2024-04-28T11:30:00Z",
        "number": "+441111111111",
        "greenList": true,
        "redList": true,
        "riskScore": 0.5
      }
    }]}
'''

operator_json_string_test = ''' {
  "data\": [
    {
      "type": "operator",
      "id": "1",
      "attributes": {
        "prefix": "1000",
        "operator": "OperatorNameTest"
      }
    }]}
'''


class TestPhoneCallProcessing(unittest.TestCase):
    TMP_TEST_CALLS_JSON_PATH = '../data/tmp_test_calls.json'
    TMP_TEST_OPERATORS_JSON_PATH = '../data/tmp_test_operators.json'
    TMP_TEST_REPORT_CSV_PATH = '../output/tmp_test_report.csv'

    def setUp(self):
        def write_tmp_file(filename, inputTest):
            f = open(filename, "w")
            f.write(inputTest)
            f.close()
        write_tmp_file(self.TMP_TEST_CALLS_JSON_PATH, phone_json_string_test)
        write_tmp_file(self.TMP_TEST_OPERATORS_JSON_PATH, operator_json_string_test)
        self.calls_data = read_json(self.TMP_TEST_CALLS_JSON_PATH)['data']
        self.operators_data = read_json(self.TMP_TEST_OPERATORS_JSON_PATH)['data']

    def test_read_json(self):
        # Test reading JSON files
        self.assertIsInstance(self.calls_data, list)
        self.assertIsInstance(self.operators_data, list)
        self.assertEqual(len(self.calls_data), 3, "error in read of calls json")
        self.assertEqual(len(self.operators_data), 1, "error in read of operators json")

    def test_match_operator(self):
        # Test matching operator
        operator = match_operator(self.calls_data[2]['attributes']['number'], self.operators_data)
        self.assertEqual(operator, "OperatorNameTest", "operator does not match correctly to the phone number")
        operator = match_operator('+44000000000', self.operators_data)
        self.assertNotEqual(operator, "OperatorNameTest", "operator matches incorrectly to the phone number")

    def test_calculate_risk_score(self):
        # Test calculating risk score
        self.assertEqual(calculate_risk_score(self.calls_data[0]), 0.3)
        self.assertEqual(calculate_risk_score(self.calls_data[1]), 1.0)
        self.assertEqual(calculate_risk_score(self.calls_data[2]), 0.0)

    def test_generate_csv(self):
        # Test generating CSV
        generate_csv(self.calls_data, self.operators_data, self.TMP_TEST_REPORT_CSV_PATH)
        self.assertTrue(os.path.exists(self.TMP_TEST_REPORT_CSV_PATH),
                        f"File '{self.TMP_TEST_REPORT_CSV_PATH}' does not exist.")
        # Add assertions to verify the generated CSV content or file existence

    def test_csv_contains_three_entries(self):
        num_entries = 0
        with open(self.TMP_TEST_REPORT_CSV_PATH, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            for row in reader:
                num_entries += 1

        self.assertEqual(num_entries, 3, f"Expected 3 entries in CSV file '{self.TMP_TEST_REPORT_CSV_PATH}', "
                                         f"found {num_entries}.")

    @classmethod
    def tearDownClass(cls):
        def delete_input_output_tmp_file(filename):
            os.remove(filename)
        delete_input_output_tmp_file('../data/tmp_test_calls.json')
        delete_input_output_tmp_file('../data/tmp_test_operators.json')
        delete_input_output_tmp_file('../output/tmp_test_report.csv')
        pass


if __name__ == '__main__':
    unittest.main()
