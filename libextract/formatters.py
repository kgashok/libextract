"""
    libextract.formatters
    ~~~~~~~~~~~~~~~~~~~~~

    Formats the results of extraction into serializable
    representations, e.g. JSON, text.
"""

from functools import partial
from libextract.xpaths import FILTER_TEXT


UNLIMITED = float('NaN')


def get_text(node):
    """
    Gets the text contained within the children node
    of a given *node*, joined by a space.
    """
    return ' '.join(node.xpath(FILTER_TEXT))


def split_node_attr(node, attr):
    """
    Given a *node*, split the *attr* of the node
    into a list of strings, suitable for id/class
    handling.
    """
    return (node.get(attr) or '').split()


get_node_id = partial(split_node_attr, attr='id')
get_node_class = partial(split_node_attr, attr='class')


def node_json(node, depth=0):
    """
    Given a *node*, serialize it and recursively
    serialize it's children to a given *depth*.
    Note that if the *depth* runs out (goes to 0),
    the children key will be ``None``.
    """
    return {
        'xpath': node.getroottree().getpath(node),
        'class': get_node_class(node),
        'text': node.text,
        'tag': node.tag,
        'id': get_node_id(node),
        'children': (
            [node_json(n, depth-1) for n in node] if depth else None
        ),
    }


def chunks(iterable, size):
    """
    Yield successive chunks of *size* from a
    given *iterable*.
    """
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []


def get_table_headings(node):
    for elem in node.iter('th'):
        yield ' '.join(elem.text_content().split())


def get_table_data(node):
    for elem in node.iter('td'):
        yield ' '.join(elem.text_content().split())


def table_json(node):
    """
    Given a table *HtmlElement* (ie. <table>), return
    a dict, with the headings as keys and the subsequent
    lists contain table rows of data
    """
    rows = get_table_data
    headings = list(get_table_headings(node))
    num_of_keys = len(headings)
    return {heading: [row[column] for row in chunks(rows(node), num_of_keys)]
            for column, heading in enumerate(headings)}


def table_list(node):
    """
    Given a table *HtmlElement* (ie. <table>), return
    a list of lists, where the first list contains the
    table headings, and the subsequent lists contain table
    rows of data
    """
    headings = list(get_table_headings(node))
    data = get_table_data(node)
    table = [headings]
    table.extend(chunks(data, len(headings)))
    return table


def ul_ol_list(node):
    """
    Given an un/ordered list *HtmlElement* (ie. <ul>|<ol>),
    return a list, where the first item may be the id or class
    of the node, and the subsequent items contain the inner text
    of the list
    """
    list_name = get_node_id(node) or get_node_class(node)
    if list_name:
        yield list_name
    for elem in node.iter('li'):
        yield elem.text_content()
