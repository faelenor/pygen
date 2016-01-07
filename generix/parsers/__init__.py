"""
Common parser methods.
"""

import os
import pkg_resources
import warnings

from ..exceptions import NoParserError


def get_parser_class_map():
    result = {}

    for entry_point in pkg_resources.iter_entry_points(
        group='generix_parsers',
    ):
        try:
            class_ = entry_point.load()
        except ImportError as ex:
            warnings.warn(
                "Exception while loading generix parser %r. It won't be "
                "available. Exception was: %s" % (entry_point.name, ex),
                RuntimeWarning,
            )
            continue

        for extension in class_.extensions:
            if extension in result:
                current_class = result[extension]

                if current_class != class_:
                    warnings.warn(
                        "Could not register extension %r with parser %r as it "
                        "is already registered with a different parser "
                        "(%r)." % (
                            extension,
                            class_,
                            current_class,
                        ),
                        RuntimeWarning,
                    )
            else:
                result[extension] = class_

    return result


parser_class_map = get_parser_class_map()


def get_parser_from_file(file):
    extension = os.path.splitext(file.name)[-1]
    parser_class = parser_class_map.get(extension)

    if not parser_class:
        raise NoParserError(
            filename=file.name,
            extensions=set(parser_class_map),
        )

    return parser_class()


def parse_files(*files):
    return [
        get_parser_from_file(file).load_from_file(file)
        for file in files
    ]


def merge_definitions(*definitions):
    return definitions[0]
