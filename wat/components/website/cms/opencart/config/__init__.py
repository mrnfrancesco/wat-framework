__provides__ = {
    # servers
    'HTTP_SERVER', 'HTTPS_SERVER',
    # directories
    'DIR_APPLICATION', 'DIR_SYSTEM', 'DIR_DATABASE',
    'DIR_LANGUAGE', 'DIR_TEMPLATE', 'DIR_CONFIG',
    'DIR_IMAGE', 'DIR_CACHE', 'DIR_DOWNLOAD', 'DIR_LOGS',
    # database
    'DB_DRIVER', 'DB_HOSTNAME', 'DB_USERNAME',
    'DB_PASSWORD', 'DB_DATABASE', 'DB_PREFIX'
}


def parse_configuration(file_content):
    import re
    regex = re.compile(r"define\('(?P<key>.+?)', '(?P<value>.+?)'\);")
    parameters = dict()
    for parameter in regex.finditer(file_content):
        parameters[parameter.group('key')] = parameter.group('value')
    return parameters