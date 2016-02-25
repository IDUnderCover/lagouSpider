__author__ = 'hadoop'

import json
if __name__ == '__main__':

    # f = open('../positions.json','rb')
    # for line in f.readlines():
    #     print len(json.loads(line)['companySize'])

    with open('../positions.json','rb') as f:
        lines = f.readlines()

    maplines = map(lambda line: json.loads(line), lines)

    for i in maplines:
        print(i['companySize'])