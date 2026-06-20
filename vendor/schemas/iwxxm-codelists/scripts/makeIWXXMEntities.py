#!/usr/bin/env python3

import re
import os
import shutil
import pandas

dictionary = {'description':'dct:description',
              'label':'rdfs:label',
              'notation':'skos:notation',
              'status':'reg:status',
              'altLabel':'skos:altLabel',
              'modified':'dct:modified',
              'versionInfo':'owl:versionInfo',
              'seeAlso':'rdfs:seeAlso',
              'manager':'reg:manager',
              'owner':'reg:owner',
              'source':'dc:source',
              'publisher':'dct:publisher',
              'subregister':'reg:subregister'}

header = ('@prefix qudt:  <http://qudt.org/schema/qudt#>.\n'
          '@prefix ssd:   <http://www.w3.org/ns/sparql-service-description#>.\n'
          '@prefix owl:   <http://www.w3.org/2002/07/owl#>.\n'
          '@prefix xsd:   <http://www.w3.org/2001/XMLSchema#>.\n'
          '@prefix skos:  <http://www.w3.org/2004/02/skos/core#>.\n'
          '@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#>.\n'
          '@prefix qudt-unit: <http://qudt.org/vocab/unit#>.\n'
          '@prefix qb:    <http://purl.org/linked-data/cube#>.\n'
          '@prefix dgu:   <http://reference.data.gov.uk/def/reference/>.\n'
          '@prefix ui:    <http://purl.org/linked-data/registry-ui#>.\n'
          '@prefix dct:   <http://purl.org/dc/terms/>.\n'
          '@prefix reg:   <http://purl.org/linked-data/registry#>.\n'
          '@prefix qudt-quantity: <http://qudt.org/vocab/quantity#>.\n'
          '@prefix grib2-parameter: <http://codes.wmo.int/grib2/schema/parameter/>.\n'
          '@prefix api:   <http://purl.org/linked-data/api/vocab#>.\n'
          '@prefix vann:  <http://purl.org/vocab/vann/>.\n'
          '@prefix prov:  <http://www.w3.org/ns/prov#>.\n'
          '@prefix foaf:  <http://xmlns.com/foaf/0.1/>.\n'
          '@prefix common-unit: <http://codes.wmo.int/common/schema/unit/>.\n'
          '@prefix cc:    <http://creativecommons.org/ns#>.\n'
          '@prefix grib2-core: <http://codes.wmo.int/grib2/schema/core/>.\n'
          '@prefix void:  <http://rdfs.org/ns/void#>.\n'
          '@prefix version: <http://purl.org/linked-data/version#>.\n'
          '@prefix bufr4-core: <http://codes.wmo.int/bufr4/schema/core/>.\n'
          '@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.\n'
          '@prefix ldp:   <http://www.w3.org/ns/ldp#>.\n'
          '@prefix time:  <http://www.w3.org/2006/time#>.\n'
          '@prefix qudt-dimension: <http://qudt.org/vocab/dimension#>.\n'
          '@prefix vs:    <http://www.w3.org/2003/06/sw-vocab-status/ns#>.\n'
          '@prefix common-core: <http://codes.wmo.int/common/schema/core/>.\n'
          '@prefix dc:    <http://purl.org/dc/elements/1.1/>.\n\n')

collectionTemplate = ('<{identity}>\n'
                      '\ta reg:Register, skos:Collection, ldp:Container')

entityTemplate = ('<{identity}>\n'
                  '\ta skos:Concept')

def clean(astr):
    if '"' in astr:
        astr = astr.replace('"', "'")
    astr = astr.strip()
    return astr

def main():
    print('Converting IWXXM Codelists from CSV to TTL format')
    root_path = os.path.dirname(os.path.dirname(__file__))
    if os.path.exists(os.path.join(root_path, 'TTL')):
        shutil.rmtree(os.path.join(root_path, 'TTL'))
    os.mkdir(os.path.join(root_path, 'TTL'))

    for (root_csv, dummy1, dummy2) in os.walk(os.path.join(root_path, 'CSV')):

        # Skip obsoleted tables 'observable-property' and 'observation-type'

        if os.path.basename(root_csv) == 'observable-property' or os.path.basename(root_csv) == 'observation-type':
            continue
        
        root_ttl = os.path.join(root_path, 'TTL', root_csv[len(os.path.join(root_path, 'CSV')) + 1:])
        
        # If {root_path}/CSV/{table}/{table}_container.csv exist
        if os.path.exists(os.path.join(root_csv, '{}_container.csv'.format(os.path.basename(root_csv)))):

            # Create {root_path}/TTL/{table}
            if not os.path.exists(root_ttl):
                os.mkdir(root_ttl)
            
            # Read {root_path}/CSV/{table}/{table}_container.csv.
            # For each row/record with non-empty identity column:
            #     1. Create {root_path}/CSV/{table}/{identity}
            #     2. Create {root_path}/CSV/{table}/{indentity}.ttl
            record = pandas.read_csv(os.path.join(root_csv, '{}_container.csv'.format(os.path.basename(root_csv))), encoding = 'utf-8')
            for i in range(record.shape[0]):
                if record.iloc[i]['notation'] != '' and not pandas.isna(record.iloc[i]['notation']):
                    with open(os.path.join(root_ttl, '{}.ttl'.format(record.iloc[i]['notation'])), 'w', encoding = 'utf-8') as ttlf:
                        print('Creating {}'.format(os.path.join(root_ttl, '{}.ttl'.format(record.iloc[i]['notation']))))
                        ttlf.write(header)
                        ttlf.write(collectionTemplate.format(identity = record.iloc[i]['notation']))
                        for j in list(record):
                            if j != 'id' and j != 'related':
                                if record.iloc[i][j] != '' and not pandas.isna(record.iloc[i][j]):
                                    if j == 'notation' or j == 'status' or j == 'modified':
                                        ttlf.write(';\n\t{a} "{b}"'.format(a = dictionary[j], b = record.iloc[i][j]))
                                    elif re.match('^http\:\/\/', record.astype(str).iloc[i][j]):
                                        ttlf.write(';\n\t{a} <{b}>'.format(a = dictionary[j], b = record.iloc[i][j]))
                                    elif re.match('^[0-9]+$', record.astype(str).iloc[i][j]):
                                        ttlf.write(';\n\t{a} {b}'.format(a = dictionary[j], b = record.iloc[i][j]))
                                    else:
                                        ttlf.write(';\n\t{a} "{b}"@en'.format(a = dictionary[j], b = record.iloc[i][j]))
                        ttlf.write('.\n')
                        ttlf.close()

        # if {root_path}/CSV/{table}/{table}_entity.csv exist
        if os.path.exists(os.path.join(root_csv, '{}_entity.csv'.format(os.path.basename(root_csv)))):

            # Create {root_path}/TTL/{table}
            if not os.path.exists(root_ttl):
                os.mkdir(root_ttl)
            
            # Read {root_path}/CSV/{table}/{table}_entity.csv.
            # For each row/record with non-empty identity column:
            #     1. Create {root_path}/CSV/{table}/{identity}.ttl
            record = pandas.read_csv(os.path.join(root_csv, '{}_entity.csv'.format(os.path.basename(root_csv))), encoding = 'utf-8')
            for i in range(record.shape[0]):
                if record.iloc[i]['notation'] != '' and not pandas.isna(record.iloc[i]['notation']):
                    with open(os.path.join(root_ttl, '{}.ttl'.format(record.iloc[i]['notation'])), 'w', encoding = 'utf-8') as ttlf:
                        print('Creating {}'.format(os.path.join(root_ttl, '{}.ttl'.format(record.iloc[i]['notation']))))
                        ttlf.write(header)
                        ttlf.write(entityTemplate.format(identity = record.iloc[i]['notation']))
                        for j in list(record):
                            if j != 'id' and j != 'related':
                                if record.iloc[i][j] != '' and not pandas.isna(record.iloc[i][j]):
                                    if j == 'notation' or j == 'status' or j == 'modified':
                                        ttlf.write(';\n\t{a} "{b}"'.format(a = dictionary[j], b = record.iloc[i][j]))
                                    elif re.match('^http\:\/\/', record.astype(str).iloc[i][j]):
                                        ttlf.write(';\n\t{a} <{b}>'.format(a = dictionary[j], b = record.iloc[i][j]))
                                    elif re.match('^[0-9]+$', record.astype(str).iloc[i][j]):
                                        ttlf.write(';\n\t{a} {b}'.format(a = dictionary[j], b = record.iloc[i][j]))
                                    else:
                                        ttlf.write(';\n\t{a} "{b}"@en'.format(a = dictionary[j], b = record.iloc[i][j]))
                        ttlf.write('.\n')
                        ttlf.close()
                        
if __name__ == '__main__':
    main()
