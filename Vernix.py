import json
import argparse
import os
import pathlib
import subprocess
import winshell
from lxml import etree
from pprint import pprint
from tabulate import tabulate
from win32com.client import Dispatch

XML_CONFIG_PATH = 'Config/monitor_config.xml'
USER_CONFIG_PATH = 'Config/user_config.json'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--gamepath', type=str, help="Path to the game's executable")
    return parser.parse_args()


def generate_monitor_config():
    subprocess.call(['MultiMonitorTool', '/sxml', XML_CONFIG_PATH])


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


def get_monitor_info_table(monitors_config: list):
    display_info = []

    for monitor in monitors_config:
         monitor_info = [clean_display_value(monitor['name']), clean_primary_value(monitor['primary']), monitor['monitor_name'], monitor['resolution'], monitor['adapter']]
         display_info.append(monitor_info)

    return display_info


def display_monitor_configuration(display_info: list):
    display_header = ['Display #', 'Primary', 'Display Name', 'Resolution', 'Graphics Card']
    print(convert_to_table(display_info, display_header))
    

def clean_display_value(display_value: str):
    return display_value.replace('\\\\.\\DISPLAY','')


def clean_primary_value(primary_value: str):
    if primary_value == 'Yes':
        return '*'
    else:
        return ''


def convert_to_table(content: list, headers: list):
    return tabulate(content, headers, colalign=("center", "center", "left",))    


def prompt_user_for_monitor_choice():
    return input('\nWhich monitor do you want to start games on? ')


def generate_user_config(choice: str, monitor_info: list):
    user_config = {}
    for monitor in monitor_info:
        if choice == monitor[0]:
            user_config['gaming_monitor'] = choice
        if monitor[1]:
            user_config['primary_monitor'] = monitor[0]
    return user_config


def export_config(config: dict):
    with open(USER_CONFIG_PATH, 'w') as file:
        json.dump(config, file)


def generate_batch_file(user_config: dict, game_path: str):
    script_contents = []
    script_contents.append('@echo off')
    script_contents.append('START nircmd setprimarydisplay {}'.format(user_config['gaming_monitor']))
    script_contents.append('timeout /t 5 /nobreak')
    script_contents.append('START "" "{}"'.format(game_path))
    return script_contents


def export_batch_file(script_contents: list, game_name: str):
    game_name = 'Batch Scripts/' + game_name + '.bat'
    
    with open(game_name, 'w') as file:
        for line in script_contents:
            file.write(line + '\n')

    return pathlib.Path(game_name).absolute()


def get_game_name(executable_path: str):
    return pathlib.Path(executable_path).stem


def create_shortcut(executable_path: str, batch_file_path: str, game_name: str):
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(game_name + '.lnk')
    shortcut.TargetPath = str(batch_file_path)
    shortcut.WorkingDirectory = str((pathlib.Path(batch_file_path)).parents[0])
    shortcut.IconLocation = str(executable_path)
    shortcut.save()

game_path = parse_args().gamepath
generate_monitor_config()
config = import_config(XML_CONFIG_PATH)
monitors_config = parse_config(config)
monitor_info = get_monitor_info_table(monitors_config)
display_monitor_configuration(monitor_info)
choice = prompt_user_for_monitor_choice()
user_config = generate_user_config(choice, monitor_info)
export_config(user_config)
script_contents = generate_batch_file(user_config, game_path)
game_name = get_game_name(game_path)
batch_file_path = export_batch_file(script_contents, game_name)
create_shortcut(game_path, batch_file_path, game_name)