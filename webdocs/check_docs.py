#!/usr/bin/env python
#

import sys
from os import walk
from ansible.utils import module_docs

def main():

    print "%s" % sys.argv[1]
    path=sys.argv[1]

    if path[-1] != '/':
        path = path + '/'

    all_docs = []
    errors = []
    for (dirpath, dirnames, ansible_modules) in walk(path):
        if dirpath == path:
            for mod in ansible_modules:
                try:
                    try:
                        doc, plainexamples, returndocs = module_docs.get_docstring(path+mod)
                    except ValueError:
                        doc, plainexamples = module_docs.get_docstring(path+mod)
                    except Exception as e:
                        print "error : %s" % str(e)

                    try:
                        examples_list = plainexamples.split('\n')
                        doc['examples'] = examples_list
                    except:
                        errors.append(doc)
                        errors.append('error-examples')
                        continue

                    all_docs.append(doc)
                except:
                    errors.append(mod)
                    errors.append('unknown')
                    continue

    print "results : %s" % all_docs
    print "errors : %s" % errors

if __name__ == '__main__':
  main()
