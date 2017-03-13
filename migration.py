# -*- coding: utf-8 -*-

import xmltodict
import simplejson as json
from codecs import open

attrMapping = {
    # Foto
    'PS_FotoID':'id',
    'Auto_Fotokennung':'identifier',
    'KurzbeschreibungFoto':'shortDescription',
    'Fotograf':'processor',
}

Befund = {
    # Befund
    'PS_BefundID':'identifier',
    'Auto_BefundKennung':'number',
    'KurzbeschreibungBefund':'shortDescription',
    'Schicht_Beschreibung':'longDescription',
    'Mauer_Beschreibung':'longDescription',
    'Masze_Laenge':'length',
    'Masze_Hoehe':'height',
    'Masze_Breite':'width',
    'Befundart':'classificaton',
    'Tagebuch':'diary',
    'Datum_Abtragung':'endingDate',
    'DS_Bearbeiter':'processor',
}

Keramik = {
    # Keramik
    'PS_KeramikID':'identifier',
    'Auto_Objektkennung_Index':'number',
    'Materialklasse':'shortDescription',
    'Nummer_Fund':'number',
    'Durchmesser':'diameter',
    'Herkunft':'provenance',
    'Hoehe':'height',
    'Laenge':'length',
    'Gewicht':'weight',
    'Aufbewahrung_Ort':'inventoryLocation',
    'Aufbewahrung_InvNr':'inventoryNumber',
    'Erhaltung_Sonstiges':'condition',
    'Funddatum':'date',
    'Grobdatierung':'dating',
}

Ausgrabung = {
    # Ausgrabung
    'PS_AusgrabungID':'identifier',
    'Auto_Ausgrabungkennung':'number',
    'KurzbeschreibungAusgrabung':'shortDescription',
    'Grabungsverlauf':'longDescription',
    'Schnittleiter':'processor',
    'Sonstige_Anmerkung':'notes',
    }

relationMapping = {
#    'FS_BefundID':'isLocatedIn',
#    'FS_AusgrabungID':'belongsTo',
#    'PS_BefundID':'includes',
#    'PS_KeramikID':'embeds',
    'ObjektFoto':'depicts',
}

idaifieldFile = 'Pergamon_Foto.xml'
geometryFile = 'Pergamon_Befund.geojson'
outputFile = 'Pergamon_Foto.jsonl'
datasetType = 'image'

print('Read external xml data into a dictionary')
with open(idaifieldFile, 'r', 'utf-8') as fd:
    xml = xmltodict.parse(fd.read(), encoding='utf-8')

# loads a geojson file with the geometries of the migrated objects
with open(geometryFile) as f: 
    jsonFile = json.load(f)
features = jsonFile['features']

# Function which searches for a geometry of a specific object, 
# identified by the iDAIfield Seriennummer
def getGeom(serialnb):
    for feature in features:
        if int(serialnb) == int(feature['properties']['id']):
            return feature['geometry']

datasets = xml['FMPDSORESULT']['ROW']
error_list = []
for key, value in datasets[1].items():
    if key not in attrMapping.keys():
        error_list.append(key)

print('Change values for keys in dictionary')
for dataset in datasets:
    for key, value in dataset.items(): 
        if value is None:
            del dataset[key]
        elif key in relationMapping.keys():
            if dataset.get('relations') is None:
                dataset['relations'] = {}
            if type(dataset[key]) is unicode:
                dataset['relations'][relationMapping[key]] = dataset[key]
            else: 
                dataset['relations'][relationMapping[key]] = dataset[key]['DATA']
            del dataset[key]
        elif key in attrMapping.keys():
            dataset[attrMapping[key]] = dataset[key].encode("utf-8")
            del dataset[key]
        else:
            del dataset[key]
    dataset['type'] = datasetType
#    dataset['geometries'] = [getGeom(dataset['identifier'])]

print('Create JSONL as external file')
with open(outputFile, 'w', 'utf-8') as outfile:
    for entry in datasets:
        json.dump(entry, outfile, ensure_ascii=False, encoding="utf-8")
        outfile.write('\n')

print('The following objects are not mapped to the target schema:')
print(error_list)
