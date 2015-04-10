#!/usr/bin/env python
import sys, re

sys.path.append('../python')
from prof_parser import prof_parse
from prof_parser import ptr_regex
from prof_parser import opts_regex

# Test info.
call = 'clCreateKernel'
id_  = ''
print '%s%s' % (call, id_)

# Parse test source.
source = {}
with open(call + id_ + '.c', 'r') as f:
    source['text'] = f.read()
    source['program'] = re.search('\(cl_program\) (?P<program>%s)' % ptr_regex, source['text']).group('program')
    source['name'] = re.search('kernel_name = \"(?P<name>%s)\"' % opts_regex, source['text']).group('name')
    # The following should match the assert statement.
    source['kernel'] = re.search('\(cl_kernel\) (?P<kernel>%s)' % ptr_regex, source['text']).group('kernel')

# Read from stdin (via pipe).
output = sys.stdin.read()
print 'OUTPUT'
print output

result = prof_parse(output)[0]
print 'RESULT'
print result
print

status = True
status &= (source['program'] == result['program'])
status &= (source['name'] == result['name'])
status &= (source['kernel'] == result['kernel'])

print '%s%s: %s' % (call, id_, 'PASSED' if status else 'FAILED')
print
