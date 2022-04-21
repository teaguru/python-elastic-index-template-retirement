"""
How to call script:
python3 put_patterns.py logstash-high logstash-high.txt
(first argument 'Index Template' second is path to the index pattern list)
index template could be from the list['logstash-high', 'logstash-low', 'logstash-morerate', 'logstash-restricted']
Set your
username = 'username'
password = 'password'
and 
url = 'http://localhost:80/_template/' + pattern
"""
try:
    import requests
    from requests.auth import HTTPBasicAuth
    import json
    import sys
    from os.path import exists

    print("All Modules are Loaded")
except Exception as e:
    print("Some Modules aren't loaded".format(e))
template_list = ['logstash-high', 'logstash-low', 'logstash-morerate', 'logstash-restricted']
if sys.argv[1] in template_list:
    pattern = sys.argv[1]
    if pattern == 'logstash-restricted':
        lifecycle_policy = "remove-indexes-older-than-365-days"
    elif pattern == 'logstash-high':
        lifecycle_policy = "remove-indexes-older-than-180-days"
    elif pattern == 'logstash-moderate':
        lifecycle_policy = "remove-indexes-older-than-90-days"
    elif pattern == 'logstash-low':
        lifecycle_policy = "remove-indexes-older-than-30-days"
else:
    print('not valid index template')
    exit
if exists(sys.argv[2]):
    path_to_index_list = sys.argv[2]
else:
    exit


def make_list(listname):
    lines = []
    with open(listname) as f:
        lines = f.readlines()
    count = 0
    index_list = []
    for line in lines:
        count += 1
        line = line.split()
        index_list.append(line[0] + '*')
    return(index_list)


def send_req():
    index_patterns = make_list(path_to_index_list)
    data = {
        "order": 0,
        "version": 60001,
        "index_patterns": index_patterns,
        "settings": {
            "index": {
                "lifecycle": {
                    "name": lifecycle_policy
                },
                "number_of_shards": "1",
                "refresh_interval": "5s"
            }
        },
        "mappings": {
            "dynamic_templates": [{
                "message_field": {
                    "path_match": "message",
                    "mapping": {
                        "norms": "false",
                        "type": "text"
                    },
                    "match_mapping_type": "string"
                }
            }, {
                "string_fields": {
                    "mapping": {
                        "norms": "false",
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "ignore_above": 256,
                                "type": "keyword"
                            }
                        }
                    },
                    "match_mapping_type": "string",
                    "match": "*"
                }
            }],
            "properties": {
                "@timestamp": {
                    "type": "date"
                },
                "geoip": {
                    "dynamic": "true",
                    "type": "object",
                    "properties": {
                        "ip": {
                            "type": "ip"
                        },
                        "latitude": {
                            "type": "half_float"
                        },
                        "location": {
                            "type": "geo_point"
                        },
                        "longitude": {
                            "type": "half_float"
                        }
                    }
                },
                "@version": {
                    "type": "keyword"
                }
            }
        },
        "aliases": {}
    }
    username = 'username'
    password = 'password'
    headers = {
        'Content-type': 'application/json'
    }
    print('will update:', pattern)
    print('index patterns from file:', path_to_index_list)
    url = 'http://localhost:80/_template/' + pattern
    response = requests.put(
        url,
        auth = HTTPBasicAuth(username, password),
        headers=headers, data=json.dumps(data))
    if (response.json()['acknowledged']):
        print('Index patternt to ', pattern, ' are uploaded sucessfully')
send_req()
