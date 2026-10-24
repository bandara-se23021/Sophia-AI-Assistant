
import eel

eel.init('www')

eel.start(
    'index.html',
    mode='chrome',
    host='localhost',
    port=8000,
    block=True
)
