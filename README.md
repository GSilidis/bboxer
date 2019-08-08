# B-Boxer
Generate smart bounding boxes of changed objects in OSM
_Warning: only simple diff files are supported, augmented diffs are not supported_
_Only nodes changes supported at this moment_

## Purpose of this project

This tool might be useful if you host only tile cache for osm servers and dont want to setup any DB for tile cache 
invalidation. With bboxer you could just diff files from planet.osm. By default, this tool generates bounding boxes in 
format that is used in mapproxy-seed cleanup tasks.

# Usage
 First, you need to create config file. Example of config file: config.example.ini. By default,
 bboxer is looking for file ./config.ini, you could use -c options to use own config file location
```
$ python3 main.py -c ./config.example.ini
```

 After creating file you could just launch bboxer like this:
```
# Downloads latest changeset and outputs bounding boxes to console
$ python3 main.py -d 
```

To get all available console params:
```
$ python3 main.py --help
```

## Config file structure

### Section 'Download'

* DiffBaseUrl - URL to diff file repository. ${DiffBaseUrl}/state.txt should be accessible for getting current sequence number

### Section 'BboxParser'

* MergeDistance - If distance (in Kilometers) from changed node to bounding box centroid is less or equal - bbox extends to this node
* PrecentageToMerge - If this percentage of bounding box area intersects with another bbox - another bbox will be merged into current 
* PolygonMinSize - When bbox polygon is created from point it has next coordinates: 
(point.lon + PolygonMinSize, point.lat - PolygonMinSize, point.lon, point.lat). This param is used for tools that 
require bbox to have certain minimal size. Set 0.02 for mapproxy-seed, set 0.0 if you need bboxes to be as small as possible.