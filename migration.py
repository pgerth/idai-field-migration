# -*- coding: utf-8 -*-

import xmltodict
import json
from codecs import open

mapping = {
    'PS_AusgrabungID':'identifier',
    'KurzbeschreibungAusgrabung':'shortDescription',
    'DS_Bearbeiter':'eventMetadataRevisor',
    'DS_Erstellungsdatum':'eventMetadataCreationDate',
    'Grabungsverlauf':'longDescription',
    'Auto_Ausgrabungkennung':'number',
    'Schnittleiter':'processor',
    'Sonstige_Anmerkung':'notes',
    'Grabungsumfang':'classification',
    'PS_BefundID':'relations',
    }

print('Read external xml data into a dictionary')
with open('Pergamon_Ausgrabung.xml', 'r', 'utf-8') as fd:
    xml = xmltodict.parse(fd.read(), encoding='utf-8')

# loads a geojson file with the geometries of the migrated objects
with open('Pergamon_Ausgrabung.geojson') as f: 
    jsonFile = json.load(f)
features = jsonFile['features']

# Function which searches for a geometry of a specific object, 
# identified by the iDAIfield Seriennummer
def getGeom(serialnb):
    for feature in features:
        if int(serialnb) == int(feature['properties']['id']):
            return feature['geometry']

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
    trench['geometries'] = getGeom(trench['identifier'])

print('Create JSONL as external file')
with open('Pergamon_Ausgrabung.jsonl', 'w', 'utf-8') as outfile:
    for entry in trenches:
        json.dump(entry, outfile)
        outfile.write('\n')

print('The following objects are not mapped to the target schema:')
print(error_list)
