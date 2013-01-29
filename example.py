"""A short example of using eSudo within another elementary application"""

import elementary, esudo, evas

command = "leafpad"

window = elementary.StandardWindow("test", "eSudo Test!")
window.callback_delete_request_add(lambda o: elementary.exit())
nf = elementary.Naviframe(window)
nf.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
nf.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
nf.show()
window.resize_object_add(nf)

lbl = elementary.Label(window)
lbl.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
lbl.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
lbl.text = "Derp"
lbl.show()

nf.item_simple_push(lbl)

window.resize(400,400)
window.show()

esudo.eSudo(command, window)

elementary.run()
elementary.shutdown()
