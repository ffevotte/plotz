# This file is part of PlotZ, a plotting library
#
# Copyright (C) 2017
#   F. Févotte <fevotte@gmail.com>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

export PYTHONPATH=${PYTHONPATH}:"$(dirname $(readlink -f ${BASH_SOURCE[0]}))"
export JULIA_LOAD_PATH=${JULIA_LOAD_PATH}:"$(dirname $(readlink -f ${BASH_SOURCE[0]}))/PlotZ.jl/src"
export TEXINPUTS=${TEXINPUTS}:"$(dirname $(readlink -f ${BASH_SOURCE[0]}))"
