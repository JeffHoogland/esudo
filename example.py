"""A short example of using eSudo within another elementary application"""

import elementary, esudo

command = "leafpad"

window = elementary.StandardWindow("test", "eSudo Test!")
window.callback_delete_request_add(lambda o: elementary.exit())
window.resize(400,400)
window.show()

esudo.eSudo(command, window)

elementary.run()
elementary.shutdown()
