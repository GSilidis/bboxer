from osmdiff import OSMChange
from osmdiff import osm
from bbox import BoundingBox


bboxes = []

mergeDistance = 0
mergePercentage = 0


def parse_object(osm_object):
    object_type = 0
    if type(osm_object) == osm.osm.Node:
        inserted = False
        for bbox in bboxes:
            if bbox.__contains__(osm_object):
                inserted = True
            else:
                if bbox.distance_to_osm_object(osm_object) < bbox.get_merge_distance():
                    bbox.insert_object(osm_object)
                    inserted = True

        if not inserted:
            # Some tools, like mapproxy-seed, doesnt want to work with polygons that have all points at the same spot
            bbox = BoundingBox([float(osm_object.attribs['lon']) + 0.0001,
                                float(osm_object.attribs['lat']) - 0.0001],
                               [float(osm_object.attribs['lon']),
                                float(osm_object.attribs['lat'])], mergeDistance, mergePercentage)
            bboxes.append(bbox)
        object_type = 1
    if type(osm_object) == osm.osm.Way:
        object_type = 2
    if type(osm_object) == osm.osm.Relation:
        object_type = 3
    return object_type


def parse_diff(file, configMergeDistance, configPercentageToMerge, verbose):
    nodes_count = 0
    ways_count = 0
    relations_count = 0

    global mergeDistance
    mergeDistance = configMergeDistance
    global mergePercentage
    mergePercentage = configPercentageToMerge


    d = OSMChange(file=file)

    for osmObject in d.create:
        type_of = parse_object(osmObject)
        if type_of == 1:
            nodes_count += 1
        elif type_of == 2:
            ways_count += 1
        elif type_of == 3:
            relations_count += 1
        else:
            print('This part shouldn\'t be reached, check algorithm')

    if verbose is True:
        print('Created: {nodes} nodes, {ways} ways and {relations} relations'.format(nodes=nodes_count, ways=ways_count,
                                                                                     relations=relations_count))

    nodes_count = 0
    ways_count = 0
    relations_count = 0

    for osmObject in d.modify:
        type_of = parse_object(osmObject)
        if type_of == 1:
            nodes_count += 1
        elif type_of == 2:
            ways_count += 1
        elif type_of == 3:
            relations_count += 1
        else:
            print('This part shouldn\'t be reached, check algorithm')

    if verbose is True:
        print('Modified: {nodes} nodes, {ways} ways and {relations} relations'.format(nodes=nodes_count, ways=ways_count,
                                                                                      relations=relations_count))

    nodes_count = 0
    ways_count = 0
    relations_count = 0

    for osmObject in d.delete:
        type_of = parse_object(osmObject)
        if type_of == 1:
            nodes_count += 1
        elif type_of == 2:
            ways_count += 1
        elif type_of == 3:
            relations_count += 1
        else:
            print('This part shouldn\'t be reached, check algorithm')

    if verbose is True:
        print('Deleted: {nodes} nodes, {ways} ways and {relations} relations'.format(nodes=nodes_count, ways=ways_count,
                                                                                     relations=relations_count))
    iterator = 0

    # Merge polygons until its possible
    while True:
        merged = False
        for bbox1 in bboxes:
            if bbox1.merged is False:
                for bbox2 in bboxes:
                    if bbox1 != bbox2 and bbox2.merged is False:
                        area = bbox1.get_poly().intersection(bbox2.get_poly()).area
                        if (bbox1.is_suitable_for_merge(area)) or bbox2.is_suitable_for_merge(area):
                            bbox1.merge_into(bbox2)
                            merged = True
        if not merged:
            break
        iterator += 1

    if verbose is True:
        print('Merged in {} iteration(s)'.format(iterator))
    return filter(lambda x: x.merged is False, bboxes)
