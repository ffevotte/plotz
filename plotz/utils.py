# -*- coding: utf-8 -*-
#
# This file is part of PlotZ, a plotting library
#
# Copyright (C) 2017
#   F. Févotte     <fevotte@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
# The GNU General Public License is contained in the file COPYING.

""" Utility functions for PlotZ """
#pylint: disable=invalid-name

import itertools
from plotz.backend import consumer

def ppfloat(x, fmt="%f"):
    """Return a pretty string representing the given float.
All useless trailing zeros are removed."""
    res = fmt % x
    if res.find(".") >= 0:
        while res.endswith("0"):
            res = res[0:len(res)-1]
        if res.endswith("."):
            res = res[0:len(res)-1]
    return res

def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(itertools.islice(iterable, n, None), default)

class Markers(object):
    """Built-in marker filters"""

    @staticmethod
    @consumer
    def always():
        """Marker filter that displays a marker for each data point"""
        while True:
            yield True

    @staticmethod
    @consumer
    def oneInN(N, start=0):
        """Marker filter that displays a marker for one data point in *N*

        Args:
          int N: period of the markers. One data points in *N* gets a marker.
          int start: index of the first data point to have a marker.
        """
        yield
        i = start
        while True:
            if i == 0:
                i = N
                yield True
            else:
                yield False
            i -= 1

    @staticmethod
    @consumer
    def equallySpaced(dX, start=0):
        """Marker filter that displays markers equally spaced (with respect to the *x* coordinate)

        Args:
          float dX: period of the markers. One marker gets displayed each time *x* advances by at
                    least *dX*.
          float start: abscissa of the first displayed marker.
        """
        ret = None

        while True:
            x, _ = yield ret
            if x >= start:
                ret = True
                start += dX
            else:
                ret = False
