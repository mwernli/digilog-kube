from dataclasses import dataclass
from typing import Union

import yaml
import os
import re


def parse_gb(in_s: str) -> float:
    try:
        return float(re.match(r'(\d+(\.\d+)?)Gi', in_s, re.IGNORECASE).group(1))
    except Exception as e:
        return parse_mb(in_s)


def parse_mb(in_s: str) -> float:
    try:
        return float(re.match(r'(\d+(\.\d+)?)Mi', in_s, re.IGNORECASE).group(1)) / 1000
    except Exception as e:
        print(e)
        print(in_s)
        return 999


@dataclass(eq=True, frozen=True)
class ResourceEntry:
    cpu: str
    memory: str

    def get_cpu(self) -> float:
        try:
            return float(re.match(r'(\d+(\.\d+)?)m(?:cpu)?', self.cpu, re.IGNORECASE).group(1)) / 1000
        except Exception as e:
            print(e)
            print(self.cpu)
            return 999

    def get_mem_gb(self) -> float:
        return parse_gb(self.memory)


@dataclass(eq=True, frozen=True)
class FileRecord:
    resource_name: str
    container_name: str
    requests: ResourceEntry
    limits: ResourceEntry


def filename_filter(filename: str) -> bool:
    return filename.endswith('.yaml')


def load_yaml_file(filename: str) -> dict:
    with open(filename, 'r') as f:
        return yaml.full_load(f)


REC_KINDS = {'Deployment', 'Job'}


def resource_filter(yaml_file: dict) -> bool:
    return yaml_file.get('kind') in REC_KINDS


def pvc_filter(yaml_file: dict) -> bool:
    return yaml_file.get('kind') == 'PersistentVolumeClaim'


def safe_get(yaml_part: dict, path: list[str]) -> Union[str, dict, list]:
    try:
        if len(path) == 1:
            return yaml_part[path[0]]
        else:
            return safe_get(yaml_part[path[0]], path[1:])
    except KeyError as e:
        print(e)
        print(yaml_part)
        print(path)
        return ''
    except AttributeError as e:
        print(e)
        print(yaml_part)
        print(path)
        return ''


def get_resources(resource_entry: dict) -> ResourceEntry:
    return ResourceEntry(resource_entry.get('cpu'), resource_entry.get('memory'))


def file_record(yaml_file: dict) -> list[FileRecord]:
    name = safe_get(yaml_file, ['metadata', 'name'])
    containers = safe_get(yaml_file, ['spec', 'template', 'spec', 'containers'])
    recs = []
    for c in containers:
        c_name = c.get('name')
        limits = get_resources(safe_get(c, ['resources', 'limits']))
        requests = get_resources(safe_get(c, ['resources', 'requests']))
        recs.append(FileRecord(name, c_name, requests, limits))
    return recs


REPLICAS = {'scrapy': 5}


def summarize_dir(dirname: str):
    os.chdir(dirname)
    yaml_files = list(map(load_yaml_file, filter(filename_filter, os.listdir())))
    rec_docs = filter(resource_filter, yaml_files)
    cpu_req_total = 0.0
    mem_req_total = 0.0
    cpu_lim_total = 0.0
    mem_lim_total = 0.0
    print('COMPUTING RESOURCES SUMMARY:')
    for doc in rec_docs:
        for rec in file_record(doc):
            m = REPLICAS.get(rec.resource_name) or 1
            cpu_req_total += m*rec.requests.get_cpu()
            mem_req_total += m*rec.requests.get_mem_gb()
            cpu_lim_total += m*rec.limits.get_cpu()
            mem_lim_total += m*rec.limits.get_mem_gb()
            name = f'{rec.resource_name} (x{m})'
            print(f'{name:20} {rec.container_name:20} {rec.requests.cpu:10} {rec.requests.memory:10} {rec.limits.cpu:10} {rec.limits.memory:10}')
    spacer = 'TOTALS:'
    print(f'{"=":=>85}')
    print(f'{spacer:41} {cpu_req_total:<10.4g} {mem_req_total:<10.4g} {cpu_lim_total:<10.4g} {mem_lim_total:<10.4g}')
    print('\n')

    print('PVC SUMMARY:')
    pvc_docs = filter(pvc_filter, yaml_files)
    total_storage = 0.0
    for doc in pvc_docs:
        name = safe_get(doc, ['metadata', 'name'])
        storage = safe_get(doc, ['spec', 'resources', 'requests', 'storage'])
        total_storage += parse_gb(storage)
        print(f'{name:20} {storage:6}')
    print(f'{"=":=>27}')
    print(f'{spacer:20} {total_storage:<10.4g}')


if __name__ == '__main__':
    summarize_dir('../overlays/init-k8s')
