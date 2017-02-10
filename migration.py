# -*- coding: utf-8 -*-

import xmltodict
import json

mapping = {
    'PS_AusgrabungID':'identifier',
    'KurzbeschreibungAusgrabung':'shortDescription',
    'DS_Bearbeiter':'eventMetadataRevisor',
    'DS_Erstellungsdatum':'eventMetadataCreationDate',
    }

print('Read external xml data into a dictionary')
with open('Pergamon_Ausgrabung.xml') as fd:
    xml = xmltodict.parse(fd.read())

trenches = xml['FMPDSORESULT']['ROW']
error_list = []
for key, value in trenches[1].items():
    if key not in mapping.keys():
        error_list.append(key)

print('Change values for keys in dictionary')
for trench in trenches:
    for key, value in trench.items():
        if value is None:
            del trench[key]
        elif key in mapping.keys():
            trench[mapping[key]] = trench[key]
            del trench[key]
        else:
            del trench[key]
    trench['type'] = 'trench'

print('Create JSONL as external file')
with open('Pergamon_Ausgrabung.jsonl', 'w') as outfile:
    for entry in trenches:
        json.dump(entry, outfile)
        outfile.write('\n')

print('The following objects are not mapped to the target schema:')
print(error_list)
