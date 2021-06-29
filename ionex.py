"""IONEX parser and handler."""


import re
import datetime

import numpy as np

from tecmap import TecMap


class IonexHandler:
    """Class to read IONEX file and store TEC maps extracted from the IONEX data."""

    def __init__(self, ionex_str=None):
        """Init the instance.

        IONEX file can be simply input as:
            with open(file_path) as f:
                ionex_handler = IonexHandler(f.read())

        Args:
            ionex_str ([str]): IONEX file stored as a string.
        """
        self.ionex_str = ionex_str

        self._tec_maps = self._get_tec_maps()

    @property
    def tec_maps(self):
        """Get all TEC maps from the file."""
        return self._tec_maps

    def get_tec_map(self, hour):
        """Get TEC map for a UTC hour."""
        if self.tec_maps is None:
            return None

        for tec_map in self.tec_maps:
            if tec_map.epoch.hour == hour:
                return tec_map
        return None

    def _get_tec_maps(self):
        """Get tec maps from IONEX file."""
        if self.ionex_str is None:
            return None

        return [
            self._parse_map(map_str)
            for map_str in self.ionex_str.split("START OF TEC MAP")[1:]
        ]

    def _parse_map(self, map_str, exponent=-1):
        """Parse a tec map

        Args:
            full_map_str ([str]): String representing the
            exponent (int, optional): Exponent to scale the TEC values. Defaults to -1.

        Returns:
            [TecMap]: [description]
        """
        # remove everything after end of map
        map_str = re.split(".*END OF TEC MAP", map_str)[0]

        # get epoch of the map
        epoch_str = re.split("EPOCH OF CURRENT", map_str)[0]
        epoch_list = np.fromstring(epoch_str, sep=" ", dtype=int)
        epoch_datetime = datetime.datetime(*epoch_list)

        # generate map array
        map_arr = (
            np.stack(
                [
                    np.fromstring(l, sep=" ")
                    for l in re.split(".*LAT/LON1/LON2/DLON/H\\n", map_str)[1:]
                ]
            )
            * 10 ** exponent
        )
        return TecMap(map_arr, epoch_datetime)