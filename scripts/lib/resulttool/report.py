# test result tool - report text based test results
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
import glob
import json
from resulttool.resultutils import checkout_git_dir
import resulttool.resultutils as resultutils

class ResultsTextReport(object):

    def get_aggregated_test_result(self, logger, testresult):
        test_count_report = {'passed': 0, 'failed': 0, 'skipped': 0, 'failed_testcases': []}
        result_types = {'passed': ['PASSED', 'passed'],
                        'failed': ['FAILED', 'failed', 'ERROR', 'error', 'UNKNOWN'],
                        'skipped': ['SKIPPED', 'skipped']}
        result = testresult.get('result', [])
        for k in result:
            test_status = result[k].get('status', [])
            for tk in result_types:
                if test_status in result_types[tk]:
                    test_count_report[tk] += 1
            if test_status in result_types['failed']:
                test_count_report['failed_testcases'].append(k)
        return test_count_report

    def print_test_report(self, template_file_name, test_count_reports):
        from jinja2 import Environment, FileSystemLoader
        script_path = os.path.dirname(os.path.realpath(__file__))
        file_loader = FileSystemLoader(script_path + '/template')
        env = Environment(loader=file_loader, trim_blocks=True)
        template = env.get_template(template_file_name)
        havefailed = False
        reportvalues = []
        cols = ['passed', 'failed', 'skipped']
        maxlen = {'passed' : 0, 'failed' : 0, 'skipped' : 0, 'result_id': 0, 'testseries' :0 }
        for line in test_count_reports:
            total_tested = line['passed'] + line['failed'] + line['skipped']
            vals = {}
            vals['result_id'] = line['result_id']
            vals['testseries'] = line['testseries']
            vals['sort'] = line['testseries'] + "_" + line['result_id']
            for k in cols:
                vals[k] = "%d (%s%%)" % (line[k], format(line[k] / total_tested * 100, '.0f'))
            for k in maxlen:
                if len(vals[k]) > maxlen[k]:
                    maxlen[k] = len(vals[k])
            reportvalues.append(vals)
            if line['failed_testcases']:
                havefailed = True
        output = template.render(reportvalues=reportvalues,
                                 havefailed=havefailed,
                                 maxlen=maxlen)
        print(output)

    def view_test_report(self, logger, source_dir, git_branch):
        if git_branch:
            checkout_git_dir(source_dir, git_branch)
        test_count_reports = []
        testresults = resultutils.load_resultsdata(source_dir)
        for testsuite in testresults:
            for resultid in testresults[testsuite]:
                result = testresults[testsuite][resultid]
                test_count_report = self.get_aggregated_test_result(logger, result)
                test_count_report['testseries'] = result['configuration']['TESTSERIES']
                test_count_report['result_id'] = resultid
                test_count_reports.append(test_count_report)
        self.print_test_report('test_report_full_text.txt', test_count_reports)

def report(args, logger):
    report = ResultsTextReport()
    report.view_test_report(logger, args.source_dir, args.git_branch)
    return 0

def register_commands(subparsers):
    """Register subcommands from this plugin"""
    parser_build = subparsers.add_parser('report', help='report test result summary',
                                         description='report text-based test result summary from the source directory',
                                         group='analysis')
    parser_build.set_defaults(func=report)
    parser_build.add_argument('source_dir',
                              help='source directory that contain the test result files for reporting')
    parser_build.add_argument('-b', '--git-branch', default='',
                              help='(optional) default assume source directory contains all available files for '
                                   'reporting unless a git branch was provided where it will try to checkout '
                                   'the provided git branch assuming source directory was a git repository')
