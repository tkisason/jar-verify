# jar-verify

Imagine you have a number of jar files, you want to detect which jar files are possibly tampered or unique, and which ones are packages that are known and available on maven.

jar-verify solves this by querying maven with the sha1 value of the jar file, and returning info about which files are known on the repository. The rest will be stored in a file for further analysis.

Note:
- This can't detect if a file is malicious, backdoored or not, only if it exists on Maven.
- This deliberately uses core-utils and base python libraries, so you can run it on almost any linux instance / container without dependencies


# How-To

Fetch all sha1 hashes of jar files you want to analyze:

```
find . -type f -iname "*.jar"  -exec sha1sum {} \; > jar_hashes
```





