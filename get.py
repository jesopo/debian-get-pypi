import json, sys
from urllib import parse, request
import psycopg2

DOAP_URL = "https://pypi.python.org/pypi?:action=doap&name=%s&version=%s"
doap_urls = {}

try:
    conn = psycopg2.connect(host="public-udd-mirror.xvm.mit.edu", database="udd", 
    user="public-udd-mirror", password="public-udd-mirror")
    cursor = conn.cursor()
    cursor.execute("SELECT source, upstream_url FROM upstream WHERE upstream_url IS NOT NULL")
except Exception as e:
    sys.stderr.write("failed to get data from database;\n%s\n" % e)
    sys.exit(1)
for name, url in cursor.fetchall():
    parsed = parse.urlparse(url)
    if parsed.hostname == "pypi.debian.net":
        package_name = parsed.path[1:].split("/", 1)[0]
        version = parsed.path.rsplit("-", 1)[1]
        if version.endswith(".tar.gz"):
            version = version.rsplit(".tar.gz", 1)[0]
        elif version.endswith(".tar.bz2"):
            version = version.rsplit(".tar.bz2", 1)[0]
        elif version.endswith(".zip"):
            version = version.rsplit(".zip", 1)[0]
        if "_" in version:
            version = version.split("_", 1)[0]
        package_doap_url = DOAP_URL % (package_name, version)
        doap_urls[name] = package_doap_url

doap_json = json.dumps(doap_urls, sort_keys=True, indent=4)
sys.stdout.write(doap_json)