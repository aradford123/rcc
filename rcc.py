#!/usr/bin/env python
from __future__ import print_function
import requests
from requests.auth import HTTPBasicAuth
import sys
import os
import json
from argparse import ArgumentParser
# silence warning for Self-signed cert
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import logging
import yaml
import pyang
import os
from pyang import plugin
from adamskeleton import pyang_plugin_init
MODELS="models"

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# = logging.getLogger('rcc')


def print_response(response, doyaml):
    if response.headers['Content-Type'] == 'application/yang':
        print (response.text)
    else:
        if doyaml:
            print(yaml.safe_dump(response.json(), default_flow_style=False))
        else:
            print (json.dumps(response.json(),indent=2))

def explore_all(args, filter):
    capabilities = get_capabilities(args)
    count = len(capabilities.split('n'))
    logging.info("Total files {}".format(count))
    repos = pyang.FileRepository(MODELS, no_path_recurse=False)
    ctx = pyang.Context(repos)
    modules = []
    for capability in capabilities.split('\n'):
        parts = capability.split('/')
        if len(parts) == 2:
            target = '{}/{}'.format(MODELS, parts[1])
        else:
            target = '{}/{}'.format(MODELS, capability)
        if  os.path.isfile(target):
            logging.info('READING {}'.format(capability))
            with open(target, "r") as f:
                data = f.read()
                name = target.split(',')[0]
                modules.append(ctx.add_module(name, data))
    pyang_plugin_init()
    fmts = {}
    for p in plugin.plugins:
        p.add_output_format(fmts)
    emit_obj = fmts['adam-skeleton']
    emit_obj.emit(ctx, modules, filter, 10)

def explore(data, url):
    repos = pyang.FileRepository(MODELS, no_path_recurse=False)
    ctx = pyang.Context(repos)

    name = url.split('/')[-1]

    module = ctx.add_module(name, data)
    pyang_plugin_init()
    fmts = {}
    for p in plugin.plugins:
        p.add_output_format(fmts)
    emit_obj = fmts['adam-skeleton']
    emit_obj.emit(ctx, [module], '', 10)

def run_post(args):
    BASE = 'https://{}:{}{}'.format(args.host, args.port, args.url)
    logging.info('POST URL {}'.format(BASE))

    headers = {'content-type': 'application/yang-data+json'}
    logging.info('requesting headers {}'.format(headers))
    # autodetect json or yaml
    with open(args.body) as config_data:
        if 'yaml' in args.body:
            body = yaml.load(config_data)
        else:
            body = json.load(config_data)
    logging.info('body:{}'.format(json.dumps(body)))
    response = requests.post(url=BASE,
                            headers=headers,
                            data = json.dumps(body),

                            auth=HTTPBasicAuth(args.username, args.password),
                            verify=False)
    if response.status_code == 409:
        print(json.dumps(response.json(),indent=2))

    response.raise_for_status()
    return response

def run_put(args):
    BASE = 'https://{}:{}{}'.format(args.host, args.port, args.url)
    logging.info('PUT URL {}'.format(BASE))

    headers = {'content-type': 'application/yang-data+json'}
    logging.info('requesting headers {}'.format(headers))
    # autodetect json or yaml
    with open(args.body) as config_data:
        if 'yaml' in args.body:
            body = yaml.load(config_data)
        else:
            body = json.load(config_data)
    logging.info('body:{}'.format(json.dumps(body)))
    response = requests.put(url=BASE,
                            headers=headers,
                            data = json.dumps(body),

                            auth=HTTPBasicAuth(args.username, args.password),
                            verify=False)
    if response.status_code == 409:
        print(json.dumps(response.json(),indent=2))

    response.raise_for_status()
    return response

def run_patch(args):
    BASE = 'https://{}:{}{}'.format(args.host, args.port, args.url)
    logging.info('PUT URL {}'.format(BASE))

    headers = {'content-type': 'application/yang-data+json'}
    logging.info('requesting headers {}'.format(headers))
    # autodetect json or yaml
    with open(args.body) as config_data:
        if 'yaml' in args.body:
            body = yaml.load(config_data)
        else:
            body = json.load(config_data)
    logging.info('body:{}'.format(json.dumps(body)))
    response = requests.patch(url=BASE,
                            headers=headers,
                            data = json.dumps(body),

                            auth=HTTPBasicAuth(args.username, args.password),
                            verify=False)
    if response.status_code == 409:
        print(json.dumps(response.json(),indent=2))

    response.raise_for_status()
    return response

def run_delete(args, url):
    BASE = 'https://{}:{}{}'.format(args.host, args.port, url)
    logging.info('DELETE URL {}'.format(BASE))

    headers = {'accept': 'application/yang-data+json'}
    logging.info('requesting headers {}'.format(headers))
    response = requests.delete(url=BASE,
                            headers=headers,
                            auth=HTTPBasicAuth(args.username, args.password),
                            verify=False)

    if response.status_code == 409:
        print(json.dumps(response.json(),indent=2))
    response.raise_for_status()
    return response

def run_request(args, url):
    BASE = 'https://{}:{}{}'.format(args.host, args.port, url)
    logging.info('requesting URL {}'.format(BASE))

    headers={'accept':'application/yang-data+json'}
    logging.info('requesting headers {}'.format(headers))

    response = requests.get(url=BASE,
                                headers=headers,
                                auth=HTTPBasicAuth(args.username, args.password),
                                verify=False )
    response.raise_for_status()
    return response


def get_capabilities(args):
    # sub-module support
    # models as model,revsion  e.g. Cisco-IOS-XE-native,2017-05-30
    # submodels as mode,revision/submodule,revision
    #  e.g.          Cisco-IOS-XE-native,2017-05-30/Cisco-IOS-XE-interfaces,2017-05-31
    #url = '/restconf/data?fields=ietf-yang-library:modules-state/module(name;revision)'
    url = '/restconf/data/ietf-yang-library:modules-state/module?fields=name;revision;submodule/name'


    response = run_request(args, url)
    models = [ '{},{}'.format(model['name'], model['revision'])
               for model in response.json()['ietf-yang-library:module']]
    submodels = ['{},{}/{},{}'.format(model['name'],model['revision'],submodel['name'], submodel['revision'])
              for model in response.json()['ietf-yang-library:module'] if 'submodule' in model
              for submodel in model['submodule']]
    models.extend(submodels)
    return ('\n'.join(models))

def download(args, download):
    # submodel support  they are module,version/submodule,version
    parts = download.split('/')
    if len(parts) == 1:
        url='/restconf/data/ietf-yang-library:modules-state/ietf-yang-library:module={}/schema' # name, version
        url = url.format(parts[0])
    else:
        url = '/restconf/data/ietf-yang-library:modules-state/ietf-yang-library:module={}/submodule={}/schema'
        url = url.format(parts[0], parts[1])

    response = run_request(args, url)
    value = response.json()['ietf-yang-library:schema']

    url = '/restconf' + value.split('/restconf')[1]
    response = run_request(args, url)
    return response

def download_all(args):
    if not os.path.exists(MODELS):
        os.makedirs(MODELS)

    capabilities = get_capabilities(args)
    count = len(capabilities.split('n'))
    logging.info("Total files {}".format(count))

    updated = 0
    for capability in capabilities.split('\n'):
        parts = capability.split('/')
        if len(parts) == 2:
            target = '{}/{}'.format(MODELS, parts[1])
        else:
            target = '{}/{}'.format(MODELS, capability)
        if not os.path.isfile(target):
            logging.info('Downloading {}'.format(capability))
            response = download(args,capability)
            updated +=1
            if response.headers['Content-Type'] == 'application/yang':
                logging.info('saving model {}'.format(capability))
                with open(target, "w") as f:
                    f.write(response.text)

    logging.info('Updated {}'.format(updated))

if __name__ == "__main__":


    parser = ArgumentParser(description='Select your RESTCONF operation and parameters: url')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help="The IP address for the device to connect to (default localhost)")
    parser.add_argument('-u', '--username', type=str, default=os.environ.get('RCC_USERNAME', 'cisco'),
                        help="Username to use for authentication (default 'cisco')")
    parser.add_argument('-p', '--password', type=str, default=os.environ.get('RCC_PASSWORD', 'cisco'),
                        help="Password to use for authentication (default 'cisco')")
    parser.add_argument('--port', type=int, default=443,
                        help="Specify this if you want a non-default port (default 443)")
    parser.add_argument('--timeout', type=int, default=60,
                        help="Operation timeout in seconds (default 60)")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Exceedingly verbose logging to the console")
    parser.add_argument('-op', type=str, default='GET',
                        help="The RESTCONF  operation to use GET/POST/PATCH/PUT/DELETE")
    parser.add_argument('--yaml', action='store_true',
                        help="print the response as YAML")
    parser.add_argument('--capabilities', action='store_true',
                        help="print the response as YAML")
    parser.add_argument('--explore', action='store_true',
                        help="explore other API calls")
    parser.add_argument('--explore_all', type=str,
                        help="explore  API calls")
    parser.add_argument('--download', type=str,
                        help="download a model ")
    parser.add_argument('--download_all', action='store_true',
                        help="download all models ")
    parser.add_argument('--body', type=str,
                        help="The BODY for the RESTCONF call, PUT,POST, PATCH")
    parser.add_argument('--url', type=str,
                        help="The URL for the RESTCONF call")

    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
        logging.info("Verbose Logging enabled")

    if args.capabilities:
        capability_list = get_capabilities(args)
        print(capability_list)
        sys.exit(0)


    if args.explore_all:
        response = explore_all(args,args.explore_all)
        sys.exit(0)

    if args.download:
        response = download(args, args.download)
        if response.headers['Content-Type'] == 'application/yang':
            if args.explore:
                explore(response.text, args.download)
            else:
                print(response.text)

        sys.exit(0)

    if args.download_all:
        download_all(args)
        sys.exit(0)

    if args.op == "DELETE":
        try:
            response = run_delete(args, args.url)
            print ('status:',response.status_code)
        except requests.exceptions.HTTPError as e:
            print (e)
    if args.op == "POST":
        try:
            response  = run_post(args)
            print("Status",response.status_code)
        except requests.exceptions.HTTPError as e:
            print("Caught", e)
    if args.op == "PUT":
        try:
            response = run_put(args)
            print("Status", response.status_code)
        except requests.exceptions.HTTPError as e:
            print("Caught", e)
    if args.op == "PATCH":
        try:
            response = run_patch(args)
            print("Status", response.status_code)
        except requests.exceptions.HTTPError as e:
            print("Caught", e)

    if args.op == "GET":
        response = run_request(args, args.url)
        print_response(response, args.yaml)



