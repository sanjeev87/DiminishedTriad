#clean logs, set up 6 beackend, start sentinel
../create-multiredis/create-multiredis clean
../create-multiredis/create-multiredis start
host="127.0.0.1" port="50001" runipy ../dt_server.ipynb 2&>1 >/dev/null &
