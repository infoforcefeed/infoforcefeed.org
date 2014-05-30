#!/usr/bin/bash

rsync -PazL built/* infoforcefeed.org:/var/www/infoforcefeed.org/
