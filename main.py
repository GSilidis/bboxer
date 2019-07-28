import diff_parser
import download_diff
import configparser
from argparse import ArgumentParser

parser = ArgumentParser(description='Generate bounding boxes for osm changesets')
parser.add_argument('-i', '--input-file', dest='input_filename', help='Location of OSM diff file')
parser.add_argument('-d', '--download', action='store_true', dest='download', help='Downloads latest OSM diff file '
                                                                                   '(from DiffBaseUrl in config)')
parser.add_argument('-o', '--output-file', dest='output_filename', help='File for output bboxes')
parser.add_argument('-g', '--as-geojson', action='store_true', dest='geojson', help='Output bboxes as GeoJSON polygons')
parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', help='Verbose output')
parser.add_argument('-c', '--config-file', dest='config_filename', help='ini file with configuration')

arguments = parser.parse_args()

# Read config
configParser = configparser.ConfigParser()
if arguments.config_filename is not None:
    configFilePath = arguments.config_filename
else:
    if arguments.verbose is True:
        print('Config file not provided, using default: ./config.ini')
    configFilePath = './config.ini'
configParser.read(configFilePath)
if len(configParser.sections()) == 0:
    print('Unable to find config file')
    if arguments.config_filename is None:
        print('You need to create config file. '
              'Try "cp ./config.example.ini ./config.ini" or use -c param to provide location of config file')
    exit(-1)

# Find changeset file
inputFile = None
if arguments.download is True:
    if arguments.input_filename is not None:
        print('Downloading new diff file, key -i is useless')
    download_diff.download(configParser.get('Download', 'diffBaseUrl'), arguments.verbose)
    inputFile = 'diff-latest.osc'
else:
    if arguments.input_filename is None:
        print('Input file is not specified')
        parser.print_help()
        exit(-1)
    else:
        inputFile = arguments.input_filename

# Parse changeset
bboxes = diff_parser.parse_diff(inputFile,
                                int(configParser.get('BboxParser', 'MergeDistance')),
                                int(configParser.get('BboxParser', 'PercentageToMerge')),
                                arguments.verbose)

# Output
iterator = 0
result = ''
if arguments.geojson is True:
    result = '{ "type": "FeatureCollection", "features": [ \n'
    for updateBounds in bboxes:
        iterator += 1
        result += ('{{ "type": "Feature", "properties": {{}}, "geometry": {{'
                   '"type": "Polygon", "coordinates": [[[{a}],[{b}],[{c}],[{d}],[{a}]]]'
                   '}} }}, \n'.format(a=(str(updateBounds.W) + ',' + str(updateBounds.S)),
                                      b=(str(updateBounds.W) + ',' + str(updateBounds.N)),
                                      c=(str(updateBounds.E) + ',' + str(updateBounds.N)),
                                      d=(str(updateBounds.E) + ',' + str(updateBounds.S)))
                   )
    result += ']}'
else:
    for updateBounds in bboxes:
        iterator += 1
        result += ('[{w},{s},{e},{n}]\n'.format(w=updateBounds.W, s=updateBounds.S, e=updateBounds.E, n=updateBounds.N))

if arguments.output_filename is not None:
    out_file = open(arguments.output_filename, "w+")
    out_file.write(result)
else:
    print('Output file is not specified, output to console')
    print(result)

if arguments.verbose is True:
    print('Found {} bbox(es)'.format(iterator))
