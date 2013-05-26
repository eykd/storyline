# = hook

## The hook

It's just a small brass hook, screwed to the wall. \
% if this.wearing_cloak:
Useful for [hanging things](!) on it.
% else:
Your [opera cloak](!) is hanging on it.
% endif

[Continue...](pop!)

## > hanging things
{{ this.push('actions::hang up cloak') }}

## > opera cloak
{{ this.set("wearing cloak", False) }}


# = message

## The message

The message, neatly marked in the sawdust, reads...

**You have won**
