import os
import sharepy
import pandas as pd
from re import sub

from urllib.parse import quote as urlencode

# from urllib.parse import urlencode

# code for sharepoint connection taken from https://github.com/acdh-oeaw/shawi-data/blob/main/080_scripts_generic/080_01_ELAN2TEI/ELAN2TEI.ipynb
# the URL of the Sharepoint installation
sp_baseURL = "oeawacat.sharepoint.com"

# the sharepoint username + password are taken from the environment
sp_username = os.environ.get("SP_USERNAME")
sp_pwd = pwd = os.environ.get("SP_PWD")

# the name of the Sharepoint Site
sp_siteName = "ACDH-CH_p_Frischmuth"

# the name of the local directory where downloaded data will be stored
download_dir = "."

# the path to the Excel file
sp_XLSX_folder = "Shared%20Documents/Data"
dest_folder = urlencode("Shared Documents/Data/import")

input_file_name = "Namen, Orte, Siglen_Stand 8.5.2023"
# dest_file_name = f"{input_file_name}_log"
dest_file_name = "import_test_log"
dest_file_name2 = "import_test_log3"

sp_sample_filename = f"{input_file_name}.xlsx"
dest_file_path = urlencode(f"{dest_file_name}.txt")
dest_file_path2 = urlencode(f"{dest_file_name2}.txt")

filename = os.path.basename(sp_sample_filename)
download_path = f"{download_dir}/{filename}"


def run():
    # download_file = download_excel_from_sharepoint()
    # parse_excel()

    # with open(download_file, "r", encoding="utf-8") as file_obj:
    #     print(file_obj)

    input_file = write_log_file(dest_file_name)
    upload_test = upload_excel_to_sharepoint(input_file, dest_folder, dest_file_path)
    print(upload_test)

    upload_test = upload_excel_to_sharepoint(input_file, dest_folder, dest_file_path2)
    print(upload_test)


def download_excel_from_sharepoint():
    request_url = f"https://{sp_baseURL}/sites/{sp_siteName}/{sp_XLSX_folder}/{sp_sample_filename}"
    print(request_url)
    s = sharepy.connect(sp_baseURL, username=sp_username, password=sp_pwd)
    s.getfile(request_url, filename=download_path)
    return download_path


def write_log_file(fpath):
    # TODO replace placeholder text with actual log contents
    with open(fpath, "w") as f:
        f.write("Just a test log file...")

    return fpath


def upload_excel_to_sharepoint(input_file, dest_folder, dest_file_path):
    file_exists = False
    headers = {}

    with open(input_file, "rb") as f:
        data = f.read()
    content_length = os.path.getsize(input_file)
    # headers["Content-Length"] = bytes(content_length)
    # headers["Accept"] = "*/*"

    get_form_digest_value_url = (
        f"https://{sp_baseURL}/sites/{sp_siteName}/_api/contextinfo"
    )
    folder_url = f"https://{sp_baseURL}/sites/{sp_siteName}/_api/web/GetFolderByServerRelativeUrl('{dest_folder}')"
    all_files = f"https://{sp_baseURL}/sites/{sp_siteName}/_api/web/GetFolderByServerRelativeUrl('{dest_folder}')/Files"
    specific_file = f"https://{sp_baseURL}/sites/{sp_siteName}/_api/web/GetFolderByServerRelativeUrl('{dest_folder}')/Files('{dest_file_path}')/$value"
    get_file_by_url = f"https://{sp_baseURL}/sites/{sp_siteName}/_api/web/GetFileByServerRelativeUrl('{dest_folder}/{dest_file_path}')/$value"
    upload_new_file = f"https://{sp_baseURL}/sites/{sp_siteName}/_api/web/GetFolderByServerRelativeUrl('{dest_folder}')/Files/Add(url='{dest_file_path}', overwrite=true)"
    post_url = "https://{}/sites/{}/_api/web/GetFolderByServerRelativeUrl('Shared%20Documents/Data/import')/Files/add(url='{}',overwrite=true)"

    dest_path_combined = f"{dest_folder}/{dest_file_path}"

    s = sharepy.connect(sp_baseURL, username=sp_username, password=sp_pwd)

    post_r_a = s.post(get_form_digest_value_url)
    print("Digest: " + dest_folder)
    print(post_r_a.status_code)

    # resp_data = post_r_a.json()
    # form_digest_value = resp_data["d"]["GetContextWebInformation"]["FormDigestValue"]
    # post_url = "https://{}/sites/{}/_api/web/GetFolderByServerRelativeUrl('Shared%20Documents/Data/import')/Files/add(url='{}',overwrite=true)"
    post_r = s.post(
        upload_new_file,
        data=data,
        headers={
            "Content-Length": str(len(data)),
            # "X-RequestDigest": str(form_digest_value),
            "Authorization": "Bearer " + s.auth.digest,
        },
    )

    print("With digest: " + dest_folder)
    print(post_r.status_code)

    r = s.get(folder_url)
    print("Status folder: " + dest_folder)
    print(r.status_code)

    r = s.get(all_files)
    print("Get all files")
    print(r.status_code)

    # r = s.get(specific_file)
    # print("Get specific file: " + dest_file_path)
    # print(r.status_code)

    # if r.status_code == 200:
    #     exists = True
    #     # Check file is checked out to current user
    #     r = s.get(
    #         url + "GetFileByServerRelativeUrl('{}')/CheckedOutByUser".format(dest)
    #     )
    #     if "LoginName" in r.json()["d"]:
    #         user = re.sub(r"^.*\|", "", r.json()["d"]["LoginName"])
    #         if user != s.username:
    #             return False, "File checked out to " + user
    #     else:
    #         r = s.post(url + "GetFileByServerRelativeUrl('{}')/Checkout()".format(dest))
    #         if r.status_code != 200:
    #             return False, "File could not be checked out"
    #
    # if r.status_code == 200:
    #     print(f"File {dest_file_path} exists! Needs overwriting")
    #     headers["X-HTTP-Method"] = "PUT"
    #     r = s.post(get_file_by_url, data=data, headers=headers)
    # else:
    #     print(f"File {dest_file_path} does not exist yet... creating new.")
    #     r = s.post(
    #         upload_new_file,
    #         data=data,
    #         headers=headers,
    #     )

    print(r)
    print(r.url)
    print(r.headers)
    # print(r.raw)
    print(r.status_code)
    print(r.reason)

    #
    # print(dest_path_combined)
    #
    # # r = s.post(upload_url + f"GetFileByServerRelativeUrl('{output_file}')/Checkout()")
    # upload_url = f"https://{sp_baseURL}/sites/{sp_siteName}/_api/web/GetFolderByServerRelativeUrl('{dest_folder}')"
    #
    # combined_url = upload_url + f"GetFileByServerRelativeUrl('{dest_path_combined}')"
    #
    # r = s.get(combined_url)
    # print("Status file")
    # print(r.status_code)
    #
    # print("tryna read file...")
    #
    # with open(input_file, "rb") as f:
    #     data = f.read()
    # headers = {"content-length": len(data)}
    # #
    # # r = s.post(
    # #     upload_url
    # #     + f"GetFolderByServerRelativeUrl('{ouput_folder}')/Files/add(url='{output_file}',overwrite=true)",
    # #     data=data,
    # #     headers=headers,
    # # )
    #
    # print(r)


def old_upload_excel_to_sharepoint(input_file, log_file_path):
    upload_url = f"https://{sp_baseURL}/sites/{sp_siteName}/_api/web"
    s = sharepy.connect(sp_baseURL, username=sp_username, password=sp_pwd)

    # request_url = f"https://{sp_baseURL}/sites/{sp_siteName}/_api/web/{sp_XLSX_folder}/Files/{sp_sample_filename}"
    # url = "https://example.sharepoint.com/_api/web/GetFolderByServerRelativeUrl('{}')/Files/add(url='{}',overwrite=true)"

    # url = (
    #     f"https://{sp_baseURL}/sites/{sp_siteName}/{sp_XLSX_folder}/{remote_file_path}"
    # )
    # url = urlencode(url, safe="/:")

    folder = upload_folder
    print(folder)
    fpath = log_file_path
    dest_path = f"{folder}/{fpath}"

    exists = False

    # Verify folder exists on server
    r = s.get(upload_url + "GetFolderByServerRelativeUrl('{}')".format(folder))
    if r.status_code in [401, 403]:
        return False, "Access denied"
    elif r.status_code != 200:
        return False, "Folder '{}' does not exist on server".format(folder)
    else:
        # Check if file already exists
        r = s.get(upload_url + "GetFileByServerRelativeUrl('{}')".format(dest_path))
        if r.status_code == 200:
            exists = True
            # Check file is checked out to current user
            r = s.get(
                upload_url
                + "GetFileByServerRelativeUrl('{}')/CheckedOutByUser".format(dest_path)
            )
            if "LoginName" in r.json()["d"]:
                user = sub(r"^.*\|", "", r.json()["d"]["LoginName"])
                if user != s.username:
                    return False, "File checked out to " + user
            else:
                r = s.post(
                    upload_url
                    + "GetFileByServerRelativeUrl('{}')/Checkout()".format(dest_path)
                )
                if r.status_code != 200:
                    return False, "File could not be checked out"

        # Upload file to server
        with open(input_file, "rb") as f:
            data = f.read()
        headers = {"content-length": len(data)}
        if exists:
            headers["X-HTTP-Method"] = "PUT"
            r = s.post(
                upload_url
                + "GetFileByServerRelativeUrl('{}')/$value".format(dest_path),
                data=data,
                headers=headers,
            )
        else:
            r = s.post(
                upload_url
                + "GetFolderByServerRelativeUrl('{}')/Files/add(url='{}',overwrite=true)".format(
                    folder, fpath
                ),
                data=data,
                headers=headers,
            )
        if r.status_code in (200, 204):
            return True, "File uploaded successfully"
        else:
            if "error" in r.json():
                error = "\n" + r.json()["error"]["message"]["value"]
            else:
                error = ""
            return False, (
                "Upload failed. Status {}{}".format(str(r.status_code), error)
            )

    # print(input_file)
    # print(remote_file_path)
    # print(s)
    # print(url)
    #
    # file_data = {"file": open(input_file, "rb")}
    # r = s.post(url, data=file_data)
    # print(r)


def parse_excel():
    dl_path = download_path
    print(dl_path)

    # with open(dl_path, "r", encoding="utf-8") as file_obj:
    with open(dl_path, "rb") as file_obj:
        df = pd.read_excel(file_obj)

        # df = pd.read_csv(file_obj, encoding="unicode_escape")
        print(df)
        # print(file_obj)

    #
    # bla = pd.read_excel(dl_path)
    # print(bla)
