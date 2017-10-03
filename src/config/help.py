#coding:utf-8
import json

f = open('districts.json.bak')

districts = json.loads(f.read())

index_block = dict()

for index in range(len(districts)):
    index_block[districts[index]['district_code']] = (index, -1, -1)
    for sub_index in range(len(districts[index]['sub_districts'])):
        index_block[districts[index]['sub_districts'][sub_index]['district_code']] = (index,sub_index,-1)
        for sub_sub_index in range(len(districts[index]['sub_districts'][sub_index]['sub_districts'])):
            index_block[districts[index]['sub_districts'][sub_index]['sub_districts'][sub_sub_index]['district_code']] = (index, sub_index, sub_sub_index)

output = {
    'index': index_block,
    'districts': districts
}

f.close()
f = open('tmp.conf','w')
f.write(json.dumps(output, ensure_ascii=False))
f.close()


