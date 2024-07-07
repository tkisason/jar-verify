#!/usr/bin/env python3

import urllib
import urllib.parse
import urllib.request
import json
import sys
import datetime
import concurrent.futures

# https://docs.python.org/3/library/concurrent.futures.html


def query_maven(sha1, filename):
    query_parameters = urllib.parse.urlencode(
        {"q": f"1:{sha1}", "rows": 20, "wt": "json"}
    )
    url = "https://search.maven.org/solrsearch/select"
    try:
        query_url = url + "?" + query_parameters
        data = json.loads(urllib.request.urlopen(query_url, timeout=30).read())
    except:
        print(f"[!] Cannot query {sha1}")
        exit()
    found_items = data["response"]["numFound"]
    if found_items == 0:
        print(f"{sha1}\t{filename}\t\tUNKNOWN")
        return {
            "sha1": sha1,
            "filename": filename,
            "id": "UNKNOWN",
            "ts": "UNKNOWN",
            "tags": "UNKNOWN",
        }
    if found_items == 1:
        package_id = data["response"]["docs"][0]["id"]
        timestamp = datetime.datetime.fromtimestamp(
            int(data["response"]["docs"][0]["timestamp"]) / 1000
        ).strftime("%Y.%m.%d %H:%M:%S")
        tags = data["response"]["docs"][0]["tags"]
        print(f"{sha1}\t{filename}\t\t{package_id}")
        return {
            "sha1": sha1,
            "filename": filename,
            "id": package_id,
            "ts": timestamp,
            "tags": tags,
        }
    if found_items > 1:
        packages = [x["id"] for x in data["response"]["docs"]]
        package_ids = ";".join([x["id"] for x in data["response"]["docs"]])
        timestamp = datetime.datetime.fromtimestamp(
            int(data["response"]["docs"][0]["timestamp"]) / 1000
        ).strftime("%Y.%m.%d %H:%M:%S")
        tags = data["response"]["docs"][0]["tags"]
        print(f"{sha1}\t{filename}\t\t{package_ids}")
        return {
            "sha1": sha1,
            "filename": filename,
            "id": packages,
            "ts": timestamp,
            "tags": tags,
        }
    else:
        print(f"{sha1} caused an error!")
        exit()


def parse_sha1file_and_annotate(sha1_filepath):
    hash_file_pairs = []
    maven_data = []
    for line in open(sha1_filepath).read().rstrip().split("\n"):
        hash, filename = line.split()
        hash_file_pairs.append([hash, filename])
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_hash = {
            executor.submit(query_maven, pair[0], pair[1]): pair
            for pair in hash_file_pairs
        }
        for future in concurrent.futures.as_completed(future_to_hash):
            hashfuture = future_to_hash[future]
            try:
                data = future.result()
            except Exception as exc:
                print("Generated an exception: ", exc)
            else:
                maven_data.append(data)
    return maven_data


if __name__ == "__main__":
    if len(sys.argv) == 2:
        jsondata = parse_sha1file_and_annotate(sys.argv[1])
        jsonfilename = f"{sys.argv[1]}.json"
        with open(jsonfilename, "w") as file:
            for line in jsondata:
                file.write(json.dumps(line) + "\n")
            file.close()
    else:
        print("Usage:")
        print('$ find . -type f -iname "*.jar"  -exec sha1sum {} \\; > jar_hashes')
        print("$ ./jar-verify.py jar_hashes")
        print("json data will be located in jar_hashes.json")
