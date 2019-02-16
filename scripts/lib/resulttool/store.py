# resulttool - store test results
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
import tempfile
import os
import subprocess
import json
import shutil
import scriptpath
scriptpath.add_bitbake_lib_path()
scriptpath.add_oe_lib_path()
import resulttool.resultutils as resultutils


def store(args, logger):
    tempdir = tempfile.mkdtemp(prefix='testresults.')
    try:
        results = {}
        logger.info('Reading files from %s' % args.source_dir)
        for root, dirs, files in os.walk(args.source_dir):
            for name in files:
                f = os.path.join(root, name)
                if name == "testresults.json":
                    resultutils.append_resultsdata(results, f)
                else:
                    dst = f.replace(args.source_dir, tempdir + "/")
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copyfile(f, dst)
        resultutils.save_resultsdata(results, tempdir)

        logger.info('Storing test result into git repository %s' % args.git_dir)
        subprocess.check_call(["oe-git-archive",
                               tempdir,
                               "-g", args.git_dir,
                               "-b", "{branch}",
                               "--tag-name", "{branch}/{commit_count}-g{commit}/{tag_number}",
                               "--commit-msg-subject", "Results of {branch}:{commit}",
                               "--commit-msg-body", "branch: {branch}\ncommit: {commit}"])
    finally:
        subprocess.check_call(["rm", "-rf",  tempdir])

    return 0

def register_commands(subparsers):
    """Register subcommands from this plugin"""
    parser_build = subparsers.add_parser('store', help='store test result files and directories into git repository',
                                         description='store the testresults.json files and related directories '
                                                     'from the source directory into the destination git repository '
                                                     'with the given git branch',
                                         group='setup')
    parser_build.set_defaults(func=store)
    parser_build.add_argument('source_dir',
                              help='source directory that contain the test result files and directories to be stored')
    parser_build.add_argument('git_dir',
                              help='the location of the git repository to store the results in')

