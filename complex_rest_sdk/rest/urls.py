import re

reg = re.compile(r'<.+?:.+?>')


class Path:
    def __init__(self, url_pattern, view):
        self.pattern = self._change_filter_order(url_pattern)
        self.view = view

    @staticmethod
    def _change_filter_order(url_pattern):
        """
        Bottle format <name:type> but given <type:name>
        """
        def change_filter(match_object):
            type_and_name_str = match_object.group(0)
            type_str, name = type_and_name_str[1:-1].split(':')
            return f'<{name}:{type_str}>'
        return reg.sub(change_filter, url_pattern)


def path(url_pattern, view):
    return Path(url_pattern, view)

