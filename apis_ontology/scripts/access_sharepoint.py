# Script to connect to Sharepoint to access Excel files.
#
# The script expects environment variables
# SP_USER, SP_PASSWORD, SP_SITE, SP_GROUP, SP_DIRECTORY
# to be set.

import os
import sharepy
import pandas as pd
import getpass
from pathlib import Path
from urllib.parse import quote


def import_and_parse_data(parse_data):
    s = sharepoint_connect()

    files = fetch_sharepoint_files(s)

    fname, file_url = input_dialog(files)

    imported, failed = import_file_data(s, fname, file_url, parse_data)

    for i in imported:
        # TODO processing equivalent to Zotero import script
        pass

    for f in failed:
        # TODO processing equivalent to Zotero import script
        pass


def sharepoint_connect():
    """
    Connect to SharePoint.

    :return: SharePoint connection object
    """
    sp_user = os.environ.get("SP_USER", None)
    sp_pass = os.environ.get("SP_PASSWORD", None)

    while sp_user is None or sp_user == "":
        sp_user = os.environ.setdefault(
            "SP_USER", getpass.getpass(prompt="Enter SharePoint user name:\n")
        )

    while sp_pass is None or sp_pass == "":
        sp_pass = os.environ.setdefault(
            "SP_PASSWORD", getpass.getpass(prompt="Enter SharePoint password:\n")
        )

    sp_site = os.environ.get("SP_SITE", None)
    while sp_site is None or sp_site == "":
        sp_site = os.environ.setdefault(
            "SP_SITE",
            input(prompt="Enter SharePoint site/domain:\n"),
        )

    try:
        s = sharepy.connect(sp_site, username=sp_user, password=sp_pass)
        s.save()
    except Exception as e:
        print("Cannot connect to SharePoint!")
        exit(1)

    return s


def input_dialog(files):
    """
    Input dialogue to let user choose from which Excel files
    to import data.

    """
    fname = None
    file_url = None

    extra_choices = [
        {
            "order": 1000,
            "label": "Exit",
            "primary_key": "X",
            "allowed_keys": ["X", "x"],
            "run": (lambda: exit(0)),
        },
    ]

    extra_keys = sum(
        [[e["primary_key"]] + e["allowed_keys"] for e in extra_choices], []
    )

    while True:
        choices = generate_input_choices(
            files,
            extra_choices=sorted(extra_choices, key=lambda a: a["order"]),
        )

        allowed_keys = list(
            set(extra_keys + sum([[c["key"], str(c["key"])] for c in choices], []))
        )

        input_prompt = "Select an Excel sheet to import from:\n"
        input_prompt += "".join([f"{c['key']}: {c['label']}\n" for c in choices])

        user_input = input(input_prompt)

        if user_input in allowed_keys:
            if user_input in extra_keys:
                for choice in [
                    e for e in extra_choices if user_input in e["allowed_keys"]
                ]:
                    choice["run"]()
            else:
                # user choice is an actual Zotero collections
                user_input = int(user_input)
                for c in choices:
                    if user_input == c["key"]:
                        fname = c["label"]
                        file_url = c["file_url"]
                break

    return fname, file_url


def generate_input_choices(sp_files, extra_choices=None):
    """
    Generate input keys and human-readable labels from raw SharePoint
    file data to offer to users in an interactive input dialogue.

    :param sp_files: list of Excel files
    :return: a list of dictionaries of input keys and labels
    """
    choices = list()

    for i, c in enumerate(sorted(sp_files, key=lambda a: a["Name"]), start=1):
        display_name = c["Name"]
        file_url = c["ServerRelativeUrl"]

        choices.append(
            {
                "key": i,
                "label": display_name,
                "file_url": file_url,
            }
        )

    if extra_choices:
        for e in extra_choices:
            choices.append(
                {
                    "key": e["primary_key"],
                    "label": e["label"],
                }
            )

    return choices


def fetch_sharepoint_files(s):
    """
    Fetch files from SharePoint.

    :param s: SharePoint connection object
    :return: all files found at given directory path
    """
    files = None
    sp_site = s.site

    sp_group = os.environ.get("SP_GROUP", None)
    sp_dir = os.environ.get("SP_DIRECTORY", None)

    while sp_group is None or sp_group == "":
        sp_group = os.environ.setdefault(
            "SP_GROUP",
            input(prompt="Enter SharePoint group:\n"),
        )

    while sp_dir is None or sp_dir == "":
        sp_dir = os.environ.setdefault(
            "SP_DIRECTORY",
            input(prompt="Enter SharePoint directory from which to fetch files:\n"),
        )

    sp_group = os.environ["SP_GROUP"] = quote(sp_group, safe="/:")
    sp_dir = os.environ["SP_DIRECTORY"] = quote(sp_dir, safe="/:")

    files_fetch_uri = f"https://{sp_site}/sites/{sp_group}/_api/web/GetFolderByServerRelativeUrl('{sp_dir}')/Files"

    try:
        files = s.get(files_fetch_uri).json()["d"]["results"]
    except Exception as e:
        print(e)
        print("Cannot log into SharePoint, sorry")

    return files


def fetch_file_data(s, sp_fname, sp_file_url):
    """
    Fetch data from an Excel file hosted on SharePoint.

    :param s: SharePoint connection object
    :param sp_fname: name of input file from SharePoint
    :param sp_file_url: url of input file on SharePoint
    :return: the requested file
    """
    sp_group = os.environ.get("SP_GROUP")
    sp_dir = os.environ.get("SP_DIRECTORY")

    source_file_by_name = f"https://{s.site}/sites/{sp_group}/_api/web/GetFolderByServerRelativeUrl('{sp_dir}')/Files('{sp_fname}')/$value"
    source_file_by_url = f"https://{s.site}/sites/{sp_group}/_api/web/GetFileByServerRelativeUrl('{sp_file_url}')/$value"

    return source_file_by_url


def import_file_data(s, in_fname, in_file_url, parse_data, out_fname=None, out_dir=None):
    """
    Import data from an Excel file.

    :param s: SharePoint connection object
    :param in_fname: name of input file on SharePoint
    :param in_file_url: url of input file on SharePoint
    :param out_fname: name of output file for subsequent parsing of data
    :param out_dir: name of directory which output file should get saved to
    :return: tuple of lists of successful and unsuccesful imports
    """
    in_file = fetch_file_data(s, sp_fname=in_fname, sp_file_url=in_file_url)

    if not out_dir:
        # save copy of input file to dir in which script is run by default
        out_dir = Path(__file__).parent.resolve()
    if not out_fname:
        out_fname = "dest_" + in_fname

    out_file = os.path.join(out_dir, out_fname)

    if not os.path.exists(out_file):
        # do not overwrite existing copies of import file
        s.getfile(in_file, filename=out_file)

    success, failure = parse_data(out_file)

    return success, failure
