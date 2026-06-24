"""Download the PreVABS (GPL-2.0) release binary for the current OS into third_party/prevabs_bin/.

PreVABS is the 2D-solid cross-section mesher used by this project. It is NOT bundled in git (large,
GPL); this script fetches the matching release asset from github.com/wenbinyugroup/prevabs/releases.
The corresponding source is the third_party/prevabs submodule. See NOTICE for license terms.
"""
import json
import os
import platform
import sys
import urllib.request
import zipfile
import io

REPO = "wenbinyugroup/prevabs"
HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, "..", "third_party", "prevabs_bin")


def os_tag():
    s = platform.system().lower()
    if s.startswith("win"):
        return ["windows-x64", "win64", "windows"]
    if s == "linux":
        return ["linux-x64", "linux"]
    if s == "darwin":
        return ["macos", "darwin", "osx"]
    return [s]


def main():
    os.makedirs(DEST, exist_ok=True)
    api = "https://api.github.com/repos/%s/releases" % REPO
    print("querying", api)
    req = urllib.request.Request(api, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "WindIO_to_OpenSG"})
    rels = json.load(urllib.request.urlopen(req))
    if not rels:
        sys.exit("no releases found at %s -- download PreVABS manually and place prevabs(.exe) in %s" % (REPO, DEST))
    tags = os_tag()
    for rel in rels:                                  # newest first
        for asset in rel.get("assets", []):
            nm = asset["name"].lower()
            if any(t in nm for t in tags) and nm.endswith((".zip", ".tar.gz", ".tgz")):
                url = asset["browser_download_url"]
                print("downloading %s (%s, %.1f MB)" % (asset["name"], rel["tag_name"], asset["size"] / 1e6))
                data = urllib.request.urlopen(urllib.request.Request(
                    url, headers={"User-Agent": "WindIO_to_OpenSG"})).read()
                if nm.endswith(".zip"):
                    zipfile.ZipFile(io.BytesIO(data)).extractall(DEST)
                else:
                    import tarfile
                    tarfile.open(fileobj=io.BytesIO(data)).extractall(DEST)
                print("extracted to", os.path.abspath(DEST))
                print("Set PREVABS_EXE to the prevabs(.exe) path, or pass --prevabs to convert_station.py.")
                return
    sys.exit("no asset matched OS tags %s. See %s/releases and place the binary in %s" % (tags, REPO, DEST))


if __name__ == "__main__":
    main()
