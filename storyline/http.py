# -*- coding: utf-8 -*-
"""Storyline HTTP server

Usage: storyline start [--listen=ADDRESS] [--debug] STORY_PATH

Options:
  -h --help             Show this screen.
  --version             Show version.
  -l --listen=ADDRESS   Address and port to listen on [default: localhost:5000]
  -d --debug            Run in DEBUG mode.
"""
import logging

from docopt import docopt

import msgpack
import markdown

from flask import (Flask, request, session, g, redirect,
                   url_for, abort, render_template, flash)


from . import states


app = Flask(__name__)
plot = states.Plot()
app.secret_key = 'foobar'


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/story/", methods=['GET', 'POST'])
@app.route("/story/<action>", methods=['GET'])
def story(action=None):
    session.permanent = True
    state = session.get('state', None)
    try:
        state = states.PlotState.from_dict(plot, msgpack.loads(state))
    except:
        state = plot.make_state()

    if request.method == 'POST':
        action = request.form.get('action', action)

    if action is not None:
        state.choose(plot, action)

    state.clear()
    session['state'] = msgpack.dumps(state.to_dict())

    story = markdown.markdown(u'\n\n'.join(state.messages) if state.messages else state.current(plot).content)

    return render_template('story.html', story=story)


def main():
    arguments = docopt(__doc__, version='Storyline HTTP v0.1')

    if arguments.get('--debug'):
        logging.basicConfig(level=logging.DEBUG)

    app.config.from_object(__name__)

    plot.load_path(arguments.get('STORY_PATH', '.'))

    app.debug = arguments.get('--debug')

    app.run()


if __name__ == "__main__":
    main()
