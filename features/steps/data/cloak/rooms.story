# = foyer

## Foyer of the Opera House

You are standing in a spacious hall, splendidly decorated in red and gold, with glittering chandeliers overhead. The entrance from the street is to the [north](select!outside), and there are doorways [south](select!bar) and [west](select!cloakroom).


# = cloakroom

## Cloakroom

The walls of this small room were clearly once lined with hooks, though now only [one](push!items::hook) remains. The exit is a door to the [east](select!foyer).


# = bar

% if this.get("wearing cloak"):
## Darkness

It is pitch dark, and you can't see a thing. You could [back out slowly](!) or [fumble around for a light](!).
% else:
## Foyer Bar

The bar, much rougher than you'd have guessed after the opulence of the foyer to the north, is completely empty. There seems to be some sort of [message](!) scrawled in the sawdust on the floor.
% endif

## > back out slowly
{{ select('foyer') }}

## > fumble around for a light
{{ push('actions::fumble around') }}

## > message
{{ push('items::message') }}


# = outside

You've only just arrived, and besides, the weather outside seems to be getting worse. Best to [stay inside](select!foyer)
