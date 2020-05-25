import re
import multiprocessing as mp
import json
from argparse import ArgumentParser
from sys import stdout
import sys
import os
import uuid

STDOUT = stdout

DESCRIPTION = ''  # noqa
__FILE_NAME_SUFFIX__ = '.json'
DIR_NAME = 'output_files'
BASE_FILE_NAME = uuid.uuid4()


def get_args():
    p = ArgumentParser(description=DESCRIPTION)
    p.add_argument('-z', '--patterns_list', nargs='+', help='<Required> Set flag', required=False, default=[])
    p.add_argument('-g', '--patterns_map', type=json.loads)
    p.add_argument('-r', '--replace', type=bool, default=False)
    p.add_argument('-f', '--file', type=str, metavar='FILE', dest='file_read', help='file to search pattern from')
    p.add_argument(
        '-p', '--pattern', type=str, metavar='PATTERN',
        dest='ppattern',
        help='a hexidecimal pattern to search for'
    )
    return p.parse_args()


class HandlePatterns():
    def __init__(self, args):
        self.matched_patterns = []
        if args.file_read:
            self.file_name = args.file_read
        if args.patterns_map:
            self.patterns_from_user = args.patterns_map

            pool = mp.Pool(processes=len(args.patterns_map.keys()))
            pool.map(self.find_pattern, args.patterns_map.keys())
            if args.replace:
                self.replace_patterns()
        if args.patterns_list:
            repeat_pattern = args.patterns_list[0]
            if repeat_pattern[:2] == "/x":
                repeat_pattern = repeat_pattern[2:]
            self.search_byte(repeat_pattern)

    @classmethod
    def input_to_pattern(cls, pattern):
        initial_input = pattern
        pattern = [p for p in pattern.split("##")]
        pattern = [bytes.fromhex(p) for p in pattern]
        len_pattern = len(b"?".join(pattern))
        pattern = [re.escape(p) for p in pattern]
        pattern = b".".join(pattern)
        regex = re.compile(pattern, re.DOTALL + re.MULTILINE)
        return {
            'len_pattern': len_pattern,
            'regex': regex,
            'pattern_from_user': initial_input,
        }

    def replace_patterns(self):
        for key, val in self.patterns_from_user.items():
            file = open(self.file_name, 'rb')
            save_to_replace = file.read()
            file.close()
            to_replace = bytearray.fromhex(key)
            new = bytearray.fromhex(val)
            save_to_replace = save_to_replace.replace(to_replace, new)
            file_open_replace = open(self.file_name, 'wb')
            file_open_replace.write(save_to_replace)
            file_open_replace.close()

    def search_match_in_row(self, pattern, match_start, match_end):
        return {
            "Pattern": ("%s" % pattern),
            "Start_offset": {
                "Decimal": ("%d" % (match_start)),
                "Hexadecimal": ("%X" % (match_start)),
            },
            "End_offset": {
                "Decimal": ("%d" % (match_end)),
                "Hexadecimal": ("%X" % (match_end)),
            }
        }

    def find_pattern(self, pattern):
        end = 0
        fh_name = self.file_name
        fh_read = open(fh_name, 'rb')
        origin_pattern = pattern
        pattern = [p for p in pattern.split("##")]
        pattern = [bytes.fromhex(p) for p in pattern]

        bsize = len(b"".join(pattern)) * 2
        bsize = max(bsize, 2 ** 23)

        len_pattern = len(b"?".join(pattern))
        read_size = bsize - len_pattern

        pattern = [re.escape(p) for p in pattern]
        pattern = b".".join(pattern)

        regex_search = re.compile(pattern, re.DOTALL + re.MULTILINE).search
        offset = 0
        try:
            buffer = fh_read.read(len_pattern + read_size)
            match = regex_search(buffer)
            match = -1 if match is None else match.start()
            while True:
                if match == -1:
                    offset += read_size
                    if end and offset > end:
                        return
                    buffer = buffer[read_size:]
                    buffer += fh_read.read(read_size)
                    match = regex_search(buffer)
                    match = -1 if match is None else match.start()
                else:
                    if match == -1 and offset + match > end:
                        return
                    find_offset = offset + match

                    self.matched_patterns.append(
                        self.search_match_in_row(
                            origin_pattern, find_offset, find_offset + len_pattern,
                        )
                    )

                    match = regex_search(buffer, match + 1)
                    match = -1 if match is None else match.start()
                if len(buffer) <= len_pattern:
                    if not os.path.exists(DIR_NAME):
                        os.makedirs(DIR_NAME)
                    file_name_unique = os.path.join(DIR_NAME, str(BASE_FILE_NAME) + __FILE_NAME_SUFFIX__)
                    with open(file_name_unique, 'w', encoding='utf-8') as file_to_write:
                        json.dump(self.matched_patterns, file_to_write, ensure_ascii=False, indent=4)
                    return
        except Exception as e:
            sys.stdout.write('Format input to pattern failed, Error: {} \n'.format(e.__repr__()));
            sys.stdout.flush()

    def read_in_chunks(self, fileObj, chunkSize=1024):
        while True:
            data = fileObj.read(chunkSize)
            if not data:
                break
            yield data

    def search_byte(self, byte_to_find):
        base_filename = uuid.uuid4()
        file_name_unique = os.path.join(DIR_NAME, str(base_filename) + __FILE_NAME_SUFFIX__)

        format_byte = "({})".format(byte_to_find) + "\\1*"
        regex = re.compile(format_byte)

        data = dict(repeating_bytes=[])
        iter_start_point = 0

        file_to_read = open(self.file_name, 'rb')
        for chuck in self.read_in_chunks(file_to_read):
            iter_chunk = regex.finditer(chuck.hex())
            for it in iter_chunk:
                start_point = (int(it.start() / 2) + (32 * iter_start_point))
                if byte_to_find != it.group():
                    data['repeating_bytes'].append(
                        dict(range=(
                            start_point,
                            start_point + int(len(it.group()) / 2) - 1),
                            repeating_byte=it.group(),
                        ),
                    )
            iter_start_point += 32
        file_to_read.close()

        if not os.path.exists(DIR_NAME):
            os.makedirs(DIR_NAME)
        with open(file_name_unique, 'w') as outfile:
            json.dump(data, outfile, indent=4)


if __name__ == "__main__":
    args1 = get_args()
    patterns_obj = HandlePatterns(args1)
