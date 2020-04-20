import re
import time

import googleapiclient.discovery
import mcrcon
from flask import render_template
from google.cloud import secretmanager

PROJECT = "minecraft-272917"
ZONE = "europe-west1-b"
SERVER_NAME = "minecraft-server-2"
API_SECRET_KEY = "api"
RCON_SECRET_KEY = "rcon"


class SecretClient(object):
    def __init__(self, project):
        self.project = project
        self.client = secretmanager.SecretManagerServiceClient()

    def get_secret(self, key):
        secret_version = "projects/{0}/secrets/{1}/versions/latest".format(self.project, key)
        secret = self.client.access_secret_version(secret_version)
        return secret.payload.data.decode('UTF-8')


class ComputeClient(object):
    def __init__(self, project, zone):
        self.project = project
        self.zone = zone
        self.client = googleapiclient.discovery.build("compute", "v1")

    def find_instance(self, name):
        result = self.client.instances().list(project=self.project, zone=self.zone, filter="name = " + name).execute()
        return ComputeInstance(result["items"][0])

    def get_instance(self, id):
        result = self.client.instances().get(project=self.project, zone=self.zone, instance=id).execute()
        return ComputeInstance(result)

    def stop_instance(self, instance):
        operation = self.client.instances().stop(project=self.project, zone=self.zone, instance=instance.get_id()).execute()
        self._wait_for_operation(operation)
        return self.get_instance(instance.get_id())

    def start_instance(self, instance):
        operation = self.client.instances().start(project=self.project, zone=self.zone, instance=instance.get_id()).execute()
        self._wait_for_operation(operation)
        return self.get_instance(instance.get_id())

    def _wait_for_operation(self, operation):
        while True:
            result = self.client.zoneOperations().get(project=self.project, zone=self.zone, operation=operation["name"]).execute()

            if result['status'] == 'DONE':
                if 'error' in result:
                    raise Exception(result['error'])
                return result

            time.sleep(1)


class ComputeInstance(object):
    def __init__(self, item, players=None):
        self.item = item
        self.players = players

    def __str__(self):
        return str(self.item)

    def get_id(self):
        return self.item["id"]

    def get_name(self):
        return self.item["name"]

    def get_ip(self):
        try:
            return self.item["networkInterfaces"][0]["accessConfigs"][0]["natIP"]
        except KeyError:
            return None

    def get_status(self):
        return self.item["status"]

    def is_running(self):
        return self.get_status() == "RUNNING"

    def is_terminated(self):
        return self.get_status() == "TERMINATED"

    def is_done(self):
        return (self.is_running() and self.players) or self.is_terminated()


def server_status(request):
    if not _is_authenticated(request):
        return _forbidden()

    compute_client = ComputeClient(PROJECT, ZONE)
    instance = compute_client.find_instance(SERVER_NAME)
    if instance.is_running():
        message = "started"
    elif instance.is_terminated():
        message = "stopped"
    else:
        message = instance.get_status().lower()
    return _render_server_status(instance, message)


def start_server(request):
    if not _is_authenticated(request):
        return _forbidden()

    compute_client = ComputeClient(PROJECT, ZONE)
    instance = compute_client.find_instance(SERVER_NAME)
    if instance.is_terminated():
        instance = compute_client.start_instance(instance)

    if instance.is_running():
        message = "started"
    else:
        message = "is starting ..."
    return _render_server_status(instance, message)


def stop_server(request):
    if not _is_authenticated(request):
        return _forbidden()

    compute_client = ComputeClient(PROJECT, ZONE)
    instance = compute_client.find_instance(SERVER_NAME)
    if instance.is_running():
        instance = compute_client.stop_instance(instance)

    if instance.is_terminated():
        message = "stopped"
    else:
        message = "is stopping ..."

    return _render_server_status(instance, message)


def stop_server_handler(event, context):
    compute_client = ComputeClient(PROJECT, ZONE)
    instance = compute_client.find_instance(SERVER_NAME)
    if instance.is_running():
        number_of_players = _minecraft_number_of_players(instance)
        if number_of_players == 0:
            print("Stopping instance {} without active players".format(instance.get_name()))
            compute_client.stop_instance(instance)
        else:
            print("Instance {} is used by {} player(s), skip stopping".format(instance.get_name(), number_of_players))


def _is_authenticated(request):
    api_key = request.args.get('api_key')
    if api_key is None:
        return False
    else:
        secret_client = SecretClient(PROJECT)
        return api_key == secret_client.get_secret(API_SECRET_KEY)


def _forbidden():
    return 'forbidden', 403


def _render_server_status(instance, message):
    if instance.is_running():
        players = _minecraft_list_players(instance)
        if players is None:
            message = "is starting ..."
        else:
            instance.players = players

    return render_template('status.html', message=message, instance=instance)


def _minecraft_list_players(instance):
    return _minecraft_command(instance, "/list")


def _minecraft_number_of_players(instance):
    list = _minecraft_command(instance, "/list")
    if list is None:
        return 0
    else:
        number_of_players = re.findall("There are (\d+) of a max \d+ players online", list)[0]
        return int(number_of_players)


def _minecraft_command(instance, command):
    try:
        secret_client = SecretClient(PROJECT)
        with mcrcon.MCRcon(instance.get_ip(), secret_client.get_secret(RCON_SECRET_KEY)) as client:
            return client.command(command)
    except ConnectionRefusedError:
        return None


if __name__ == "__main__":
    # compute_client = ComputeClient(PROJECT, ZONE)
    # compute_instance = compute_client.find_instance(SERVER_NAME)
    # print(compute_instance.get_status())

    # secret_client = SecretClient(PROJECT)
    # print(secret_client.get_secret(API_SECRET_KEY))

    pass
