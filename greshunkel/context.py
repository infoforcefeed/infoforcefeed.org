from greshunkel.build import POSTS_DIR
from greshunkel.utils import parse_variable
from greshunkel.slimdown import Slimdown

import subprocess
from os import listdir

DEFAULT_LANGUAGE = "en"
# Question: Hey qpfiffer, why is this indented all weird?
# Man I don't know leave me alone.
BASE_CONTEXT = {
    "PROJECTS": [
        {
            "title": "OlegDB",
            "description": "The ugly duckling database of champions.",
            "link": "https://olegdb.org"
        },
        {
            "title": "logpurge",
            "description": "Logarhythmically purge backup files in order of importance. More recent and importan files are kept in closed intervals, while older files are removed.",
            "link": "https://github.com/nijotz/logpurge"
        },
        {
            "title": "GRESHUNKEL",
            "description": "The static site generator that built this and the OlegDB website. Written in python with much leering and hatred.",
            "link": "https://github.com/infoforcefeed/OlegDB-Website/tree/master/greshunkel"
        },
        {
            "title": "shitstream",
            "description": "Radio music service and streaming.",
            "link": "https://github.com/nijotz/shitstream"
        },
        {
            "title": "Goat Tower",
            "description": "Ambitious and horrifying MUD.",
            "link": "https://github.com/infoforcefeed/goat-tower"
        },
        {
            "title": "tenyks",
            "description": "Pluggable, extensible, concurrent multi-threaded IRC bot.",
            "link": "https://github.com/kyleterry/tenyks"
        },
        {
            "title": "#metaforcefeed",
            "description": "reddit-esque task-tracker. Designed to test OlegDB as a backend.",
            "link": "http://meta.infoforcefeed.org/"
        },
        {
            "title": "Dyno",
            "description": "A basic blog framework in shell. Enough movement to get you where you need to go.",
            "link": "https://github.com/colby/dyno"
        },
        {
            "title": "Entropy Meter",
            "description": "An entropy meter that measures Jira chaos via the Dashing web framework. Built in Ruby for some reason.",
            "link": "https://github.com/nijotz/entropy-meter"
        },
    ],
    "TALKS": [
        {
            "title": "Shitstream Presentation",
            "description": "Ad-hoc presentation nijotz gave on his <a href=\"/projects.html\">shitstream</a> project. Link is to full talk, 114MB.",
            "img": "./static/img/nick_shitstream_preview.jpg",
            "talk_link": "./static/vid/nick_shitstream_2014-05-24.webm"
        },
        {
            "title": "Golang General",
            "description": "Semi-prepared talk on Go, go-routines and interesting finds while porting tenyks. Vid is ~200MB.",
            "img": "./static/img/kyles_go_talk.jpg",
            "talk_link": "./static/vid/kyles_go_talk_2014_07_05.webm"
        }
    ],
    "ABOUTS": [
        "#infoforcefeed is on irc.freenode.net. Come join us.",
        "You know suckless? Well we essentially suckmore sometimes.",
        "We all like to code and we each have our favorite languages, but Python and C seem to be the most popular among the group.",
        "We have dreams of a crypto-anarchist-potato-tomato farm.",
        "This \"about\" is a bullet point list that even YOU can contribute to. JUST GRESHUNKEL IT."
    ]
}

def build_blog_context(default_context):
    default_context['POSTS'] = []

    slimmin = Slimdown()
    for post in listdir(POSTS_DIR):
        if not post.endswith(".markdown"):
            continue

        new_post = {}
        dashes_seen = 0
        reading_meta = True
        muh_file = open(POSTS_DIR + post)
        all_text = ""
        for line in muh_file:
            stripped = line.strip()
            if stripped == '---':
                dashes_seen += 1
                if reading_meta and dashes_seen < 2:
                    continue
            elif reading_meta and dashes_seen >= 2:
                reading_meta = False
                continue

            if reading_meta and ':' in line:
                split_line = stripped.split(":")
                new_post[split_line[0]] = split_line[1]

            if not reading_meta:
                all_text += line

        new_post['content'] = slimmin.render(all_text)
        new_post['preview'] = new_post['content'][:300] + "&hellip;"
        new_post['link'] = "blog/{}".format(post.replace("markdown", "html"))
        new_post['filename'] = post
        new_post['built_filename'] = post.replace("markdown", "html")
        default_context['POSTS'].append(new_post)
        muh_file.close()
    default_context['POSTS'] = sorted(default_context['POSTS'], key=lambda x: x["date"], reverse=True)
    return default_context

def build_doc_context(default_context):
    include_dir = "./OlegDB/include/"
    output = subprocess.check_output("cd OlegDB && git tag --list", shell=True)
    default_context['docs'] = {}
    default_context['ALL_VERSIONS'] = []
    versions = [output.strip()]
    versions.append("master")

    for version in versions:
        print "Checking out {}".format(version)
        cmd = "cd OlegDB && git checkout {} &> /dev/null".format(version)
        subprocess.call(cmd, shell=True)
        headers = ["oleg.h", "defs.h"]
        headers = map(lambda x: "{}/{}".format(include_dir, x), headers)
        version_context = {}
        for header_file in headers:
            try:
                oleg_header = open(header_file)
            except IOError as e:
                print e
                continue

            docstring_special = ["DEFINE", "ENUM", "STRUCT", "DESCRIPTION",
                    "RETURNS", "TYPEDEF"]

            reading_docs = False
            raw_code = ""
            doc_object = {}

            for line in oleg_header:
                docline = False
                stripped = line.strip()
                if stripped == '*/':
                    continue

                # ThIs iS sOmE wEiRd FaLlThRouGh BuLlShIt
                if reading_docs and stripped.startswith("/*"):
                    raise Exception("Yo I think you messed up your formatting. Read too far.")
                if "xXx" in line and "*" in stripped[:2]:
                    (variable, value) = parse_variable(stripped)

                    docline = True
                    if not reading_docs:
                        doc_object["name"] = value
                        doc_object["type"] = variable
                        doc_object["params"] = []
                        reading_docs = True
                    else:
                        if variable in docstring_special:
                            # SpEcIaL
                            doc_object[variable] = value
                        else:
                            doc_object["params"].append((variable, value))
                if reading_docs and not docline and stripped != "":
                    raw_code = raw_code + line
                if stripped == "" and reading_docs:
                    reading_docs = False
                    doc_object["raw_code"] = raw_code
                    if version_context.get(doc_object["type"], False):
                        version_context[doc_object["type"]].append(doc_object)
                    else:
                        version_context[doc_object["type"]] = [doc_object]
                    doc_object = {}
                    raw_code = ""

            oleg_header.close()

        key_raw_code = [x for x in version_context['DEFINE'] if x['name'] == 'KEY_SIZE'][0]['raw_code']
        version_raw_code = [x for x in version_context['DEFINE'] if x['name'] == 'VERSION'][0]['raw_code']
        extracted_ks = key_raw_code.split(' ')[2].strip()
        extracted_version = version_raw_code.split(' ')[2].strip()
        extracted_version = extracted_version.replace('"', '')
        if version == 'master':
            default_context['EXTRACTED_KEY_SIZE'] = extracted_ks
            default_context['EXTRACTED_VERSION'] = extracted_version
        default_context['docs'][extracted_version] = version_context
        default_context['ALL_VERSIONS'].append(extracted_version)

    return default_context
