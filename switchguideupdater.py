import urllib.request
import json
import nx
import os
import shutil
import imgui
import imguihelper
import _nx
from imgui.integrations.nx import NXRenderer
import sys
import traceback
from enum import Enum

BASE_URL = 'http://amsupdater.catgirlsin.space/json/'
VERSION = '1.2.4'

class WindowState(Enum):
    MAIN_MENU = 0
    FAILED = 1
    UPDATING_HEKATE = 2
    UPDATING_AMS = 3
    SELF_UPDATE_AVAILABLE = 4
    UPDATING_SELF = 5
    SELF_UPDATE_SUCCEEDED = 6
    UPDATING_NX_HBMENU = 7
    UPDATING_NX_HBLOADER = 8

def download_file(remote_name, local_path):
    r = urllib.request.urlopen(remote_name)
    if r.getcode() == 200:
        with open(local_path, 'wb') as output_path:
            shutil.copyfileobj(r, output_path)

def update_atmosphere():
    download_file(BASE_URL + 'fusee-primary.bin', '/fusee-primary.bin')
    download_file(BASE_URL + 'fusee-secondary.bin', '/fusee-secondary.bin')
    os.makedirs('/atmosphere/titles/0100000000000032/', exist_ok=True)
    download_file(BASE_URL + 'atmosphere/titles/0100000000000032/exefs.nsp', '/atmosphere/titles/0100000000000032/exefs.nsp')
    os.makedirs('/atmosphere/titles/0100000000000034/', exist_ok=True)
    download_file(BASE_URL + 'atmosphere/titles/0100000000000034/exefs.nsp', '/atmosphere/titles/0100000000000034/exefs.nsp')
    os.makedirs('/atmosphere/titles/0100000000000036/', exist_ok=True)
    download_file(BASE_URL + 'atmosphere/titles/0100000000000036/exefs.nsp', '/atmosphere/titles/0100000000000036/exefs.nsp')

def update_hekate():
    download_file(BASE_URL + 'hekate.bin', '/bootloader/update.bin')

def update_nx_hbloader():
    os.makedirs('/atmosphere', exist_ok=True)
    download_file(BASE_URL + 'hbl.nsp', '/atmosphere')

def update_nx_hbmenu():
    download_file(BASE_URL + 'hbl.nro', '/')

def update_self():
    r = urllib.request.urlopen(BASE_URL + 'switchguideupdater.py')
    if r.getcode() == 200:
        with open(sys.argv[0], 'wb') as current_script:
            shutil.copyfileobj(r, current_script)

def fetch_json():
    ## Get remote.json
    r = urllib.request.urlopen(BASE_URL + 'version.json')
    remote_json = json.loads(r.read().decode("utf-8"))

    ## Get local.json
    try:
        with open('SwitchGuideUpdater/local.json', 'r') as localfile:
            local_json = json.load(localfile)
    except FileNotFoundError: # Local json doesn't exist yet? No biggie, we'll just load in that we don't know it!
        local_json = {
            "atmosphere": "Unknown, run \"Update Atmosphere\" at least once!", 
            "hekate": "Unknown, run \"Update Hekate\" at least once!",
            "nx-hbmenu": "Unknown, run \"Update nx-hbmenu\" at least once!",
            "nx-hbloader": "Unknown, run \"Update nx-hbloader\" at least once!"
        }

    if "nx-hbmenu" not in local_json:
        local_json["nx-hbmenu"] = "Unknown, run \"Update nx-hbmenu\" at least once!"
    if "nx-hbloader" not in local_json:
        local_json["nx-hbloader"] = "Unknown, run \"Update nx-hbloader\" at least once!"

    return local_json, remote_json


def write_update_file(local_json, remote_json, updated_ams=False, updated_hekate=False, updated_nx_hbmenu=False, updated_nx_hbloader=False):
    os.makedirs('SwitchGuideUpdater', exist_ok=True)
    output_json = {
        "atmosphere": local_json["atmosphere"],
        "hekate": local_json["hekate"],
        "nx-hbmenu": local_json["nx-hbmenu"],
        "nx-hbloader": local_json["nx-hbloader"]
    }
    if updated_ams:
        output_json["atmosphere"] = remote_json["atmosphere"]
    if updated_hekate:
        output_json["hekate"] = remote_json["hekate"]
    if updated_nx_hbloader:
        output_json["nx-hbloader"] = remote_json["nx-hbloader"]
    if updated_nx_hbmenu:
        output_json["nx-hbmenu"] = remote_json["nx-hbmenu"]
    with open('SwitchGuideUpdater/local.json', 'w') as localfile:
        json.dump(output_json, localfile)

def main():
    fail_exception = None
    status = WindowState.MAIN_MENU
    try:
        local_json, remote_json = fetch_json()
    except:
        fail_exception = traceback.format_exc()
        status = WindowState.FAILED
    else:
        if VERSION != remote_json["updater"]:
            status = WindowState.SELF_UPDATE_AVAILABLE
    can_update = False
    renderer = NXRenderer()
    while True:
        renderer.handleinputs()

        imgui.new_frame()
        width, height = renderer.io.display_size
        imgui.set_next_window_size(width, height)
        imgui.set_next_window_position(0, 0)
        imgui.begin("SwitchGuide Updater", flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_SAVED_SETTINGS | imgui.WINDOW_NO_COLLAPSE)
        imgui.set_window_font_scale(2.0)
        if status is WindowState.MAIN_MENU:
            imgui.begin_group()
            imgui.text("Atmosphere Updater")
            imgui.text("Loaded Atmosphere version: {}\nRemote Atmosphere version: {}".format(local_json["atmosphere"], remote_json["atmosphere"]))
            if imgui.button("Update Atmosphere"):
                status = WindowState.UPDATING_AMS
            imgui.end_group()
            imgui.separator()
            imgui.begin_group()
            imgui.text("Loaded Hekate version: {}\nRemote Hekate version: {}"
                    .format(local_json["hekate"], remote_json["hekate"]))                
            if imgui.button("Update Hekate"):
                status = WindowState.UPDATING_HEKATE
            imgui.end_group()
            imgui.separator()
            imgui.begin_group()
            imgui.text("Loaded nx-hbmenu version: {}\nRemote nx-hbmenu version: {}"
                    .format(local_json["nx-hbmenu"], remote_json["nx-hbmenu"]))
            imgui.text("Loaded nx-hbloader version: {}\nRemote nx-hbloader version: {}"
                    .format(local_json["nx-hbloader"], remote_json["nx-hbloader"]))
            if imgui.button("Update nx-hbmenu"):
                status = WindowState.UPDATING_NX_HBMENU
            imgui.same_line()
            if imgui.button("Update nx-hbloader"):
                status = WindowState.UPDATING_NX_HBLOADER
            imgui.end_group()
            imgui.separator()
            imgui.text("SwitchGuide Updater {}".format(VERSION))
            imgui.text("© 2018 - Valentijn \"noirscape\" V.")
        elif status is WindowState.SELF_UPDATE_AVAILABLE:
            imgui.begin_group()
            imgui.text("An update for SwitchGuide-Updater is available.")
            imgui.end_group()
            imgui.separator()
            if imgui.button("Install version {}".format(remote_json["updater"])):
                status = WindowState.UPDATING_SELF
            if imgui.button("Keep running version {}".format(VERSION)):
                status = WindowState.MAIN_MENU
        elif status is WindowState.UPDATING_AMS:
            imgui.text("Updating Atmosphere to version {}...".format(remote_json["atmosphere"]))
            can_update = True
        elif status is WindowState.UPDATING_HEKATE:
            imgui.text("Updating Hekate to version {}...".format(remote_json["hekate"]))
            can_update = True
        elif status is WindowState.UPDATING_SELF:
            imgui.text("Updating SwitchGuide-Updater to version {}...".format(remote_json["updater"]))
            can_update = True
        elif status is WindowState.UPDATING_NX_HBLOADER:
            imgui.text("Updating nx-hbloader to version {}...".format(remote_json["nx-hbloader"]))
            can_update = True
        elif status is WindowState.UPDATING_NX_HBMENU:
            imgui.text("Updating nx-hbmenu to version {}...".format(remote_json["nx-hbmenu"]))
            can_update = True
        elif status is WindowState.SELF_UPDATE_SUCCEEDED:
            imgui.text("Succesfully updated SwitchGuide-Updater")
            imgui.text("Press HOME to exit and reopen PyNX to run this application.")
        elif status is WindowState.FAILED:
            imgui.text(str(fail_exception))
        imgui.end()

        imgui.render()
        renderer.render()

        if status is WindowState.UPDATING_AMS and can_update:
            try:
                update_atmosphere()
            except:
                fail_exception = traceback.format_exc()
                status = WindowState.FAILED
            else:
                try:
                    write_update_file(local_json, remote_json, updated_ams=True)
                    local_json, remote_json = fetch_json()
                    status = WindowState.MAIN_MENU
                    can_update = False
                except:
                    fail_exception = traceback.format_exc()
                    status = WindowState.FAILED
        elif status is WindowState.UPDATING_HEKATE and can_update:
            try:
                update_hekate()
            except:
                fail_exception = traceback.format_exc()
                status = WindowState.FAILED
            else:
                try:
                    write_update_file(local_json, remote_json, updated_hekate=True)
                    local_json, remote_json = fetch_json()
                    status = WindowState.MAIN_MENU
                    can_update = False
                except:
                    fail_exception = traceback.format_exc()
                    status = WindowState.FAILED
        elif status is WindowState.UPDATING_SELF and can_update:
            try:
                update_self()
            except:
                fail_exception = traceback.format_exc()
                status = WindowState.FAILED
            else:
                status = WindowState.SELF_UPDATE_SUCCEEDED
                can_update = False
        elif status is WindowState.UPDATING_NX_HBLOADER and can_update:
            try:
                update_nx_hbloader()
            except:
                fail_exception = traceback.format_exc()
                status = WindowState.FAILED
            else:
                try:
                    write_update_file(local_json, remote_json, updated_nx_hbloader=True)
                    local_json, remote_json = fetch_json()
                    status = WindowState.MAIN_MENU
                    can_update = False
                except:
                    fail_exception = traceback.format_exc()
                    status = WindowState.FAILED
        elif status is WindowState.UPDATING_NX_HBMENU and can_update:
            try:
                update_nx_hbmenu()
            except:
                fail_exception = traceback.format_exc()
                status = WindowState.FAILED
            else:
                try:
                    write_update_file(local_json, remote_json, updated_nx_hbmenu=True)
                    local_json, remote_json = fetch_json()
                    status = WindowState.MAIN_MENU
                    can_update = False
                except:
                    fail_exception = traceback.format_exc()
                    status = WindowState.FAILED

    renderer.shutdown()

if __name__ == '__main__':
    main()
