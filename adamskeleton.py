# Copyright (c) 2014 by Ladislav Lhotka, CZ.NIC <lhotka@nic.cz>
#
# Pyang plugin generating a sample XML instance document..
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""sample-xml-skeleton output plugin
This plugin takes a YANG data model and generates an XML instance
document containing sample elements for all data nodes.
* An element is present for every leaf, container or anyxml.
* At least one element is present for every leaf-list or list. The
  number of entries in the sample is min(1, min-elements).
* For a choice node, sample element(s) are present for each case.
* Leaf, leaf-list and anyxml elements are empty (exception:
  --sample-xml-skeleton-defaults option).
"""
import re

from pyang import plugin, statements, error
from pyang.util import unique_prefixes

def pyang_plugin_init():
    plugin.register_plugin(AdamRestPlugin())

class AdamRestPlugin(plugin.PyangPlugin):

    def add_opts(self, optparser):
        pass
    def add_output_format(self, fmts):
        self.multiple_modules = True
        fmts['adam-skeleton'] = self

    def setup_fmt(self, ctx):
        pass

    def emit(self, ctx, modules, fd):
        """Main control function.
        """

        self.doctype = 'data'
        if self.doctype not in ("config", "data"):
            raise error.EmitError("Unsupported document type: %s" %
                                  self.doctype)

        self.adam_node_handler = {
            "container": self.adam_container,
            "leaf": self.adam_leaf,
            "anyxml": self.adam_anyxml,
            "choice": self.adam_process_children,
            "case": self.adam_process_children,
            "list": self.adam_list,
            "leaf-list": self.adam_leaf_list,
            "rpc": self.adam_ignore,
            "action": self.adam_ignore,
            "notification": self.adam_ignore
        }
        for yam in modules:
            self.adam_process_children(yam,  '/' + yam.arg + ':' , yam.arg)

            for augmentation in  yam.search('augment'):
                self.process_augmentation(augmentation, yam.i_prefixes)

    def print_it(self, node, path, module_name):
        if node.i_config:
            mode = 'rw'
        else:
            mode = 'ro'
        # if path ends in :
        if path.endswith(':'):
            line = path + node.arg
        elif path.endswith(']'):
            line = path
        else:
            line = path + '/' + node.arg
        print mode + ' ' + line

    def process_augmentation(self, node, prefix_map):
        path = node.arg
        prefixes = set([p.split(':')[0] for p in path.split('/')])
        for prefix in prefixes:
            if prefix:
                replace = prefix_map[prefix][0]
                path = path.replace(prefix, replace)

        self.adam_process_children(node, path, node.arg)

    def adam_process_children(self, node, path, module):
        for ch in node.i_children:
            if ch.i_config or self.doctype == "data":
                self.adam_node_handler[ch.keyword](ch,path, module)

    def adam_container(self,node, path, module):
        self.print_it(node, path, module)
        if path.endswith(':'):
            path = path + node.arg
        else:
            path = path + '/' + node.arg

        self.adam_process_children(node,path, module)

    def adam_list(self, node, path, module):
        path += '/' + node.arg
        if node.search_one('key') is not None:
            keystr = "=[%s]" % re.sub('\s+', ' ', node.search_one('key').arg)
        path += keystr
        self.print_it(node, path, module)
        self.adam_process_children(node, path, module)

    def adam_leaf_list(self, node, path, module):
        #print "leaflist"
        self.print_it(node, path + '/' + node.arg, module)

    def adam_leaf(self, node, path, module):
        pass
    def adam_anyxml(self,node, path, module):
        pass
    def adam_ignore(self, node, path, module):
        pass
