# -*- coding: utf-8 -*-

# Copyright (C) 2025, Natalia Budzińska
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
"""This script initializes the plugin, making it known to QGIS."""

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load AttributeCopier class from file AttributeCopier.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .attribute_copier import AttributeCopier
    return AttributeCopier(iface)
