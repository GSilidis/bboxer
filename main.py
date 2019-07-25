import diff_parser
import download_diff
from argparse import ArgumentParser

parser = ArgumentParser(description='Generate bounding boxes for osm changesets')
parser.add_argument('-i', '--input-file', dest='input_filename', help='Location of OSM diff file')
parser.add_argument('-d', '--download', action='store_true', dest='download', help='Downloads latest OSM diff file '
                                                                                   '(Russian daily changeset, '
                                                                                   'from geofabrik)')
parser.add_argument('-o', '--output-file', dest='output_filename', help='File for output bboxes')
parser.add_argument('-g', '--as-geojson', action='store_true', dest='geojson', help='Output bboxes as GeoJSON polygons')
parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', help='Verbose output')

arguments = parser.parse_args()

inputFile = None
if arguments.download is True:
    if arguments.input_filename is not None:
        print('Downloading new diff file, key -i is useless')
    download_diff.download(arguments.verbose)
    inputFile = 'diff-latest.osc'
else:
    if arguments.input_filename is None:
        print('Input file is not specified')
        parser.print_help()
        exit(-1)
    else:
        inputFile = arguments.input_filename

bboxes = diff_parser.parse_diff(inputFile, arguments.verbose)

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
