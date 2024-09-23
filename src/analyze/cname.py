from typing import List

cname_join = "."
desc_join = ".\n"


def join_cname(cname: str, *cname_parts: List[str]):
    return __join_str(cname_join, cname, *cname_parts)


def join_description(desc: str, *desc_parts: List[str]):
    return __join_str(desc_join, desc, *desc_parts)


def __join_str(join: str, cname: str, *cname_parts: List[str]):
    if not cname_parts:
        return cname

    cname_parts = [cname, *cname_parts]
    # Filter empty strings
    cname_parts = filter(lambda s: s, cname_parts)
    return join.join(cname_parts)
