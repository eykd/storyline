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

from docopt import docopt

import msgpack
import markdown
from typogrify.filters import typogrify

from flask import (Flask, request, session, g, redirect,
                   url_for, abort, render_template, flash)

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler

from . import states


app = Flask(__name__)
plot = states.Plot()
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
        state = msgpack.loads(state)
    try:
        state = states.PlotState.from_dict(plot, state)
        state.clear()
    except:
        state = plot.make_state()

    if request.method == 'POST':
        if action is None:
            action = request.form.get('action', action)
        state.trigger(plot, action, **request.form)
    else:
        if action is not None:
            state.choose(plot, action)

    if state.messages:
        story_text = u'\n\n'.join(m for m in state.messages
                                  if m is not None and m.strip())
    else:
        story_text = state.current(plot).content
    logger.debug("#### The Story:\n%s", story_text)
    story_text = markdown.markdown(story_text)
    story = typogrify(story_text)
    session['state'] = msgpack.dumps(state.to_dict())

    logger.debug("########## Fin.")

    return render_template('story.html', story=story)


@app.route("/reset/", methods=['GET'])
def reset():
    session.permanent = True
    session['state'] = u''
    del session['state']

    return redirect(url_for('story'))


class Reloader(FileSystemEventHandler):
    def __init__(self, plot, story_path):
        self.plot = plot
        self.path = story_path
        super(Reloader, self).__init__()

    def on_any_event(self, event):
        if not event.is_directory and event.src_path.endswith('.story'):
            logger.debug("%s changed. Reloading." % event.src_path)
            self.plot.load_path(self.path)


def main():
    arguments = docopt(__doc__, version='Storyline HTTP v0.1')

    if arguments.get('--debug'):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stderr)
        logger.addHandler(handler)

    app.config.from_object(__name__)
    app.debug = arguments.get('--debug')

    story_path = arguments.get('STOROY_PATH', '.')

    plot.load_path(story_path)

    observer = Observer()
    observer.schedule(LoggingEventHandler(), path=story_path, recursive=True)
    observer.schedule(Reloader(plot, story_path), path=story_path, recursive=True)

    observer.start()
    try:
        app.run()
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
