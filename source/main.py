import json
import csv
import datetime


def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def match_operator(phone_number, operators):
    if phone_number == "Withheld":
        return "Unknown"

    # Check country code is uk
    if phone_number[:3] != "+44":
        return "Unknown"

    # phone_number[3] contains the matching char to the operator prefix
    for operator in operators:
        if operator["attributes"]["prefix"][0] == phone_number[3]:
            return operator["attributes"]['operator']

    return "Unknown"


def calculate_risk_score(call):
    if call['attributes']['greenList']:
        return 0.0
    if call['attributes']['redList']:
        return 1.0
    else:
        return round(call['attributes']['riskScore'], 1)


def generate_csv(calls_data, operators_data, filename):
    calls_data.sort(key=lambda x: datetime.datetime.strptime(x['attributes']['date'], "%Y-%m-%dT%H:%M:%SZ"))

    with open(filename, 'w') as csvfile:
        fieldnames = ['id', 'date', 'number', 'operator', 'riskScore']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for call in calls_data:
            phone_number = "Withheld"
            if "number" in call['attributes']:
                phone_number = call['attributes']['number']
            operator = match_operator(phone_number, operators_data)
            risk_score = calculate_risk_score(call)
            writer.writerow({
                'id': call['id'],
                'date': datetime.datetime.strptime(call['attributes']['date'], "%Y-%m-%dT%H:%M:%SZ"),
                'number': phone_number,
                'operator': operator,
                'riskScore': risk_score
            })


if __name__ == "__main__":
    calls_data = read_json('../data/calls.json')['data']
    operators_data = read_json('../data/operators.json')['data']
    generate_csv(calls_data, operators_data, '../output/report.csv')
