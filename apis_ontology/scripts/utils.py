"""
Helper functions useful for various data import scripts.
"""
import datetime


def secure_urls(url: str):
    """
    Convert insecure web addresses to secure ones by replacing
    the protocol part of the URL.

    :param url: the original, non-secure URL as a string
    :return: the converted URL, or None if the passed string doesn't
             start with http
    """
    if url.startswith("http:"):
        url = url.replace("http:", "https:")
    elif url.startswith("https:"):
        pass
    else:
        url = None

    return url


def get_xml_contents(file_path, xml_tag):
    """
    Helper function to search an XML file for a specific tag
    and to retrieve its (cleaned) contents.

    :param file_path: path to XML file to search
    :param xml_tag: XML tag to look for
    :return: a string containing the (stripped) contents of the XML tag,
             or None
    """
    contents = None
    try:
        tag = file_path.find(xml_tag)
        if tag.text and tag != "":
            contents = tag.text.strip()
    except Exception as e:
        print(e)

    return contents


def create_import_date_string(dt: datetime = None, separator="_"):
    """
    Create a human-readable date string based on either the current date
    and time or a user-provided datetime.

    :param dt: a datetime object, optional
    :param separator: word separator
    :return: string representation of
    """
    if not dt:
        dt = datetime.datetime.now()
    return dt.strftime(f"%Y%m%d{separator}%H%M%S")


def create_import_name(
    identifiers: list, import_source="Unknown_Source", separator="_"
):
    if isinstance(identifiers, str):
        identifiers = [identifiers]
    name_components = [i.strip().replace(" ", separator) for i in identifiers]

    return f"{import_source}{separator}{separator.join(name_components)}"


def convert_year_only_date(year: str):
    """
     Convert a YYYY date string to a date object.

    :param year: a YYYY-formatted date string
    :return: a date object
    """
    if year != "":
        publish_date = datetime.datetime.strptime(year, "%Y").date()
    else:
        publish_date = datetime.datetime.strptime("1111", "%Y").date()

    return publish_date


def clean_and_split_multivalue_string(str, separator):
    return [val.strip() for val in str.split(separator)]
