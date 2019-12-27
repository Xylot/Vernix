import json
from lxml import etree
from pprint import pprint
from tabulate import tabulate


def import_config(file_path: str) -> list:
    config = etree.parse(file_path)
    return config.xpath('//item')


def parse_config(config: list):
    monitors = []
    for monitor in config:
        monitor_config = {}
        for prop in monitor:
            monitor_config[prop.tag] = prop.text
        monitors.append(monitor_config)
    return monitors


def display_monitor_configuration(monitors_config: list):
    display_info = []
    display_header = ['Display #', 'Display Name', 'Resolution', 'Graphics Card']

    for monitor in monitors_config:
         monitor_info = [clean_display_value(monitor['name']), monitor['monitor_name'], monitor['resolution'], monitor['adapter']]
         display_info.append(monitor_info)

    print(convert_to_table(display_info, display_header))
    

def clean_display_value(display_value: str):
    return display_value.replace('\\\\.\\DISPLAY','')


def convert_to_table(content: list, headers: list):
    return tabulate(content, headers, numalign="center")    


def prompt_user_for_monitor_choice():
    pass

config = import_config('xml')
monitors_config = parse_config(config)
display_monitor_configuration(monitors_config)

