# B-Boxer
Generate smart bounding boxes of changed objects in OSM

_Warning: only simple diff files are supported, augmented diffs are not supported_

# Usage

Basic usage:
```
# Downloads latest changeset for russia and outputs bounding boxes to console
$ python3 main.py -d 
```

All console params:
```
$ python3 main.py --help
```

# Dependencies

* python3
* osmdiff
* shapely
