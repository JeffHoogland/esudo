#!/bin/env python2
#
# eSudo - a GUI sudo tool in python and elementary
#
# Base code by AntCer, polished by Jeff Hoogland
# Something actually useful done by Kai Huuhko <kai.huuhko@gmail.com>
#

import os
import getpass
import logging
logging.basicConfig(level=logging.DEBUG)

import PAM

import ecore
import evas
import elementary

#----Popups
def pw_error_popup(en):
    win = en.top_widget_get()
    popup = elementary.Popup(win)
    popup.size_hint_weight = evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND
    popup.part_text_set("title,text", "Error")
    popup.text = "Incorrect Password!<br>Please try again."
    popup.timeout = 3.0
    popup.show()

#----eSudo
class eSudo(object):
    def __init__( self, command=None, win=None, end_callback=None ):
        if not win:
            win = elementary.Window("esudo", elementary.ELM_WIN_DIALOG_BASIC)
            win.title = "eSudo"
            win.borderless = True
            win.size_hint_weight = evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND
            win.size_hint_align = evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL
            win.resize(300, 200)
            win.callback_delete_request_add(lambda o: elementary.exit())
            win.show()

            bg = elementary.Background(win)
            bg.size_hint_weight = 1.0, 1.0
            win.resize_object_add(bg)
            bg.show()

            self.embedded = False
        else:
            self.embedded = True

        self.cmd = command
        self.end_cb = end_callback if callable(end_callback) else None

#--------eSudo Window
        bz = elementary.Box(win)
        bz.size_hint_weight = 1.0, 0.0
        bz.size_hint_align = -1.0, 0.0
        bz.show()

        lbl = elementary.Label(win)
        lbl.size_hint_align = -1.0, 0.0
        lbl.text = "eSudo"
        lbl.scale = 2.0
        lbl.show()

        bz.pack_end(lbl)

        sep = elementary.Separator(win)
        sep.horizontal = True
        sep.show()

        bz.pack_end(sep)

        fr = elementary.Frame(win)
        fr.text = "Command:"
        fr.size_hint_align = -1.0, 0.0
        fr.show()

        bz.pack_end(fr)

        self.cmdline = cmdline = elementary.Entry(win)
        cmdline.elm_event_callback_add(self.entry_event)
        cmdline.single_line = True
        if self.cmd:
            cmdline.text = self.cmd
            cmdline.editable = False
        cmdline.show()

        fr.content = cmdline

        fr = elementary.Frame(win)
        fr.text = "Password:"
        fr.size_hint_align = -1.0, 0.0
        fr.show()

        bz.pack_end(fr)

        en = elementary.Entry(win)
        en.name = "password"
        en.elm_event_callback_add(self.entry_event)
        en.single_line = True
        en.password = True
        en.show()

        fr.content = en

        sep = elementary.Separator(win)
        sep.horizontal = True
        sep.show()

        bz.pack_end(sep)

        btnb = elementary.Box(win)
        btnb.horizontal = True
        btnb.size_hint_weight = evas.EVAS_HINT_EXPAND, 0.0
        btnb.size_hint_align = evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL
        btnb.show()

        bt = elementary.Button(win)
        bt.text = "Cancel"
        bt.callback_clicked_add(self.esudo_cancel, en)
        bt.size_hint_align = evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL
        bt.size_hint_weight = evas.EVAS_HINT_EXPAND, 0.0
        bt.show()

        btnb.pack_end(bt)

        bt = elementary.Button(win)
        bt.text = "OK"
        bt.callback_clicked_add(self.password_check, en)
        bt.size_hint_align = evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL
        bt.size_hint_weight = evas.EVAS_HINT_EXPAND, 0.0
        bt.show()

        btnb.pack_end(bt)

        bz.pack_end(btnb)

        self.iw = iw = elementary.InnerWindow(win)
        iw.content = bz
        iw.show()
        iw.activate()
        if self.cmd:
            en.focus = True

    def entry_event(self, obj, entry, event_type, event, *args):
        if event_type == evas.EVAS_CALLBACK_KEY_UP:
            if event.keyname == "Return" and entry.name == "password":
                self.password_check(None, entry)
            elif event.keyname == "Escape":
                self.close()

        return True

#--------Password Checker
    def password_check(self, bt, en):
        if not en.entry or not self.cmdline.entry:
            return

#------------Sets Password
        def pam_conv(auth, query_list, userData):
            password = en.entry
            resp = []
            for i in range(len(query_list)):
                query, type = query_list[i]
                if type == PAM.PAM_PROMPT_ECHO_ON or type == PAM.PAM_PROMPT_ECHO_OFF:
                    val = password
                    resp.append((val, 0))
                elif type == PAM.PAM_PROMPT_ERROR_MSG or type == PAM.PAM_PROMPT_TEXT_INFO:
                    resp.append(('', 0))
                else:
                    return None
            return resp

#------------Username & Service To Use
        username = getpass.getuser()
        service = 'passwd'

#------------Start Password Test
        auth = PAM.pam()
        auth.start(service)
        auth.set_item(PAM.PAM_USER, username)
        auth.set_item(PAM.PAM_CONV, pam_conv)
        try:
            auth.authenticate()
            auth.acct_mgmt()
        except PAM.error, resp:
            pw_error_popup(en)
            en.entry = ""
            en.focus = True
            logging.info("Invalid password! Please try again.")
            return
        except:
            logging.exception("Internal error! File bug report.")
        else:
            self.esudo_ok(bt, en)

#--------eSudo Cancel Button
    def esudo_cancel(self, bt, en):
        en.entry = ""
        self.close()

    def close(self):
        self.iw.delete() if self.embedded else elementary.exit()

#--------eSudo OK Button
    def esudo_ok(self, bt, en):
        password = en.entry
        cmd = self.cmdline.entry
        logging.info("Starting %s" % cmd)
        self.run_command("sudo -S %s" % (cmd), password)

    def run_command(self, command, password):
        self.cmd_exe = cmd = ecore.Exe(command, ecore.ECORE_EXE_PIPE_READ|ecore.ECORE_EXE_PIPE_ERROR|ecore.ECORE_EXE_PIPE_WRITE)
        cmd.on_add_event_add(self.command_started)
        cmd.on_data_event_add(self.received_data, password)
        cmd.on_error_event_add(self.received_error, password)
        cmd.on_del_event_add(self.command_done)

    def command_started(self, cmd, event, *args, **kwargs):
        logging.debug("Command started")
        logging.debug(cmd)

    def received_data(self, cmd, event, *args, **kwargs):
        logging.debug("Received data")
        logging.debug(event.data)

    def received_error(self, cmd, event, *args, **kwargs):
        logging.debug("Received error")
        logging.debug(event.data)

        if "password for" in event.data:
            password = args[0]
            cmd.send(str(password)+"\n")

    def command_done(self, cmd, event, *args, **kwargs):
        logging.debug("Command done")
        if self.end_cb:
            try:
                self.end_cb(event.exit_code)
            except:
                pass
        self.close()

if __name__ == "__main__":
    import sys
    cmd = " ".join(sys.argv[1:])

    start = eSudo(cmd)

    elementary.run()
    elementary.shutdown()
