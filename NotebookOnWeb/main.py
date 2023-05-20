import sys
from xes.tool import xopen
xopen()
if '' not in sys.path:
    sys.path.append(".")

from notebookOnWeb import app
from os import environ
port = int(environ.get('PORT',80))
app.run(host='0.0.0.0',port=port,debug=True)
