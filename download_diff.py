import requests
import gzip


def download(base_url, verbose):
    response = requests.get(base_url + '/state.txt')
    if response.status_code != 200:
        print('Unable to get current state')
        exit(-1)

    sequence_number = -1
    for line in response.text.split("\n"):
        if line.startswith("sequenceNumber"):
            sequence_number = int(line[15:])

    if sequence_number < 0:
        print('Unable to get sequence number from {}'.format(response.url))
        exit(-1)

    if verbose is True:
        print('State received, current sequence: {}'.format(sequence_number))

    osm_sequence = str(sequence_number).zfill(9)
    diff_url = base_url + ('/{}/{}/{}.osc.gz'.format(osm_sequence[:3], osm_sequence[3:6], format(osm_sequence[6:])))

    diff_file = open("diff-latest.osc", "wb+")

    response = requests.get(diff_url)
    if response.status_code != 200:
        print("Unable to download diff")
        exit(-1)
    else:
        uncompressed_diff = gzip.decompress(response.content)
        diff_file.write(uncompressed_diff)
