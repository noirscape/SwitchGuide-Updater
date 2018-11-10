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
VERSION = '1.1.0'

class WindowState(Enum):
    MAIN_MENU = 0
    FAILED = 1
    UPDATING_HEKATE = 2
    UPDATING_AMS = 3
    SELF_UPDATE_AVAILABLE = 4
    UPDATING_SELF = 5
    SELF_UPDATE_SUCCEEDED = 6

def update_atmosphere():
    r = urllib.request.urlopen(BASE_URL + 'fusee-primary.bin')
    if r.getcode() == 200:
        with open('/fusee-primary.bin', 'wb') as fusee_primary:
            shutil.copyfileobj(r, fusee_primary)

    r_two = urllib.request.urlopen(BASE_URL + 'fusee-secondary.bin')
    if r_two.getcode() == 200:
        with open('/fusee-secondary.bin', 'wb') as fusee_secondary:
            shutil.copyfileobj(r_two, fusee_secondary)

    r_three = urllib.request.urlopen(BASE_URL + 'atmosphere/titles/0100000000000036/exefs.nsp')
    if r_three.getcode() == 200:
        os.makedirs('/atmosphere/titles/0100000000000036/', exist_ok=True)
        with open('/atmosphere/titles/0100000000000036/exefs.nsp', 'wb') as creport:
            shutil.copyfileobj(r_three, creport)

    r_four = urllib.request.urlopen(BASE_URL + 'atmosphere/titles/0100000000000032/exefs.nsp')
    if r_four.getcode() == 200:
        os.makedirs('/atmosphere/titles/0100000000000032/', exist_ok=True)
        with open('/atmosphere/titles/0100000000000032/exefs.nsp', 'wb') as settings_mitm:
            shutil.copyfileobj(r_three, settings_mitm)

def update_hekate():
    r = urllib.request.urlopen(BASE_URL + 'hekate.bin')
    if r.getcode() == 200:
        with open('/bootloader/update.bin', 'wb') as hekate_update_file:
            shutil.copyfileobj(r, hekate_update_file)

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
        local_json = {"atmosphere": "Unknown, run \"Update Atmosphere\" at least once!", "hekate": "Unknown, run \"Update Hekate\" at least once!"}

    return local_json, remote_json


def write_update_file(local_json, remote_json, updated_ams=False, updated_hekate=False):
    os.makedirs('SwitchGuideUpdater', exist_ok=True)
    output_json = {
        "atmosphere": local_json["atmosphere"],
        "hekate": local_json["hekate"]
    }
    if updated_ams:
        output_json["atmosphere"] = remote_json["atmosphere"]
    if updated_hekate:
        output_json["hekate"] = remote_json["hekate"]
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

    renderer.shutdown()

if __name__ == '__main__':
    main()
