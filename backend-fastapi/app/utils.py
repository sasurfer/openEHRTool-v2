import base64
from app.backend_redis.myredis import get_redis_status
from datetime import datetime
import asyncio
from fastapi import Request
import json
from json_tools import diff
from lxml import etree
from typing import Any, Callable
import re
from app.xdiff import xdiff
import collections.abc


def getauth(username, password):
    message = username + ":" + password
    message_bytes = message.encode("ascii")
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode("ascii")
    auth = "Basic " + base64_message
    return auth


def setEHRbasepaths(input_url):
    """set base paths for EHRBase"""
    url_base = input_url + "rest/openehr/v1/"
    url_base_ecis = input_url + "rest/ecis/v1/"
    url_base_admin = input_url + "rest/admin/"
    url_base_management = input_url + "management/"
    url_base_status = input_url + "rest/status"
    return url_base, url_base_ecis, url_base_admin, url_base_management, url_base_status


def insertlogline(redis_client, line):
    if get_redis_status(redis_client) == "ok":
        now = datetime.now()
        timestamp = now.strftime("%Y/%m/%d-%H:%M:%S-")
        mykey = "log"
        try:
            redis_client.rpush(mykey, timestamp + line)
        except Exception as e:
            return "error:", e
    else:
        return "error: redis not initialized"


def check_event_loop_status():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        print("ok")
    else:
        print("Event loop is not running.")


def get_logger(request: Request):
    return request.app.state.logger


class EHRBaseVersion(Exception):
    def __init__(self, message="Error in parsing ehrbase version"):
        self.message = message
        super().__init__(self.message)


def compareEhrbaseVersions(runningversion, specificversion):
    if runningversion == "latest":
        return 1
    if not runningversion[-1].isdigit():
        raise EHRBaseVersion(code=400, message="Error in parsing ehrbase version")
    rv = runningversion.split(".")
    sv = specificversion.split(".")
    for r, s in zip(rv, sv):
        if int(r) > int(s):
            return 1
        elif int(r) < int(s):
            return 0


def composition_check(composition, composition_get, format):
    comparison_results = compare_compositions(composition, composition_get, format)
    ndiff = analyze_comparison(comparison_results, format)
    if ndiff > 0:
        return comparison_results
    else:
        return None


def compare_compositions(composition, composition_get, format):
    if format == "xml":
        return compare_xmls(composition, composition_get)
    else:  # json,structured,flat
        return compare_jsons(composition, composition_get)


def compare_xmls(firstxml, secondxml):
    origcompositiontree = etree.fromstring(firstxml)
    retrievedcompositiontree = etree.fromstring(secondxml)
    xml_parser = etree.XMLParser(
        remove_blank_text=True, remove_comments=False, remove_pis=False
    )
    firststring = etree.tostring(origcompositiontree)
    secondstring = etree.tostring(retrievedcompositiontree)
    firstxml = etree.fromstring(firststring, xml_parser)
    secondxml = etree.fromstring(secondstring, xml_parser)
    difference = xdiff(firstxml, secondxml)
    return difference


def compare_jsons(firstjson, secondjson):
    origcomposition = json.loads(firstjson)
    retrievedcomposition = json.loads(secondjson)
    origchanged = change_naming(origcomposition)
    retrchanged = change_naming(retrievedcomposition)
    one = flatten(origchanged)
    two = flatten(retrchanged)
    return json.dumps((diff(one, two)), indent=4)


def change_naming(myjson: json) -> json:
    """change naming convention on the json"""
    return change_dict_naming_convention(myjson, convertcase)


def flatten(d: dict, parent_key: str = "", sep: str = "_") -> dict:
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.abc.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def change_dict_naming_convention(
    d: Any, convert_function: Callable[[str], str]
) -> dict:
    """
    Convert a nested dictionary from one convention to another.
    Args:
        d (dict): dictionary (nested or not) to be converted.
        convert_function (func): function that takes the string in one convention and returns it in the other one.
    Returns:
            Dictionary with the new keys.
    """
    if not isinstance(d, dict):
        return d
    new = {}
    for k, v in d.items():
        new_v = v
        if isinstance(v, dict):
            new_v = change_dict_naming_convention(v, convert_function)
        elif isinstance(v, list):
            new_v = list()
            for x in v:
                new_v.append(change_dict_naming_convention(x, convert_function))
        new[convert_function(k)] = new_v
    return new


def convertcase(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def analyze_comparison(comparison_results, format):
    if format == "xml":
        return analyze_comparison_xml(comparison_results)
    else:
        return analyze_comparison_json(comparison_results)


def analyze_comparison_xml(comparison_results):
    ndifferences = 0
    for l in comparison_results:
        if "hunk" not in l[0]:
            continue
        else:
            if "<uid" in l[1]:  # uid
                continue
            elif "<value>" in l[1]:
                text1 = l[1].split("<value>")[1].split("</value>")[0]
                if text1.startswith("P"):
                    text2 = l[2].split("<value>")[1].split("</value>")[0]
                    if convert_duration_to_days(text1) == convert_duration_to_days(
                        text2
                    ):
                        continue
                ndifferences += 1
    return ndifferences


def analyze_comparison_json(comparison_results: list) -> int:
    ndifferences = 0
    for l in comparison_results:
        if "add" in l:
            if "_uid" in l["add"]:  # ignore if it is _uid
                continue
            else:
                ndifferences += 1
                print(f"difference add:{l['add']} value={l['value']}")
        elif "remove" in l:
            ndifferences += 1
            print(f"difference remove:{l['remove']} value={l['value']}")
        elif "replace" in l:
            if l["value"].endswith("Z") and l["value"][:3].isnumeric():
                if l["value"][:18] == l["prev"][:18]:
                    continue
                ndifferences += 1
                print(
                    f"difference replace:{l['replace']} value={l['value']} prev={l['prev']}"
                )
            elif (
                l["value"].startswith("P")
                and l["value"].endswith("D")
                and l["prev"].endswith("W")
            ):
                daysvalue = int(l["value"][1:-1])
                daysprev = int(l["prev"][1:-1])
                if daysvalue == daysprev:
                    continue
                ndifferences += 1
                print(
                    f"difference replace:{l['replace']} value={l['value']} prev={l['prev']}"
                )
            else:
                ndifferences += 1
                print(
                    f"difference replace:{l['replace']} value={l['value']} prev={l['prev']}"
                )
    return ndifferences


def convert_duration_to_days(duration_string):
    argument = duration_string[-1]
    duration = int(duration_string[1:-1])
    if argument == "D":
        return duration
    elif argument == "W":
        return 7 * duration
    elif argument == "Y":
        return 365 * duration
    else:
        return -1
