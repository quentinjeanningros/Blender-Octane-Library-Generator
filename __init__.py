# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Generate Catalogs from Selected Folders",
    "author": "Quentin JEANNINROS",
    "description": "Generate catalogs based on selected folders",
    "blender": (4, 0, 0),
    "version": (1, 0, 0),
    "category": "Generic",
}

from .interface import register_ui, unregister_ui

def register():
    register_ui()

def unregister():
    unregister_ui()

if __name__ == "__main__":
    register()