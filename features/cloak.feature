Feature: Cloak of Darkness
  An implementation of the infamous Cloak of Darkness IF spec.

  The Foyer of the Opera House is where the game begins. This empty room has doors to the south and west, also an unusable exit to the north. There is nobody else around.

  The Bar lies south of the Foyer, and is initially unlit. Trying to do anything other than return northwards results in a warning message about disturbing things in the dark.

  On the wall of the Cloakroom, to the west of the Foyer, is fixed a small brass hook.

  Taking an inventory of possessions reveals that the player is wearing a black velvet cloak which, upon examination, is found to be light-absorbent. The player can drop the cloak on the floor of the Cloakroom or, better, put it on the hook.

  Returning to the Bar without the cloak reveals that the room is now lit. A message is scratched in the sawdust on the floor.

  The message reads either "You have won" or "You have lost", depending on how much it was disturbed by the player while the room was dark.

  The act of reading the message ends the game.

  Background: Cloak of Darkness initialization
    Given a Plot definition for the Cloak of Darkness spec
    When I read the Cloak of Darkness series definitions
    Then I have a Plot with the Cloak of Darkness Series definitions
    And I can start a new Plot State
    And the stack has a length of 1

  Scenario: on_enter initialization
    Given I am in the "intro" situation of "start"
    Then the "wearing cloak" flag should be "True" (bool)
    And the last message says "Hurrying through the rainswept November night, you're glad to see the bright\nlights of the Opera House. It's surprising that there aren't more people about\nbut, hey, what do you expect in a cheap demo game...?\n\n[Onward!](Onward%21)"

  Scenario: Navigation to Cloakroom
    Given I am in the "intro" situation of "start"
    When I choose "Onward!"
    Then I am in the "foyer" situation of "rooms"
    When I choose "west"
    Then I am in the "cloakroom" situation of "rooms"
    And the stack has a length of 1

  Scenario: Messing around in the Bar
    Given I am in the "intro" situation of "start"
    When I choose "Onward!"
    Then I am in the "foyer" situation of "rooms"
    When I choose "south"
    Then I am in the "bar" situation of "rooms"
    And the stack has a length of 1

    When I choose "back out slowly"
    Then I am in the "foyer" situation of "rooms"
    And the stack has a length of 1

    When I choose "south"
    And I choose "fumble around for a light"
    Then I am in the "fumble around" situation of "actions"
    And the last message says "You fumble around in the dark, but to no avail.\n\n[Continue...](Continue...)"
