# MatchingPatternsTool

Main functionality -
1. Find/Replace regex-like patterns.
2. Matching bytes, by a given pattern.
3. Finding offsets of patterns in a binary file.

For each functionality it produced
JSON with the required results.

Generic run:
main.py -p <PATTERN> if <FILENAME>


EXAMPLES
Search for the hex bytes "C54C6BA5FEE1", "CDD0F08AE8" in the file some_file.bin:


python bin24.py -g {\"A54C6BA5FEE1\":\"value1\"\,\"BDD0F08AE8\":\"value3\} -f some_file.bin -r True

Will replace data in file and will also produce produce JSON, e.g:
`[
    {
        "Pattern": "A54C6BA5FEE1",
        "Start_offset": {
            "Decimal": "2307695617",
            "Hexadecimal": "898CA401"
        },
        "End_offset": {
            "Decimal": "2307695623",
            "Hexadecimal": "898CA407"
        }
    },
    {
        "Pattern": "BDD0F08AE8",
        "Start_offset": {
            "Decimal": "6161538689",
            "Hexadecimal": "16F419E81"
        },
        "End_offset": {
            "Decimal": "6161538694",
            "Hexadecimal": "16F419E86"
        }
    }
]`

You can Input patterns as a list
python bin24.py -z "FF64FF" "A4A5A6" "AE" -f my_file.bin

Will produce JSON, e.g:

`{
    "repeating_bytes": [
        {
            "range": [
                0,
                2
            ],
            "size": 2,
            "repeating_byte": "A4A5A6"
        },
        {
            "range": [
                8,
                10
            ],
            "size": 2,
            "repeating_byte": "AE"
        },
        {
            "range": [
                14,
                18
            ],
            "size": 4,
            "repeating_byte": "AEAE"
        },
        {
            "range": [
                23,
                25
            ],
            "size": 2,
            "repeating_byte": "AE"
        },
        {
            "range": [
                29,
                31
            ],
            "size": 2,
            "repeating_byte": "AE"
        }
    ]
}`
********

python bin24.py -g {\"C54C6BA5FEE1\":\"value1\"\,\"CDD0F08AE8\":\"value3\"} -f some_file.bin 

Will produce JSON, e.g:
`[
    {
        "Pattern": "C54C6BA5FEE1",
        "Start_offset": {
            "Decimal": "2307695617",
            "Hexadecimal": "898CA401"
        },
        "End_offset": {
            "Decimal": "2307695623",
            "Hexadecimal": "898CA407"
        }
    },
    {
        "Pattern": "CDD0F08AE8",
        "Start_offset": {
            "Decimal": "6161538689",
            "Hexadecimal": "16F419E81"
        },
        "End_offset": {
            "Decimal": "6161538694",
            "Hexadecimal": "16F419E86"
        }
    }
]
`

python main.py -z "/xaf" -f some_file.bin

will produce json with all the repeating bytes 

Will produce JSON, e.g:

`{
    "repeating_bytes": [
        {
            "range": [
                0,
                2
            ],
            "size": 2,
            "repeating_byte": "Af"
        },
        {
            "range": [
                8,
                10
            ],
            "size": 2,
            "repeating_byte": "af"
        },
        {
            "range": [
                14,
                18
            ],
            "size": 4,
            "repeating_byte": "af"
        },
        {
            "range": [
                23,
                25
            ],
            "size": 2,
            "repeating_byte": "af"
        },
        {
            "range": [
                29,
                31
            ],
            "size": 2,
            "repeating_byte": "af"
        }
    ]
}
`

Searches for the hexidecimal pattern "PA##TT##ERN" in some_file will produce 
JSON with values where ##=ANy valid char=.*
python main.py -p "PA##TT##ERN" some_file.bin

`[
"PATTERN",
PAA3TTA4EN",
...
]`

args optionS

Optional Arguments:
  -f FILE, --file FILE  file to read search pattern from
  -p PATTERN, --pattern PATTERN
                        a hexidecimal pattern to search for
 
  -r replace, --replace replace bin/hex with map vals
                        
  -z, --zlist          list of pattern to search
                    