import argparse
import dill
import os
import pybryt
import sys
import tempfile
import urllib
import validators


PARSER = argparse.ArgumentParser()
PARSER.add_argument("--additional-files")
PARSER.add_argument("--references")
PARSER.add_argument("--subm")


def parse_list_arg(ref_urls):
    return [u.strip() for u in ref_urls.split("\n") if u.strip()]


def get_full_path(repo_path):
    workspace_path = os.environ["GITHUB_WORKSPACE"]
    return os.path.join(workspace_path, repo_path)


def download_url(url, save_path):
    url = urllib.request.urlopen(url)
    with open(save_path, "wb") as f:
        f.write(url.read())


def main():
    args = PARSER.parse_args()

    ref_paths_or_urls = parse_list_arg(args.references)
    addl_filenames = [os.path.abspath(f) for f in parse_list_arg(args.additional_files)]

    sys.path.insert(0, ".")

    refs = []
    for ref_path in ref_paths_or_urls:
        if validators.url(ref_path):
            with tempfile.NamedTemporaryFile(suffix=".pkl") as ref_ntf:
                download_url(ref_path, ref_ntf.name)
                ref = pybryt.ReferenceImplementation.load(ref_ntf.name)
        else:
            ref = pybryt.ReferenceImplementation.load(ref_path)

        if isinstance(ref, list):
            refs.extend(ref)
        else:
            refs.append(ref)

    print("Found refs: ", ", ".join(r.name for r in refs))

    subm_path = get_full_path(args.subm)
    print("Grading ", subm_path)

    stu = pybryt.StudentImplementation(subm_path, addl_filenames=addl_filenames)
    res = stu.check(refs)
    report = pybryt.generate_report(res)
    print(report)

    _, report_path = tempfile.mkstemp(suffix=".txt")
    with open(report_path, "w") as f:
        f.write(report)

    print(f"::set-output name=report-path::{report_path}")

    _, results_path = tempfile.mkstemp(suffix=".pkl")
    with open(results_path, "wb") as f:
        dill.dump(res, f)

    print(f"::set-output name=results-path::{results_path}")

    _, stu_path = tempfile.mkstemp(suffix=".pkl")
    stu.dump(stu_path)

    print(f"::set-output name=student-implementation-path::{stu_path}")


if __name__ == "__main__":
    main()
