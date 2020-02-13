# Copyright (c) 2016, Universal Robots A/S,
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Universal Robots A/S nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL UNIVERSAL ROBOTS A/S BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import xml.etree.ElementTree as ET


class Recipe(object):
    """
      Class representing a recipe. 
      It has the following attributes.
      key: string. name of the recipe.
      names: list of strings. Name of the registers.
      types: list of strings. Type of the registers.
    """
    __slots__=['key', 'names', 'types']
    @staticmethod
    def parse(recipe_node):
        """
          Is like a constructor. Instantiates a new Recipe object.
        """
        rmd = Recipe()
        rmd.key = recipe_node.get('key')
        rmd.names = [f.get('name') for f in recipe_node.findall('field')]
        rmd.types = [f.get('type') for f in recipe_node.findall('field')]
        return rmd


class ConfigFile(object):
    """
      Class to load recipe from xml file.
    """
    def __init__(self, filename):
        """
          Parses the filename .xml into the variable tree.
          Then It creates a Recipe class for each tag recipe found in the
          .xml file.
          Finally, generates a dictionary where each instate of Recipe is
          accessed with the key attribute given to the recipe tag in the .xml
          file
        """
        self.__filename = filename
        tree = ET.parse(self.__filename)
# root has tag = rtde_config
        root = tree.getroot()
#root.findall() finds only elements with a tag which are direct children of root
        recipes = [Recipe.parse(r) for r in root.findall('recipe')]
        self.__dictionary = {r.key: r for r in recipes}
        
    def get_recipe(self, key):
        r = self.__dictionary[key]
        return r.names, r.types
