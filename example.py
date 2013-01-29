#!/bin/env python2
"""A short example of using eSudo within another elementary application"""

import evas
import elementary

import esudo

command = "leafpad"

window = elementary.StandardWindow("test", "eSudo Test!")
window.callback_delete_request_add(lambda o: elementary.exit())
window.resize(400,400)

box = elementary.Box(window)
box.size_hint_weight = 1.0, 1.0
window.resize_object_add(box)
box.show()

lbl = elementary.Label(window)
lbl.text = "eSudo Test!"
lbl.show()
box.pack_end(lbl)

window.show()

def cb():
    print("The End")

esudo.eSudo(command, window, end_callback=cb)

elementary.run()
elementary.shutdown()
