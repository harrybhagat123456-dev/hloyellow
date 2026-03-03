#!/bin/bash

rm -f bot.session bot.session-journal
python3 app.py &
python3 modules/main.py
