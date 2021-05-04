#!/usr/bin/env bash

rsync -PazrL built/* infoforcefeed.org:/var/www/infoforcefeed.org/
