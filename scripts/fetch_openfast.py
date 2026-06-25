"""Download the OpenFAST (Apache-2.0) release binary for the current OS into third_party/openfast_bin/.

OpenFAST is the third-party aeroelastic tool this project bridges (see opensg_io/openfast_io.py):
read its ElastoDyn/BeamDyn blade data as a validation reference, and write BeamDyn blade files from the
OpenSG-homogenised 6x6 to DRIVE an OpenFAST run. The binary is only needed if you actually run OpenFAST;
reading/writing the blade text files needs no binary. Source: github.com/OpenFAST/openfast (Apache-2.0).
"""
import json
import os
import platform
import sys
import urllib.request
import zipfile
import io
import tarfile

REPO = "OpenFAST/openfast"
HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, "..", "third_party", "openfast_bin")


def os_tags():
    s = platform.system().lower()
    if s.startswith("win"):
        return ["windows", "win64", "x64.exe"]
    if s == "linux":
        return ["linux", "rhel", "ubuntu"]
    if s == "darwin":
        return ["macos", "darwin", "osx"]
    return [s]


def main():
    os.makedirs(DEST, exist_ok=True)
    api = "https://api.github.com/repos/%s/releases" % REPO
    print("querying", api)
    req = urllib.request.Request(api, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": "opensg_io"})
    rels = json.load(urllib.request.urlopen(req))
    if not rels:
        sys.exit("no releases found at %s -- install OpenFAST manually into %s" % (REPO, DEST))
    tags = os_tags()
    for rel in rels:                                  # newest first
        for asset in rel.get("assets", []):
            nm = asset["name"].lower()
            if any(t in nm for t in tags):
                url = asset["browser_download_url"]
                print("downloading %s (%s, %.1f MB)" % (asset["name"], rel["tag_name"], asset["size"] / 1e6))
                data = urllib.request.urlopen(urllib.request.Request(
                    url, headers={"User-Agent": "opensg_io"})).read()
                if nm.endswith(".zip"):
                    zipfile.ZipFile(io.BytesIO(data)).extractall(DEST)
                elif nm.endswith((".tar.gz", ".tgz")):
                    tarfile.open(fileobj=io.BytesIO(data), mode="r:gz").extractall(DEST)
                else:
                    open(os.path.join(DEST, asset["name"]), "wb").write(data)
                print("extracted to", DEST)
                return
    sys.exit("no OS-matching OpenFAST asset found; install manually into %s" % DEST)


if __name__ == "__main__":
    main()
