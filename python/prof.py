import re

#
# Common definitions.
#

prefix = '\[dv\/dt\]'
call_regex = 'cl[a-zA-Z]*?' # non-greedy
opts_regex = '[ \-\w_=]*'
iso_regex  = '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}' 
ptr_regex  = '0x[0-9a-fA-F]{1,8}'
int_regex  = '\d*'

#
# Parsers for API calls.
#

def match_clBuildProgram(output, result):
    call = 'clBuildProgram'

    # Arguments.
    result['program']    = re.search('%s %s %s (?P<program>%s)' % \
        (prefix, call, 'program', ptr_regex), output).group('program')
    result['options']    = re.search('%s %s %s (?P<options>%s)' % \
        (prefix, call, 'options', opts_regex), output).group('options')

    return result


def match_clCreateCommandQueue(output, result):
    call = 'clCreateCommandQueue'

    # Arguments.
    result['context']    = re.search('%s %s %s (?P<context>%s)' % \
        (prefix, call, 'context', ptr_regex), output).group('context')
    result['device']     = re.search('%s %s %s (?P<device>%s)'  % \
        (prefix, call, 'device', ptr_regex), output).group('device')
    result['properties'] = re.search('%s %s %s (?P<properties>%s)'   % \
        (prefix, call, 'properties', int_regex), output).group('properties')
    result['errcode']    = re.search('%s %s %s (?P<errcode>%s)' % \
        (prefix, call, 'errcode', ptr_regex), output).group('errcode')
    # Return value.
    result['queue']      = re.search('%s %s %s (?P<queue>%s)' % \
        (prefix, call, 'queue', ptr_regex), output).group('queue')

    return result


def match_clCreateKernel(output, result):
    call = 'clCreateKernel'

    # Arguments.
    result['program']    = re.search('%s %s %s (?P<program>%s)' % \
        (prefix, call, 'program', ptr_regex), output).group('program')
    result['kernel_name']= re.search('%s %s %s (?P<kernel_name>%s)' % \
        (prefix, call, 'kernel_name', opts_regex), output).group('kernel_name')
    result['errcode']    = re.search('%s %s %s (?P<errcode>%s)' % \
        (prefix, call, 'errcode', ptr_regex), output).group('errcode')

    return result


def match_clEnqueueNDRangeKernel(output, result):
    call = 'clEnqueueNDRangeKernel'

    # Arguments.
    result['queue']  = re.search('%s %s %s (?P<queue>%s)' % \
        (prefix, call, 'queue', ptr_regex), output).group('queue')
    result['kernel'] = re.search('%s %s %s (?P<kernel>%s)' % \
        (prefix, call, 'kernel', ptr_regex), output).group('kernel')
    result['offset'] = [int(i) for i in re.search('%s %s %s (?P<offset>%s)' % \
        (prefix, call, 'offset', '.*'), output).group('offset').split()]
    result['gws']    = [int(i) for i in re.search('%s %s %s (?P<gws>%s)' % \
        (prefix, call, 'gws', '.*'), output).group('gws').split()]
    result['lws']    = [int(i) for i in re.search('%s %s %s (?P<lws>%s)' % \
        (prefix, call, 'lws', '.*'), output).group('lws').split()]
    result['event_wait_list'] = re.search('%s %s %s (?P<event_wait_list>%s)' % \
        (prefix, call, 'event_wait_list', '.*'), output).group('event_wait_list').split()
    result['event']  = re.search('%s %s %s (?P<event>%s)' % \
        (prefix, call, 'event', ptr_regex), output).group('event')

    return result


# Map from API calls to parsers.
map_call_to_parser = {
    'clBuildProgram'         : match_clBuildProgram,
    'clCreateCommandQueue'   : match_clCreateCommandQueue,
    'clCreateKernel'         : match_clCreateKernel,
    'clEnqueueNDRangeKernel' : match_clEnqueueNDRangeKernel
}


# FIXME: The start and end matches are not all that special: they can happen after
# matches for arguments. Moreover, they may become optional in future.
def next_match(output):
    match = re.search('%s (?P<call>%s) start (?P<start>%s)' % (prefix, call_regex, iso_regex), output)
    if not match:
        return ('', {})

    result = {}
    result['call'] = match.group('call')
    result['start'] = match.group('start')
    parser = map_call_to_parser[result['call']]
    if not parser:
        raise Exception('OpenCL API call %s not supported!' % result['call'])
    result = parser(output, result)

    match = re.search('%s (?P<call>%s) end (?P<end>%s)' % (prefix, call_regex, iso_regex), output)
    if not match:
        return ('', {})
    result['end'] = match.group('end')

    return (output[match.end():], result)


def match(output):
    results = []
    (output, result) = next_match(output)
    while result:
        results.append(result)
        (output, result) = next_match(output)
    return results
