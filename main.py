#!/usr/bin/env python2
# -*- coding: utf-8 -*-


from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar

from kivy.clock import Clock

import paramiko
import threading
#import time


# Classe pour un objet ssh avec la connexion déconnexion command …
class SSHThread(threading.Thread):
    def __init__(self):  # , popup_progress_win):
        super(SSHThread, self).__init__()
        self.hostname = ""
        self.username = ""
        self.password = ""
        #self.pop_win_progress = popup_progress_win

        self.conn = None
        self.is_finished = False

    def close(self):
        self.conn.close()

    def command(self, string):
        return self.conn.exec_command(string)

    def run(self):
        self.conn = paramiko.SSHClient()
        self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.conn.connect(self.hostname, username=self.username,
                          password=self.password,)

        self.is_finished = True
        #time.sleep(5)
        #self.pop_win_progress.dismiss()


# Affichage d'une popup pendant la connexion
class ConnexionModal(Popup):
    def __init__(self, title=""):
        super(ConnexionModal, self).__init__(auto_dismiss=False, title=title)
        self.pb = ProgressBar(max=10)
        self.content = self.pb
        self.on_open = self.connect_to_ssh
        self.stop_progress = False

    def connect_to_ssh(self):
        app = Vismais.get_running_app()
        # Lancer la connexion à SSH
        app.connect_to_ssh(self)
        # Lancer l'avancement
        Clock.schedule_interval(self.plus, 1)
        # Afficher la nouvelle fenêtre
        app.root.show_main_window()

    def on_close(self):
        self.stop_progress = True

    def plus(self, dt):
        if self.stop_progress:
            self.stop_progress = False
            return False

        if self.pb.value == 10:
            self.pb.value = 0
        else:
            self.pb.value += 1


# Fenêtre de connexion au démarrage
class ConnectForm(BoxLayout):
    def quit(self):
        Vismais.get_running_app().stop()

    def connect(self):
        popup = ConnexionModal(title="Connexion en cours")
        popup.open()


class StartStopMotion(BoxLayout):
    def __init__(self):
        super(StartStopMotion, self).__init__()
        self.on_open = self.essai()

    def quit(self):
        Vismais.get_running_app().stop()

    def essai(self):
        app = Vismais.get_running_app()
        app.ssh_thread.join()  # caca ici
            # avancer ailleurs de plus 1 dans l'affichage de la progressbar

        print('je passe ici')


# Fenêtre principale
class RootForm(AnchorLayout):
    def show_main_window(self):
        self.clear_widgets()
        self.main_window = StartStopMotion()
        self.add_widget(self.main_window)


# Application principale
class Vismais(App):
    def __init__(self):
        super(Vismais, self).__init__()
        self.ssh_thread = None
        self._popup = None

    def on_stop(self):
        self.disconnect_ssh()

    def disconnect_ssh(self):
        if self.ssh_thread:
            self.ssh_thread.close()

    def connect_to_ssh(self, popup_conn):
        self._popup = popup_conn
        self.ssh_thread = SSHThread()
        self.ssh_thread.start()

        Clock.schedule_interval(self.connection_checker, 1 / 10.)

    def connection_checker(self, dt):
        if self.ssh_thread.is_finished:
            self._popup.dismiss()
            Clock.unschedule(self.connection_checker)

    def is_alive(self):
        return self.ssh_thread.is_alive()


if __name__ == "__main__":
    Vismais().run()
