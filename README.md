# BtmonParser

A parser for btmon output.

## Installation

It is recommended to install BtmonParser using [pipx](https://pipx.pypa.io/stable/):

`pipx install git+https://github.com/JamesConlan96/BtmonParser`

## Usage

```
usage: btmonParser.py [-h]
                      [-f {asciidoc,double_grid,double_outline,fancy_grid,fancy_outline,github,grid,heavy_grid,heavy_outline,html,jira,latex,latex_booktabs,latex_longtable,latex_raw,mediawiki,mixed_grid,mixed_outline,moinmoin,orgtbl,outline,pipe,plain,presto,pretty,psql,rounded_grid,rounded_outline,rst,simple,simple_grid,simple_outline,textile,tsv,unsafehtml,youtrack}]
                      -i FILE [FILE ...] [-n] [-o FILE] [-r RSSIMIN]

A parser for btmon output

options:
  -h, --help            show this help message and exit
  -f, --format {asciidoc,double_grid,double_outline,fancy_grid,fancy_outline,github,grid,heavy_grid,heavy_outline,html,jira,latex,latex_booktabs,latex_longtable,latex_raw,mediawiki,mixed_grid,mixed_outline,moinmoin,orgtbl,outline,pipe,plain,presto,pretty,psql,rounded_grid,rounded_outline,rst,simple,simple_grid,simple_outline,textile,tsv,unsafehtml,youtrack}
                        format for output tables (default: github)
  -i, --inputFiles FILE [FILE ...]
                        btmon output files to parse
  -n, --noPrompt        overwrite existing output files without asking
  -o, --outFile FILE    file to save output to
  -r, --rssiMin RSSIMIN
                        minimum RSSI value a record must have to be included in the report
```