# resulttool - merge multiple testresults.json files into a file or directory
#
# Copyright (c) 2019, Intel Corporation.
# Copyright (c) 2019, Linux Foundation
#
# This program is free software; you can redistribute it and/or modify it
# under the terms and conditions of the GNU General Public License,
# version 2, as published by the Free Software Foundation.
#
# This program is distributed in the hope it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
import os
import json
import resulttool.resultutils as resultutils

def merge(args, logger):
    # FIXME Add -t support for  args.target_result_id

    if os.path.isdir(args.target_result_file):
        results = resultutils.load_resultsdata(args.target_result_file, configmap=resultutils.store_map)
        resultutils.append_resultsdata(results, args.base_result_file, configmap=resultutils.store_map)
        resultutils.save_resultsdata(results, args.target_result_file)
    else:
        results = resultutils.load_resultsdata(args.base_result_file, configmap=resultutils.flatten_map)
        if os.path.exists(args.target_result_file):
            resultutils.append_resultsdata(results, args.target_result_file, configmap=resultutils.flatten_map)
        resultutils.save_resultsdata(results, os.path.dirname(args.target_result_file), fn=os.path.basename(args.target_result_file))

    return 0

def register_commands(subparsers):
    """Register subcommands from this plugin"""
    parser_build = subparsers.add_parser('merge', help='merge test results',
                                         description='merge results from multiple files',
                                         group='setup')
    parser_build.set_defaults(func=merge)
    parser_build.add_argument('base_result_file',
                              help='base result file provide the base result set')
    parser_build.add_argument('target_result_file',
                              help='target result file provide the target result set for merging into the '
                                   'base result set')
    parser_build.add_argument('-t', '--target-result-id', default='',
                              help='(optional) default merge all result sets available from target to base '
                                   'unless specific target result id was provided')

