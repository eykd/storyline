# -*- coding: utf-8 -*-
"""Storyline HTTP server

Usage: storyline start [--listen=ADDRESS] [--debug] STORY_PATH

Options:
  -h --help             Show this screen.
  --version             Show version.
  -l --listen=ADDRESS   Address and port to listen on [default: localhost:5000]
  -d --debug            Run in DEBUG mode.
"""
import sys
import logging
import urllib

from docopt import docopt

from flask import (Flask, request, session, g, redirect,
                   url_for, abort, render_template, flash)

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler

from . import storyfile
from . import serializers
from . import turns
from . import entities


app = Flask(__name__)
plot = entities.Plot()
app.secret_key = 'foobar'

logger = logging.getLogger('http')


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/story/", methods=['GET', 'POST'])
@app.route("/story/<action>", methods=['GET'])
def story(action=None):
    logger.debug("########## Starting /story/")
    session.permanent = True
    state = session.get('state', None)
    if state is not None:
        state = serializers.MsgPackStateSerializer.loads(plot, state)

    turn = turns.TurnManager(plot, state)

    action_kwargs = {}
    if request.method == 'POST':
        if action is None:
            action = request.form.get('action', action)
        action_kwargs.update(request.form)

    if action is not None:
        action = urllib.unquote_plus(action)

    story, state = turn.take_turn(action, **action_kwargs)

    session['state'] = serializers.MsgPackStateSerializer.dumps(state)

    logger.debug("########## Fin.")

    return render_template('story.html', story=story)


@app.route("/reset/", methods=['GET'])
def reset():
    session.permanent = True
    session['state'] = u''
    del session['state']

    return redirect(url_for('story'))


class Reloader(FileSystemEventHandler):
    def __init__(self, story_path):
        self.path = story_path
        super(Reloader, self).__init__()

    def on_any_event(self, event):
        if not event.is_directory:
            logger.debug("%s changed. Reloading." % event.src_path)
            global plot
            plot = storyfile.load_plot_from_path(self.path)


def main():
    arguments = docopt(__doc__, version='Storyline HTTP v0.1')

    if arguments.get('--debug'):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stderr)
        logger.addHandler(handler)

    app.config.from_object(__name__)
    app.debug = arguments.get('--debug')

    story_path = arguments.get('STORY_PATH', '.')

    global plot
    plot = storyfile.load_plot_from_path(story_path)

    observer = Observer()
    observer.schedule(LoggingEventHandler(), path=story_path, recursive=True)
    observer.schedule(Reloader(story_path), path=story_path, recursive=True)

    observer.start()
    try:
        app.run()
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
