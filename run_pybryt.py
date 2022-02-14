"""A command-line program for running PyBryt on GitHub Actions"""

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
PARSER.add_argument("--timeout")


is_none = lambda s: s.lower() == "none"
"""a function to determine if a user-supplied value is None"""


def parse_list_arg(args):
    """
    Parse a list of newline-delimited arguments, returning a list of strings with leading and
    trailing whitespace stripped.

    Parameters
    ----------
    args : str
        the arguments

    Returns
    -------
    list[str]
        the parsed arguments
    """
    return [u.strip() for u in args.split("\n") if u.strip()]


def get_full_path(repo_path):
    """
    Get the absolute path of a file in the repo using the GITHUB_WORKSPACE environment variable.

    Parameters
    ----------
    repo_path : str
        the relative path to a file from the root of the repo

    Returns
    -------
    str
        the file's absolute path
    """
    workspace_path = os.environ["GITHUB_WORKSPACE"]
    return os.path.join(workspace_path, repo_path)


def download_url(url, save_path):
    """
    Visit a URL and save the response's body to a file.

    Parameters
    ----------
    url       : str
        the URL to visit
    save_path : str
        the path at which to save the response
    """
    url = urllib.request.urlopen(url)
    with open(save_path, "wb") as f:
        f.write(url.read())


def main():
    """
    Run PyBryt using the arguments provided in ``sys.argv``.
    """
    args = PARSER.parse_args()

    # parse the timeout
    if not args.timeout:
        timeout = 1200
    elif is_none(args.timeout):
        timeout = None
    elif args.timeout.isdigit():
        timeout = int(args.timeout)
    else:
        raise ValueError("timeout must be a positive integer, 'none', or unspecified")

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

    stu = pybryt.StudentImplementation(subm_path, addl_filenames=addl_filenames, timeout=timeout)
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
