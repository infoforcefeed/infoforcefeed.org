#!/usr/bin/env bash

rsync -PazL built/* infoforcefeed.org:/var/www/infoforcefeed.org/
