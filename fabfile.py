#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

from fabric.api import cd, run, local, sudo, env


env.hosts = ["matt@web1.ubskin.net:48022"]

PROJECT_NAME = "ubskin"
DB_NAME = "ubskin_web"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, '', '')
SECRETS_DIR = os.path.join(BASE_DIR, '', 'secrets', '')
# dockers_dir = os.path.join(base_dir, "dockers", "")
# rsync_exclude_file_path = os.path.join(base_dir, "scripts", "rsync_exclude.list")

RSYNC_EXCLUDES = " --exclude=.git --exclude=.gitignore --exclude=.settings "\
    "--exclude=.project --exclude=.buildpath --exclude=.DS_Store --exclude=.idea/ "\
    "--exclude=/scripts/ --exclude=/static/index_data/ --exclude=__pycache__/ "\
    "--exclude=/config_local.py --exclude=*.md --exclude=*.pyc "\
    "--exclude=/fabfile.py --exclude=/dockers/ --exclude=/ENV/ "\
    "--exclude=/venv/ --exclude=.vscode --exclude=/conf/supervisor.conf "\
    "--exclude=migrations/ --exclude=settings_local.py "

curr_time = time.strftime("%y%m%d")
LOCAL_BACKUP_PATH = "".join(["~/Projects/backup/", PROJECT_NAME, "/"])
REMOTE_BACKUP_PATH = "".join(["/data/", PROJECT_NAME, "/backup/"])

cmd_rsync_static = os.path.join(BASE_DIR, PROJECT_NAME, "scripts", "rsync_static.sh")
cmd_rsync_webwork = os.path.join(BASE_DIR, PROJECT_NAME, "scripts", "rsync_webwork.sh")
cmd_rsync_webwork_test = os.path.join(BASE_DIR, PROJECT_NAME, "scripts", "rsync_webwork_test.sh")


def rsync_static():
    local(cmd_rsync_static)

def rsync_static_run():
    local(cmd_rsync_static+" run")


def rsync_web(is_real=False):
    """Rsync webwork from local to remote"""
    # local("python -m compileall "+WEB_DIR)
    param_dry_run = ' ' if is_real else ' --dry-run'
    cmd_rsync = "rsync -avz -u --no-times --progress --delete -e \"ssh -p 48022\"" + \
        param_dry_run + RSYNC_EXCLUDES + " " + WEB_DIR + \
        " matt@web1.ubskin.net:/data/ubskin/web/"
    local(cmd_rsync)
    # local(cmd_rsync_webwork)

def rsync_web_run():
    """Rsync webwork for sure"""
    rsync_web(is_real=True)

def restart_web():
    # run("sudo supervisorctl restart "+PROJECT_NAME+"_web:")
    run("docker-compose -f /data/dockers/docker-compose.yml restart "+PROJECT_NAME+"web")


# --- dev --- #

def rsync_dev(is_real=False):
    # local("python -m compileall " + WEB_DIR)
    param_dry_run = ' ' if is_real else ' --dry-run'
    cmd_rsync = 'rsync -avz -u --no-times --progress --delete -e "ssh" ' + \
        param_dry_run + RSYNC_EXCLUDES + ' ' + WEB_DIR + \
        ' matt@10.0.0.101:/data/ubskin/web/'
    local(cmd_rsync)

def rsync_dev_run():
    rsync_dev(is_real=True)


# --- jh --- #

def rsync_jh(is_real=False):
    # local("python -m compileall " + WEB_DIR)
    param_dry_run = ' ' if is_real else ' --dry-run'
    cmd_rsync = 'rsync -avz -u --no-times --progress --delete -e "ssh -p48022" ' + \
        param_dry_run + RSYNC_EXCLUDES + ' ' + WEB_DIR + \
        ' matt@web1.ubskin.net:/data/prop/web/'
    local(cmd_rsync)

def rsync_jh_run():
    rsync_jh(is_real=True)


# --- secrets --- #

def rsync_secrets(is_real=False):
    param_dry_run = ' ' if is_real else ' --dry-run'
    cmd_rsync = 'rsync -avz -u --no-times --progress --delete -e "ssh -p 48022" ' + \
        param_dry_run + RSYNC_EXCLUDES + ' ' + SECRETS_DIR + \
        ' matt@aliyun.juanxin.com:/data/prop/secrets/'
    local(cmd_rsync)

def rsync_secrets_run():
    rsync_secrets(is_real=True)


# === www site === #

SITE_DIR = os.path.join(BASE_DIR, "siteWork", "")

def rsync_site():
    local("rsync -avz -u --dry-run --progress --delete -e \"ssh -p 48022\" " + \
        RSYNC_EXCLUDES + " " + SITE_DIR + \
        " matt@site.igidi.com:/data/gtrip/siteWork/"
    )

def rsync_site_run():
    local("rsync -avz -u --progress --delete -e \"ssh -p 48022\" " + \
        RSYNC_EXCLUDES + " " + SITE_DIR + \
        " matt@site.igidi.com:/data/gtrip/siteWork/"
    )


# === db backup === #

def remote_db_backup():
    run("".join(["mongodump -d ", DB_NAME, " -o ", REMOTE_BACKUP_PATH]))

    f_tar_name = _build_tar_name()
    cmd_tar = "".join(
        ["tar jcvf ", f_tar_name, " -C ", REMOTE_BACKUP_PATH, DB_NAME, "/ ."]
    )
    run(cmd_tar)

    run("".join(["rm -rf ", REMOTE_BACKUP_PATH, DB_NAME, "/"]))

def _build_tar_name():
    return "".join([REMOTE_BACKUP_PATH, DB_NAME, "-", curr_time, ".tar.bz2"])


def remote_db_pull():
    remote_db_backup()

    # copy to local
    f_tar_name = _build_tar_name()
    cmd_tar = "".join(
        ["tar jcvf ", f_tar_name, " -C ", REMOTE_BACKUP_PATH, DB_NAME, "/ ."]
    )
    run(cmd_tar)

    # clean up
    run("".join(["rm -rf ", REMOTE_BACKUP_PATH, DB_NAME, "/"]))


def remote_db_import():
    remote_db_pull()

    cmd_tar = "".join(
        ["tar jxvf ", LOCAL_BACKUP_PATH, "database/", DB_NAME,
         "-", curr_time, ".tar.bz2", " -C ", LOCAL_BACKUP_PATH, "database/"]
    )
    local(cmd_tar)

    collection_tuple = (
        'cities', 'codes', 'feedbacks', 'members', 'photos', 'relations',
        'reviews', 'shops', 'trips'
    )
    for collection in collection_tuple:
        cmd_restore = "".join(
            ["mongorestore --drop -d ", DB_NAME, " ",
             LOCAL_BACKUP_PATH, "database/app_", collection, ".bson"]
        )
        local(cmd_restore)

    cmd_clear_bson = "".join(["rm -f ", LOCAL_BACKUP_PATH, "database/", "*.bson"])
    local(cmd_clear_bson)
    cmd_clear_json = "".join(["rm -f ", LOCAL_BACKUP_PATH, "database/", "*.json"])
    local(cmd_clear_json)


# === docker === #

def rsync_dockers():
    local("rsync -avz --dry-run --progress --delete -e \"ssh -p 48022\" " + \
        RSYNC_EXCLUDES + " " + dockers_dir + \
        " matt@api.xiaotangdou.com:/data/dockers/"
    )

def rsync_dockers_run():
    local("rsync -avz --progress --delete -e \"ssh -p 48022\" " + \
        RSYNC_EXCLUDES + " " + dockers_dir + \
        " matt@api.xiaotangdou.com:/data/dockers/"
    )


def rsync_webwork_test():
    run("sudo supervisorctl restart "+PROJECT_NAME+":")

def rsync_webwork_test_run():
    local(cmd_rsync_webwork_test+" run")

def restart_webwork_test():
    run("sudo supervisorctl restart "+PROJECT_NAME+":")


def clean_webwork():
    cmd_clean = "find "+WEBWORK_DIR+" -name '*.pyc' -delete"
    local(cmd_clean)
