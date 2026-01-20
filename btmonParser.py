#!/usr/bin/env python


import argparse
import logging
from pathlib import Path
import sys
from tabulate import tabulate, tabulate_formats
import re
import yaml


logger = logging.getLogger(__name__)


class BtmonParser():
    """Btmon parser object"""

    def __init__(self) -> None:
        """Initialises a btmon parser object"""
        self.devices = {}
        logger.debug("Btmon parser initialised")

    def _addDeviceRecord(self, timestamp: str, mac: str, name: str,
                       manufacturer: str, rssi: str) -> None:
        """Adds or updates a data record
        @param timestamp: Timestamp for data collection
        @param mac: MAC address of device
        @param name: Name of device
        @param manufacturer: Manufacturer of device
        @param rssi: RSSI of device
        """
        mac = mac.strip().upper()
        if not mac:
            return
        timestamp = float(timestamp)
        rssi = int(rssi) if rssi else 5000
        if mac in self.devices:
            if timestamp < self.devices[mac]["firstTime"]:
                self.devices[mac]["firstTime"] = timestamp
            elif timestamp > self.devices[mac]["lastTime"]:
                self.devices[mac]["lastTime"] = timestamp
            if not self.devices[mac]["name"]:
                self.devices[mac]["name"] = name
            if not self.devices[mac]["manufacturer"]:
                self.devices[mac]["manufacturer"] = manufacturer
            if abs(rssi) < abs(self.devices[mac]["rssi"]):
                self.devices[mac]["rssi"] = rssi
        else:
            self.devices[mac] = {
                "firstTime": timestamp,
                "lastTime": timestamp,
                "name": name,
                "manufacturer": manufacturer,
                "rssi": rssi
            }

    def _yesNo(self, prompt: str) -> bool:
        """Prompts the user for a yes/no response
        @param prompt: Prompt to display to the user
        @return: True if yes, False if no
        """
        yn = input(f"{prompt} (y/n): ")
        if yn.lower() == 'y':
            return True
        elif yn.lower() == 'n':
            return False
        else:
            return self._yesNo(prompt)

    def parse(self, file: Path) -> None:
        """Parses an input file
        @param file: File to parse
        """
        file = file.resolve()
        logger.debug(f"Initiated parsing of input file '{file}'")
        try:
            with file.open('r', errors="replace") as f:
                timestamp = ""
                mac = ""
                name = ""
                manufacturer = ""
                rssi = ""
                for line in f.readlines():
                    line = line.rstrip()
                    if re.match(r'^\S', line):
                        self._addDeviceRecord(timestamp, mac, name,
                                              manufacturer, rssi)
                        timestamp = ""
                        mac = ""
                        name = ""
                        manufacturer = ""
                        rssi = ""
                        check = re.search(r'] (.+?)$', line)
                        if check is not None:
                            timestamp = check.group(1)
                            continue
                    else:
                        line = line.lstrip()
                        # MAC
                        check = re.match(r'^((LE )|(BR/EDR ))?Address: (.+?) ',
                                        line)
                        if check is not None:
                            mac = check.group(4)
                            continue
                        # Name
                        check = re.match(r'^Name \(complete\): (.+?)$', line)
                        if check is not None:
                            name = check.group(1)
                            continue
                        # Manufacturer
                        check = re.match(r'^Company: (.+?) \((.+?)\)$', line)
                        if check is not None:
                            manufacturer = check.group(1)
                            continue
                        # RSSI
                        check = re.match(r'^RSSI: (.+?) dBm', line)
                        if check is not None:
                            rssi = check.group(1)
                            continue
        except:
            raise
            error = "Could not parse file"
            logger.error(error)
            raise Warning(error)
        logger.debug(f"Parsing complete")

    def report(self, outFile: Path, format: str = "github",
               overwrite: bool = False) -> None:
        """Generates ouput files
        @param outFile: File to save output to
        @param format: Python-tabulate format for output tables
        @param overwrite: Whether or not to overwrite existing output file 
        without prompting the user
        """
        logger.debug("Initiated reporting")
        if not self.devices:
            logger.warning("No bluetooth devices to report on")
            return
        outFile = outFile.resolve()
        if outFile.exists() and not overwrite and not \
            self._yesNo(f"output file '{outFile}' exists, overwrite it?"):
            return
        try:
            outFile.parent.mkdir(parents=True, exist_ok=True)
            with outFile.open('w') as f:
                headings = ["MAC Address", "First Time", "Last Time",
                            "Common Name", "Manufacturer", "RSSI"]
                rows = []
                for mac in self.devices.keys():
                    row = [mac]
                    row.append(self.devices[mac]["firstTime"])
                    row.append(self.devices[mac]["lastTime"])
                    if self.devices[mac]["name"]:
                        row.append(self.devices[mac]["name"])
                    else:
                        row.append(mac)
                    if self.devices[mac]["manufacturer"]:
                        row.append(self.devices[mac]["manufacturer"])
                    else:
                        row.append("Unknown")
                    if abs(self.devices[mac]['rssi']) > 255:
                        row.append("Unknown")
                    else:
                        row.append(self.devices[mac]['rssi'])
                    rows.append(row)
                rows.sort(key=lambda x: f"{x[-1]} {x[0]}")
                f.write(tabulate(rows, headings, format))
                logger.debug(f"Bluetooth device report written to '{outFile}'")
        except:
            error = f"Could not write to output file '{outFile}'"
            logger.error(error)
            raise Warning(error)
        logger.debug("Reporting complete")

    def summarise(self) -> str:
        """Generates a summary of findings
        @return Summary of findings
        """
        return f"Total bluetooth devices identified: {len(self.devices)}"


def genArgParser() -> argparse.ArgumentParser:
    """Generates a CLI argument parser
    @return: CLI argument parser object
    """
    parser = argparse.ArgumentParser(description="A parser for btmon output")
    parser.add_argument('-f', '--format', choices=tabulate_formats,
                        help="format for output tables (default: github)",
                        default="github")
    parser.add_argument('-i', '--inputFiles', nargs='+', type=Path,
                        action="store", required=True, metavar="FILE",
                        help="btmon output files to parse")
    parser.add_argument('-n', '--noPrompt', action="store_true",
                        help="overwrite existing output files without asking")
    parser.add_argument('-o', '--outFile', type=Path, action="store",
                        help="file to save output to", metavar="FILE")
    return parser

def main(cliArgs: list = sys.argv) -> None:
    """Main method"""
    if len(cliArgs) == 1:
        genArgParser().print_usage()
        sys.exit()
    try:
        logHandlerStdout = logging.StreamHandler(sys.stdout)
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)-7s - " +
                    "%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[logHandlerStdout]
        )
        args = genArgParser().parse_args()
        bp = BtmonParser()
        for file in args.inputFiles:
            bp.parse(file)
        bp.report(args.outFile, args.format, args.noPrompt)
        print("\nParsing complete!\n", bp.summarise(), "", sep="\n")
    except Warning:
        sys.exit()
    except KeyboardInterrupt:
        logger.debug("Terminated by user")
        sys.exit()


if __name__ == "__main__":
    main()
