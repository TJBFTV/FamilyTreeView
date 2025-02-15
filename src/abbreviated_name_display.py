#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024-      ztlxltl
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#


import re
from typing import TYPE_CHECKING
import unicodedata

from gramps.gen.const import GRAMPS_LOCALE
from gramps.gen.display.name import (
    _CONNECTOR_IN_LIST, _F_FMT, _ORIGINMATRO, _ORIGINPATRO, _PREFIX_IN_LIST,
    _PRIMARY_IN_LIST, _SURNAME_IN_LIST, _TYPE_IN_LIST, PAT_AS_SURN,
    displayer as name_displayer, _make_cmp_key, cleanup_name
)

from family_tree_view_utils import make_hashable
if TYPE_CHECKING:
    from family_tree_view import FamilyTreeView


_ = GRAMPS_LOCALE.translation.gettext

def _raw_full_surname(raw_surn_data_list):
    """method for the 'l' symbol: full surnames"""
    result = []
    global PAT_AS_SURN
    nrsur = len(raw_surn_data_list)
    for raw_surn_data in raw_surn_data_list:
        if raw_surn_data[_PRIMARY_IN_LIST]:
            #if there are multiple surnames, return the primary. If there
            #is only one surname, then primary has little meaning, and we
            #assume a pa/matronymic should not be given as primary as it
            #normally is defined independently
            if not PAT_AS_SURN and nrsur == 1 and \
                    (raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO
                    or raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO):
                pass # add surname without "primary-"
            else:
                if len(result) > 0:
                    result += [" "]
                result += [
                    ("primary-prefix", raw_surn_data[_PREFIX_IN_LIST]),
                    " " if raw_surn_data[_PREFIX_IN_LIST] and raw_surn_data[_SURNAME_IN_LIST] else "",
                    ("primary-surname", raw_surn_data[_SURNAME_IN_LIST]),
                    " " if raw_surn_data[_SURNAME_IN_LIST] and raw_surn_data[_CONNECTOR_IN_LIST] else "",
                    ("primary-connector", raw_surn_data[_CONNECTOR_IN_LIST])
                ]
                continue # add surname only once
        if len(result) > 0:
            result += [" "]
        result += [
            ("prefix", raw_surn_data[_PREFIX_IN_LIST]),
            " " if raw_surn_data[_PREFIX_IN_LIST] and raw_surn_data[_SURNAME_IN_LIST] else "",
            ("surname", raw_surn_data[_SURNAME_IN_LIST]),
            " " if raw_surn_data[_SURNAME_IN_LIST] and raw_surn_data[_CONNECTOR_IN_LIST] else "",
            ("connector", raw_surn_data[_CONNECTOR_IN_LIST])
        ]
    return result

def _raw_primary_surname(raw_surn_data_list):
    """method for the 'm' symbol: primary surname"""
    global PAT_AS_SURN
    nrsur = len(raw_surn_data_list)
    for raw_surn_data in raw_surn_data_list:
        if raw_surn_data[_PRIMARY_IN_LIST]:
            #if there are multiple surnames, return the primary. If there
            #is only one surname, then primary has little meaning, and we
            #assume a pa/matronymic should not be given as primary as it
            #normally is defined independently
            if not PAT_AS_SURN and nrsur == 1 and \
                    (raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO
                    or raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO):
                return []
            else:
                result = [
                    ("prefix", raw_surn_data[_PREFIX_IN_LIST]),
                    " " if raw_surn_data[_PREFIX_IN_LIST] and raw_surn_data[_SURNAME_IN_LIST] else "",
                    ("surname", raw_surn_data[_SURNAME_IN_LIST]),
                    " " if raw_surn_data[_SURNAME_IN_LIST] and raw_surn_data[_CONNECTOR_IN_LIST] else "",
                    ("connector", raw_surn_data[_CONNECTOR_IN_LIST])
                ]
                return result
    return []

def _raw_primary_surname_only(raw_surn_data_list):
    """method to obtain the raw primary surname data, so this returns a string
    """
    global PAT_AS_SURN
    nrsur = len(raw_surn_data_list)
    for raw_surn_data in raw_surn_data_list:
        if raw_surn_data[_PRIMARY_IN_LIST]:
            if not PAT_AS_SURN and nrsur == 1 and \
                    (raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO
                    or raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO):
                return []
            else:
                return [("primary-surname", raw_surn_data[_SURNAME_IN_LIST])]
    return []

def _raw_primary_prefix_only(raw_surn_data_list):
    """method to obtain the raw primary surname data"""
    global PAT_AS_SURN
    nrsur = len(raw_surn_data_list)
    for raw_surn_data in raw_surn_data_list:
        if raw_surn_data[_PRIMARY_IN_LIST]:
            if not PAT_AS_SURN and nrsur == 1 and \
                    (raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO
                    or raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO):
                return []
            else:
                return [("primary-prefix", raw_surn_data[_PREFIX_IN_LIST])]
    return []

def _raw_primary_conn_only(raw_surn_data_list):
    """method to obtain the raw primary surname data"""
    global PAT_AS_SURN
    nrsur = len(raw_surn_data_list)
    for raw_surn_data in raw_surn_data_list:
        if raw_surn_data[_PRIMARY_IN_LIST]:
            if not PAT_AS_SURN and nrsur == 1 and \
                    (raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO
                    or raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO):
                return []
            else:
                return [("primary-connector", raw_surn_data[_CONNECTOR_IN_LIST])]
    return []

def _raw_patro_surname(raw_surn_data_list):
    """method for the 'y' symbol: patronymic surname"""
    for raw_surn_data in raw_surn_data_list:
        if (raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO or
            raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO):
            result = [
                    ("prefix", raw_surn_data[_PREFIX_IN_LIST]),
                    " " if raw_surn_data[_PREFIX_IN_LIST] and raw_surn_data[_SURNAME_IN_LIST] else "",
                    ("surname", raw_surn_data[_SURNAME_IN_LIST]),
                    " " if raw_surn_data[_SURNAME_IN_LIST] and raw_surn_data[_CONNECTOR_IN_LIST] else "",
                    ("connector", raw_surn_data[_CONNECTOR_IN_LIST])
                ]
            return result
    return []

def _raw_patro_surname_only(raw_surn_data_list):
    """method for the '1y' symbol: patronymic surname only"""
    for raw_surn_data in raw_surn_data_list:
        if (raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO or
            raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO):
            result = [("surname", raw_surn_data[_SURNAME_IN_LIST])]
            return result
    return []

def _raw_patro_prefix_only(raw_surn_data_list):
    """method for the '0y' symbol: patronymic prefix only"""
    for raw_surn_data in raw_surn_data_list:
        if (raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO or
            raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO):
            result = [("prefix", raw_surn_data[_PREFIX_IN_LIST])]
            return result
    return []

def _raw_patro_conn_only(raw_surn_data_list):
    """method for the '2y' symbol: patronymic conn only"""
    for raw_surn_data in raw_surn_data_list:
        if (raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO or
            raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO):
            result = [("connector", raw_surn_data[_CONNECTOR_IN_LIST])]
            return result
    return []

def _raw_nonpatro_surname(raw_surn_data_list):
    """method for the 'o' symbol: full surnames without pa/matronymic or
       primary
    """
    result = []
    for raw_surn_data in raw_surn_data_list:
        if ((not raw_surn_data[_PRIMARY_IN_LIST]) and
            raw_surn_data[_TYPE_IN_LIST][0] != _ORIGINPATRO and
            raw_surn_data[_TYPE_IN_LIST][0] != _ORIGINMATRO):
            if len(result) > 0:
                result += [" "]
            result += [
                ("prefix", raw_surn_data[_PREFIX_IN_LIST]),
                " " if raw_surn_data[_PREFIX_IN_LIST] and raw_surn_data[_SURNAME_IN_LIST] else "",
                ("surname", raw_surn_data[_SURNAME_IN_LIST]),
                " " if raw_surn_data[_SURNAME_IN_LIST] and raw_surn_data[_CONNECTOR_IN_LIST] else "",
                ("connector", raw_surn_data[_CONNECTOR_IN_LIST])
            ]
    return result

def _raw_nonprimary_surname(raw_surn_data_list):
    """method for the 'r' symbol: nonprimary surnames"""
    result = []
    for raw_surn_data in raw_surn_data_list:
        if not raw_surn_data[_PRIMARY_IN_LIST]:
            if len(result) > 0:
                result += [" "]
            result += [
                ("prefix", raw_surn_data[_PREFIX_IN_LIST]),
                " " if raw_surn_data[_PREFIX_IN_LIST] and raw_surn_data[_SURNAME_IN_LIST] else "",
                ("surname", raw_surn_data[_SURNAME_IN_LIST]),
                " " if raw_surn_data[_SURNAME_IN_LIST] and raw_surn_data[_CONNECTOR_IN_LIST] else "",
                ("connector", raw_surn_data[_CONNECTOR_IN_LIST])
            ]
    return result

def _raw_prefix_surname(raw_surn_data_list):
    """method for the 'p' symbol: all prefixes"""
    result = []
    global PAT_AS_SURN
    nrsur = len(raw_surn_data_list)
    for raw_surn_data in raw_surn_data_list:
        if raw_surn_data[_PRIMARY_IN_LIST]:
            if not PAT_AS_SURN and nrsur == 1 and \
                    (raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO
                    or raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO):
                pass
            else:
                if len(result) > 0:
                    result.append(" ")
                result.append(("primary-prefix", raw_surn_data[_PREFIX_IN_LIST]))
                continue
        if len(result) > 0:
            result.append(" ")
        result.append(("prefix", raw_surn_data[_PREFIX_IN_LIST]))
    return result

def _raw_single_surname(raw_surn_data_list):
    """method for the 'q' symbol: surnames without prefix and connectors"""
    result = []
    global PAT_AS_SURN
    nrsur = len(raw_surn_data_list)
    for raw_surn_data in raw_surn_data_list:
        if raw_surn_data[_PRIMARY_IN_LIST]:
            if not PAT_AS_SURN and nrsur == 1 and \
                    (raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINPATRO
                    or raw_surn_data[_TYPE_IN_LIST][0] == _ORIGINMATRO):
                pass
            else:
                if len(result) > 0:
                    result.append(" ")
                result.append(("primary-surname", raw_surn_data[_SURNAME_IN_LIST]))
                continue
        if len(result) > 0:
            result.append(" ")
        result.append(("surname", raw_surn_data[_SURNAME_IN_LIST]))
    return result


class AbbreviatedNameDisplay():
    def __init__(self, ftv: "FamilyTreeView"):
        self.ftv = ftv
        self.step_description = None

        self.ftv.uistate.connect("nameformat-changed", self.reset_cache)
        self.ftv.connect("abbrev-rules-changed", self.reset_cache)

        self.reset_cache()

    def reset_cache(self):
        self.cache = {}

    def get_num_for_name_abbrev(self, name):
        format_num_config_always = self.ftv._config.get("names.familytreeview-abbrev-name-format-always")
        format_num_config = self.ftv._config.get("names.familytreeview-abbrev-name-format-id")
        format_num_name = name.display_as
        if format_num_config_always:
            # always use num from config
            num = format_num_config
        else:
            if format_num_name == 0:
                # name: use default -> use num from config
                num = format_num_config
            else:
                # name: use specific -> use that
                num = format_num_name
        num = name_displayer._is_format_valid(num)
        return num

    def get_abbreviated_names(self, name, num=None, return_step_description=False, use_cached=True):
        """
        Returns a list of strings with abbreviations of the given name object.
        The returned list is ordered by decreasing name length.

        Rules are defined with FTV's configs.

        Prefixes which are part of a surname are not abbreviated (e.g. MacCarthy -> MacC., O'Brien -> O'B.)
        Given names, prefixes etc. are abbreviated step by step (examples with reverse=True: 
        Mary Ann -> Mary A. -> M. A., Mary-Ann -> Mary-A. -> M.-A., MaryAnn -> MaryA. -> M.A., van der -> van d. -> v. d.)
        """

        if return_step_description:
            use_cached = False

        hashable_name = make_hashable((name.serialize(), num))
        if use_cached and hashable_name in self.cache:
            return self.cache[hashable_name]

        self.step_description = []

        name_parts = self._get_name_parts(name, num=num)

        abbrev_name_list = []

        # full name
        full_name = self._name_from_parts(name_parts)
        abbrev_name_list.append(full_name)
        self.step_description.append((
            None, None, None, None, None, None, None,
            None, None,
            "full name"
        ))

        abbrev_rules = self.ftv._config.get("names.familytreeview-name-abbrev-rules")
        for rule_i, (action, name_part_types, reverse) in enumerate(abbrev_rules):
            for rule_step_i in range(1000):
                if not self._apply_rule_once(name_parts, action, name_part_types, reverse, rule_i, rule_step_i):
                    break
                abbrev_name_list.append(self._name_from_parts(name_parts))

        self.cache[hashable_name] = abbrev_name_list

        step_description = self.step_description
        self.step_description = None
        if return_step_description:
            return abbrev_name_list, step_description
        return abbrev_name_list

    def combine_abbreviated_names(self, fmt_str, names, nums=None, return_step_description=False, use_cached=True):
        """
        Returns a list of strings, each created by applying the
        abbreviated formatted names to the fmt_str (printf-style string
        formatting), while synchronizing the abbreviation steps. This is
        useful if the names are of different complexity (e.g. given
        names would be removed in the third abbreviation for one name
        and in the tenth abbreviation for the other).
        """

        try:
            fmt_str % tuple([""]*len(names))
        except TypeError:
            raise TypeError("Number of specifiers (printf-style string formatting) in fmt_str doesn't match the number of names")
        if nums is None:
            nums = [None]*len(names)
        else:
            try:
                assert len(names) == len(nums), "Number of nums doesn't match number of names"
            except TypeError:
                # one for all
                nums = [nums]*len(names)

        abbrev_names_lists = []
        step_descriptions_lists = []
        for i in range(len(names)):
            abbreviated_names, step_descriptions = self.get_abbreviated_names(names[i], num=nums[i], return_step_description=True, use_cached=use_cached)
            abbrev_names_lists.append(abbreviated_names)
            step_descriptions_lists.append(step_descriptions)

        # first is always full name
        abbrev_names_tuples = [tuple(l[0] for l in abbrev_names_lists)]
        combined_step_descriptions = [[l[0] for l in step_descriptions_lists]]

        abbrev_rules_applied = [[step[0] for step in l] for l in step_descriptions_lists]
        prev_abbrev_indices = [0]*len(names) # used full name (0)
        last_abbrev_indices = [len(abbrev_names)-1 for abbrev_names in abbrev_names_lists]
        abbrev_rules = self.ftv._config.get("names.familytreeview-name-abbrev-rules")
        for rule_i in range(len(abbrev_rules)):
            if not any(rule_i in rules for rules in abbrev_rules_applied):
                # This rule was not applied to any of the names.
                continue

            while True:
                # This rule can be applied if any of prev_abbrev_indices
                # can be increased while (still) pointing to this rule.
                rules_of_next_abbreviations = [
                    abbrev_rules_applied[name_i][
                        prev_abbrev_indices[name_i]+1
                    ]
                    for name_i in range(len(names))
                    if prev_abbrev_indices[name_i] != last_abbrev_indices[name_i]
                ]
                if (
                    rule_i not in rules_of_next_abbreviations
                    or all(
                        prev_abbrev_indices[name_i] == last_abbrev_indices[name_i]
                        for name_i in range(len(names))
                    ) # also break if we cannot increase any abbrev index
                ):
                    break

                cur_abbrev_names = []
                combined_step_description = []
                for name_i in range(len(names)):
                    if (
                        prev_abbrev_indices[name_i] != last_abbrev_indices[name_i]
                        and rule_i == abbrev_rules_applied[name_i][prev_abbrev_indices[name_i]+1]
                    ):
                        # The next abbreviated name uses this rule. Use
                        # it.
                        cur_abbrev_names.append(abbrev_names_lists[name_i][prev_abbrev_indices[name_i]+1])
                        combined_step_description.append(step_descriptions_lists[name_i][prev_abbrev_indices[name_i]+1])
                        prev_abbrev_indices[name_i] += 1
                        continue

                    # Reuse the last abbreviated name, other names have
                    # abbreviations to use (this was checked above).
                    cur_abbrev_names.append(abbrev_names_lists[name_i][prev_abbrev_indices[name_i]])
                    combined_step_description.append(step_descriptions_lists[name_i][prev_abbrev_indices[name_i]])
                abbrev_names_tuples.append(tuple(cur_abbrev_names))
                combined_step_descriptions.append(combined_step_description)

        # Actually applying the names to the format string.
        formatted_strings = [
            fmt_str % abbrev_names
            for abbrev_names in abbrev_names_tuples
        ]

        if return_step_description:
            return formatted_strings, combined_step_descriptions
        return formatted_strings

    def _get_name_parts(self, name, num=None):
        format_str = self._get_format_str(name, num=num)
        d = {
            "t": ("('title', title)","title", _("Person|title")),
            "f": ("('given', first, first, call)","given", _("given")), # first two times so one can be abbreviated and second can be checked for call afterwards
            "l": ("_raw_full_surname(raw_surname_list)", "surname", _("surname")),
            "s": ("('suffix', suffix)", "suffix", _("suffix")),
            "c": ("('call', call)", "call", _("Name|call")),
            "x": ("((('nick', nick) if nick else False) or (('call', call) if call else False) or ('given0', first.split(' ')[0]))", "common", _("Name|common")),
            "i": ("('initials', ''.join([word[0] +'.' for word in ('. ' + first).split()][1:]))", "initials", _("initials")),
            "m": ("_raw_primary_surname(raw_surname_list)", "primary", _("Name|primary")),
            "0m":("_raw_primary_prefix_only(raw_surname_list)", "primary[pre]", _("primary[pre]")),
            "1m":("_raw_primary_surname_only(raw_surname_list)", "primary[sur]",_("primary[sur]")),
            "2m":("_raw_primary_conn_only(raw_surname_list)", "primary[con]", _("primary[con]")),
            "y": ("_raw_patro_surname(raw_surname_list)", "patronymic", _("patronymic")),
            "0y":("_raw_patro_prefix_only(raw_surname_list)", "patronymic[pre]", _("patronymic[pre]")),
            "1y":("_raw_patro_surname_only(raw_surname_list)", "patronymic[sur]", _("patronymic[sur]")),
            "2y":("_raw_patro_conn_only(raw_surname_list)", "patronymic[con]", _("patronymic[con]")),
            "o": ("_raw_nonpatro_surname(raw_surname_list)", "notpatronymic", _("notpatronymic")),
            "r": ("_raw_nonprimary_surname(raw_surname_list)", "rest", _("Remaining names|rest")),
            "p": ("_raw_prefix_surname(raw_surname_list)", "prefix", _("prefix")),
            "q": ("_raw_single_surname(raw_surname_list)", "rawsurnames", _("rawsurnames")),
            "n": ("('nick', nick)", "nickname", _("nickname")),
            "g": ("('famnick', famnick)", "familynick", _("familynick")),
        }
        first = name.first_name
        surname_list = name.surname_list
        raw_surname_list = [surn.serialize() for surn in surname_list]
        suffix = name.suffix
        title = name.title
        call = name.call
        nick = name.nick
        famnick = name.famnick

        raw_display_name_parts = self._make_name_parts(format_str, d)
        # raw_display_name_parts item examples:
        #   ('nickname', '"', "('nick', nick)", '"')
        #   ('surname', '', '_raw_full_surname(raw_surname_list)', '')

        display_name_parts = []
        for i in range(len(raw_display_name_parts)):
            if isinstance(raw_display_name_parts[i], str):
                if len(raw_display_name_parts[i]) > 0:
                    display_name_parts.append(raw_display_name_parts[i])
            else:
                raw_res = eval(raw_display_name_parts[i][2])
                if isinstance(raw_res, tuple):
                    raw_res = [raw_res]
                res = []
                for res_part in raw_res:
                    if isinstance(res_part, str):
                        if len(res_part) > 0:
                            res.append(res_part)
                    else:
                        if len(res_part[1]) > 0:
                            res.append(res_part)
                display_name_parts.append([raw_display_name_parts[i][0], raw_display_name_parts[i][1], res, raw_display_name_parts[i][3]])
        # display_name_parts item example:
        #   ('nickname', '"', [('nick', 'Big Louie')], '"')
        #   ('surname', '', [('surname', 'Garner'), ' ', ('primary-prefix', 'von'), ' ', ('primary-surname', 'Zieliński')], '')

        return display_name_parts

    def _get_format_str(self, name, num=None):
        if num is None:
            num = name.display_as
        if num == 0:
            num = name_displayer.get_default_format()
        format_str = name_displayer.name_formats[num][_F_FMT]
        return format_str

    def _make_name_parts(self, format_str, d):
        """adapted from _make_fn"""

        if (len(format_str) > 2 and
            format_str[0] == format_str[-1] == '"'):
            pass
        else:
            d_keys = [(code, _tuple[2]) for code, _tuple in d.items()]
            d_keys.sort(key=_make_cmp_key, reverse=True) # reverse on length and by ikeyword
            for (code, ikeyword) in d_keys:
                exp, keyword, ikeyword = d[code]
                format_str = format_str.replace(ikeyword, "%"+ code)
                format_str = format_str.replace(ikeyword.title(), "%"+ code)
                format_str = format_str.replace(ikeyword.upper(), "%"+ code.upper())

        if (len(format_str) > 2 and
            format_str[0] == format_str[-1] == '"'):
            pass
        else:
            d_keys = [(code, _tuple[1]) for code, _tuple in d.items()]
            d_keys.sort(key=_make_cmp_key, reverse=True)
            for (code, keyword) in d_keys:
                exp, keyword, ikeyword = d[code]
                format_str = format_str.replace(keyword, "%"+ code)
                format_str = format_str.replace(keyword.title(), "%"+ code)
                format_str = format_str.replace(keyword.upper(), "%"+ code.upper())
        codes = list(d.keys()) + [c.upper() for c in d]
        if len(format_str) > 0 and format_str[0] == "!":
            patterns = ["%(" + ("|".join(codes)) + ")",]
            format_str = format_str[1:]
        else:
            patterns = [
                ",\\W*\"%(" + ("|".join(codes)) + ")\"",    # ,\W*"%s"
                ",\\W*\\(%(" + ("|".join(codes)) + ")\\)",  # ,\W*(%s)
                ",\\W*%(" + ("|".join(codes)) + ")",        # ,\W*%s
                "\"%(" + ("|".join(codes)) + ")\"",         # "%s"
                "_%(" + ("|".join(codes)) + ")_",           # _%s_
                "\\(%(" + ("|".join(codes)) + ")\\)",       # (%s)
                "%(" + ("|".join(codes)) + ")",             # %s
                ]

        pat = re.compile("|".join(patterns))
        res = []
        last_mat_end = 0
        mat = pat.search(format_str)
        while mat:
            if mat.start() > last_mat_end:
                res.append(format_str[last_mat_end:mat.start()])
            match_pattern = mat.group(0)
            p, code, s = re.split("%(.)", match_pattern)
            if code in "0123456789":
                code = code + s[0]
                s = s[1:]
            field = d[code.lower()][0]
            field_name = d[code.lower()][1]
            if code.isupper():
                field = ("["
                    "("
                        "part[0].upper(), "
                        "*part[1:]"
                    ") if isinstance(part, tuple) "
                    "else part " # This should only be a space or an empty string.
                    # There should only be strings (e.g. spaces) and list of tuples
                    # (list of tuples: 'surname', tuple which needs to be converted: 'given').
                    # A lambda is used so field doesn't have to be evaluated multiple times (e.g. if it's a function).
                    f"for part in (lambda x: [x] if isinstance(x, tuple) else x)({field})"
                "]")
            res.append((field_name, p, field, s))
            last_mat_end = mat.end()
            mat = pat.search(format_str, mat.end())
        return res

    def _name_from_parts(self, display_name_parts):
        all_caps_style = self.ftv._config.get("names.familytreeview-abbrev-name-all-caps-style")
        if all_caps_style == 0:
            style_fcn = _upper
        elif all_caps_style == 1:
            style_fcn = _fake_small_caps
        elif all_caps_style == 2:
            style_fcn = lambda names, **kwargs: _fake_small_caps(names, petite_caps=True, **kwargs)
        else:
            if all_caps_style == 3:
                style_tag = "b"
            elif all_caps_style == 4:
                style_tag = "i"
            elif all_caps_style == 5:
                style_tag = "u"
            style_fcn = lambda names, **kwargs: [f"<{style_tag}>"+name+f"</{style_tag}>" for name in names]
        name_str = ""
        for name_part in display_name_parts:
            if isinstance(name_part, str):
                name_str += name_part
            else:
                part_str = ""
                for sub_part in name_part[2]:
                    if isinstance(sub_part, str):
                        part_str += sub_part
                    else:
                        if sub_part[0].isupper():
                            prefix_possible = sub_part[0].lower() in ["surname", "primary-surname", "famnick"]
                            part_str += " ".join(
                                "-".join(
                                    "".join(style_fcn(
                                        _split_name_at_capital_letter(
                                            hysep_part,
                                            expect_prefix=prefix_possible
                                        ),
                                        all_but_first=prefix_possible
                                    ))
                                    for hysep_part in spsep_part.split("-")
                                )
                                for spsep_part in sub_part[1].split()
                            )
                        else:
                            part_str += sub_part[1]
                if part_str.strip() != "":
                    # This is equivalent to ifNotEmpty in NameDisplay.
                    part_str = name_part[1] + part_str + name_part[3]
                name_str += part_str

        clean_name_str = cleanup_name(name_str)

        return clean_name_str

    def _apply_rule_once(self, name_parts, action, name_part_types, reverse, rule_i, rule_step_i):
        if reverse:
            reversed_ = reversed
        else:
            reversed_ = lambda x: x

        for i, ii in self._iter_name_parts(name_parts, reverse):
            name_part_type = name_parts[i][2][ii][0].lower()
            if name_part_type not in name_part_types:
                if name_part_type == "given" and "given[ncnf]" in name_part_types:
                    name_part_type_opts = "ncnf"
                    call = name_parts[i][2][ii][3]
                else:
                    continue
            else:
                name_part_type_opts = ""
            is_given = name_part_type == "given" # special handling for 'given'
            spsep_parts = name_parts[i][2][ii][1].split()
            for j in reversed_(range(len(spsep_parts))):
                spsep_part = spsep_parts[j]
                if is_given:
                    # Check full (non-abbreviated) to check for actual call name.
                    spsep_parts_given_full = name_parts[i][2][ii][2].split()
                    if name_part_type_opts == "ncnf" and spsep_parts_given_full[j] == call:
                        # NOTE: Don't check for first since first can be hyphenated or a compound name without a separator.
                        # Skip call name.
                        continue
                hysep_parts = spsep_part.split("-")
                for k in reversed_(range(len(hysep_parts))):
                    hysep_part = hysep_parts[k]
                    if is_given:
                        # Check full (non-abbreviated) to check for actual call name.
                        hysep_parts_given_full = spsep_parts_given_full[j].split("-")
                        if name_part_type_opts == "ncnf" and hysep_parts_given_full[k] == call:
                            # NOTE: Don't check for first since first can be a compound name without a separator.
                            # Skip call name.
                            continue
                    if name_part_type in ["surname", "primary-surname", "famnick"]:
                        prefix, *upsep_parts_without_prefix = _split_name_at_capital_letter(hysep_part)
                    else:
                        # Only surnames have prefixes that need to be handled specially.
                        upsep_parts_without_prefix = _split_name_at_capital_letter(hysep_part, expect_prefix=False)
                        prefix = ""
                    for l in reversed_(range(len(upsep_parts_without_prefix))):
                        upsep_part_without_prefix = upsep_parts_without_prefix[l]
                        if is_given:
                            # Check full (non-abbreviated) to check for actual call name.
                            # Only surnames have prefixes that need to be handled specially.
                            upsep_parts_given_full = _split_name_at_capital_letter(hysep_parts_given_full[k], expect_prefix=False)
                            if name_part_type_opts == "ncnf" and (
                                upsep_parts_given_full[l] == call # call name
                                or (call == "" and j == 0 and k == 0 and l == 0) # no call and this is first
                            ):
                                # Skip call name and first name.
                                continue
                        if action == "abbrev":
                            if not upsep_part_without_prefix.isalpha():
                                # Ignore everything that's not a name or abbreviated name.
                                # TODO What about names with question marks etc.
                                continue
                            if (len(upsep_part_without_prefix) == 1):
                                # Can't abbreviate a one-letter name part or an abbreviated name.
                                continue
                            # Actual abbreviation:
                            upsep_parts_without_prefix[l] = upsep_part_without_prefix[0] + "."
                            hysep_parts[k] =  prefix + "".join(upsep_parts_without_prefix)
                            spsep_parts[j] = "-".join(hysep_parts)
                            if is_given:
                                name_parts[i][2][ii] = (name_parts[i][2][ii][0], " ".join(spsep_parts), name_parts[i][2][ii][2], name_parts[i][2][ii][3])
                            else:
                                name_parts[i][2][ii] = (name_parts[i][2][ii][0], " ".join(spsep_parts))
                        elif action == "remove":
                            upsep_parts_without_prefix.pop(l)
                            hysep_parts[k] = "".join(upsep_parts_without_prefix)
                            if len(hysep_parts[k]) == 0:
                                hysep_parts.pop(k)
                            spsep_parts[j] = "-".join(hysep_parts)
                            if len(spsep_parts[j]) == 0:
                                spsep_parts.pop(j)
                            if is_given:
                                upsep_parts_given_full.pop(l)
                                hysep_parts_given_full[k] = "".join(upsep_parts_given_full)
                                if len(hysep_parts_given_full[k]) == 0:
                                    hysep_parts_given_full.pop(k)
                                spsep_parts_given_full[j] = "-".join(hysep_parts_given_full)
                                if len(spsep_parts_given_full[j]) == 0:
                                    spsep_parts_given_full.pop(j)
                                name_parts[i][2][ii] = (name_parts[i][2][ii][0], " ".join(spsep_parts).strip(), " ".join(spsep_parts_given_full).strip(), name_parts[i][2][ii][3])
                            else:
                                name_parts[i][2][ii] = (name_parts[i][2][ii][0], " ".join(spsep_parts))

                        if action == "abbrev":
                            action_str = "abbreviate"
                            extra_str = "non-abbreviated "
                        elif action == "remove":
                            action_str = "remove"
                            extra_str = ""
                        if reverse:
                            last_or_first = "last"
                        else:
                            last_or_first = "first"
                        if len(name_part_types) == 1:
                            name_part_types_str = (
                                repr("given") + " (non-call or non-first)"
                                if name_part_types[0] == "given[ncnf]"
                                else repr(name_part_types[0])
                            )
                        else:
                            name_part_types_str = (
                                ", ".join(
                                    repr("given") + " (non-call or non-first)"
                                    if p == "given[ncnf]"
                                    else repr(p)
                                    for p in name_part_types[:-1]
                                )
                                + " or " + repr(name_part_types[-1]))
                        self.step_description.append((
                            rule_i, rule_step_i, i, ii, j, k, l,
                            name_parts[i][0], name_parts[i][2][ii][0],
                            f"{action_str} {last_or_first} {extra_str}{name_part_types_str}"
                        ))
                        return True
        return False

    def _iter_name_parts(self, name_parts, reverse=True):
        """Loop backwards ofer non-str items of name_parts.
        Yields i, ii for all useful name_parts[i][2][ii]
        """
        if reverse:
            reversed_ = reversed
        else:
            reversed_ = lambda x: x
        for i in reversed_(range(len(name_parts))):
            if isinstance(name_parts[i], str):
                continue
            for ii in reversed_(range(len(name_parts[i][2]))):
                if isinstance(name_parts[i][2][ii], str):
                    continue
                yield i, ii

def _split_name_at_capital_letter(name, expect_prefix=True):
    """splits names at capital letter
    "Abc" -> ("", "Abc") if handle_prefix else ("Abc",)
    "AbcDef" -> ("Abc", "Def")
    "O'Def" -> ("O'", "Def")
    "AbcDefGhi" -> ("Abc", "Def", "Ghi")
    """
    if len(name) == 0:
        return ["", ""] if expect_prefix else [""]
    if name.isupper() or name.islower() or all(not ch.isalpha() for ch in name):
        # All upper, all lower and all special characters cannot be separated.
        return ["", name] if expect_prefix else [name]
    upper_indices = [idx for idx in range(len(name)) if name[idx].isupper()]
    if len(upper_indices) == 0:
        return ["", name] if expect_prefix else [name]
    if upper_indices[0] == 0:
        if len(upper_indices) == 1:
            # no prefix
            return ["", name] if expect_prefix else [name]
        idx = upper_indices[1]
    else:
        if len(upper_indices) == 0:
            # this should not be reachable
            return ["", name] if expect_prefix else [name]
        idx = upper_indices[0]
    prefix = name[:idx]
    names = _split_name_at_capital_letter(name[idx:], expect_prefix=False)
    if not expect_prefix and prefix == "":
        return names
    return [prefix, *names]

def _upper(names, all_but_first=True, **kwargs):
    if all_but_first:
        return [names[0], *(name.upper() for name in names[1:])]
    else:
        return [name.upper() for name in names]

def _fake_small_caps(names, petite_caps=False, **kwargs):
    # Pango's <span variant="small-caps"> doesn't scale well when zooming the canvas and a Pango warning appears:
    # "failed to create cairo scaled font, expect ugly output. the offending font is ..."
    # This function creates fake small caps instead.
    small_caps_names = []
    for name in names:
        if len(name) == 0:
            continue

        # get char groups, equivalent to char_groups = re.findall(r'[^a-z]+|[a-z]+', name) but with all unicode Ll characters.
        char_groups = []
        group = ""
        for char in name:
            char_is_lowercase = unicodedata.category(char) == "Ll"
            if len(group) == 0:
                if char_is_lowercase:
                    # second group is first lowercase group
                    char_groups.append("")
                # new group
                group += char
                group_is_lowercase = char_is_lowercase
            elif char_is_lowercase == group_is_lowercase:
                group += char
            else:
                # end of group
                if len(group) > 0:
                    char_groups.append(group)
                # new group
                group = char
                group_is_lowercase = char_is_lowercase
        if len(group) > 0:
            # last group
            char_groups.append(group)

        for i in range(1, len(char_groups), 2): # every second group is lowercase
            if char_groups[i] == "":
                continue
            # Use these to see how it looks. It has wrong size when zoomed.
            # char_groups[i] = '<span variant="small-caps">' + char_groups[i] + "</span>"
            # char_groups[i] = '<span variant="petite-caps">' + char_groups[i] + "</span>"
            if petite_caps:
                char_groups[i] = "<small><small>" + char_groups[i].upper() + "</small></small>" # similar to petite caps
            else:
                char_groups[i] = "<small>" + char_groups[i].upper() + "</small>" # similar to small caps
        small_caps_names.append(''.join(char_groups))
    return small_caps_names