import json
import csv
import datetime


class PhoneCall:
    def __init__(self, phoneId, date, riskScore, number='Withheld',
                 greenList=False, redList=False):
        self.phoneId = phoneId
        self.date = date
        self.number = number
        self.greenList = greenList
        self.redList = redList
        self.operatorName = 'Unknown'
        # Risk can be calculated at the initialisation of the object
        if greenList:
            self.riskScore = 0.0
        elif redList:
            self.riskScore = 1.0
        else:
            self.riskScore = round(riskScore, 1)


class PhoneOperator:
    def __init__(self, operatorId, operatorName, prefix):
        self.operatorId = operatorId
        self.operatorName = operatorName
        self.prefix = prefix


class DataProcessor:
    def __init__(self, callsFile, operatorsFile):
        self.callsFile = callsFile
        self.operatorsFile = operatorsFile
        self.phoneCalls = []
        self.phoneOperators = []

    def load_json_data(self):
        def read_file(file):
            with open(file, 'r') as file:
                return json.load(file)

        # processing the calls into the class
        phoneCalls = read_file(self.callsFile)['data']
        for call in phoneCalls:
            phone_number = 'Withheld'
            if "number" in call['attributes']:
                phone_number = call['attributes']['number']
            phoneInstance = PhoneCall(call['id'], call['attributes']['date'], call['attributes']['riskScore'],
                                      phone_number, call['attributes']['greenList'], call['attributes']['redList'])
            self.phoneCalls.append(phoneInstance)

        # processing the operators into the class
        phoneOperators = read_file(self.operatorsFile)['data']
        for operator in phoneOperators:
            OperatorInstance = PhoneOperator(operator['id'], operator['attributes']['operator'],
                                             operator['attributes']['prefix'])
            self.phoneOperators.append(OperatorInstance)

    def add_operators_to_calls(self):
        for call in self.phoneCalls:
            for operator in self.phoneOperators:
                # Operator is already unknown, if we find a match, we change the name
                if call.number[3] == operator.prefix[0]:
                    call.operatorName = operator.operatorName
                    break

    def write_calls_csv(self, output_file):
        self.phoneCalls.sort(key=lambda x: datetime.datetime.strptime(x.date, "%Y-%m-%dT%H:%M:%SZ"))

        with open(output_file, 'w') as csvfile:
            fieldnames = ['id', 'date', 'number', 'operator', 'riskScore']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for call in self.phoneCalls:
                writer.writerow({
                    'id': call.phoneId,
                    'date': datetime.datetime.strptime(call.date, "%Y-%m-%dT%H:%M:%SZ"),
                    'number': call.number,
                    'operator': call.operatorName,
                    'riskScore': call.riskScore
                })


if __name__ == "__main__":
    processor = DataProcessor('../data/calls.json', '../data/operators.json')
    processor.load_json_data()
    processor.add_operators_to_calls()
    processor.write_calls_csv('output2.csv')
