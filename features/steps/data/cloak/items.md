# = hook

## The hook

It's just a small brass hook, screwed to the wall.
{% if I.am("wearing cloak") %}
Useful for [hanging things](!) on it.
{% else %}
Your [opera cloak](!) is hanging on it.
{% endif %}

[Continue...](pop!)

## > hanging things
{{ push('actions::hang up cloak') }}

## > opera cloak
{{ I.am("wearing cloak", True) }}


# = message

## The message

The message, neatly marked in the sawdust, reads...

**You have won**

{% if I.fumbled %}
But you fumbled {{ my.fumbled }} times!
{% endif %}

[Start over.](reset!)


# = Opera Cloak

A handsome cloak, of velvet trimmed with satin, and slightly spattered with
raindrops. Its blackness is so deep that it almost seems to suck light from the
room.

## > on_title

A velvet opera cloak{% if I.am('wearing cloak') %} (being worn) {% endif %}
