Feature: Situation
  Example:

  We start with a basic set of navigation situations. These Situations
  pass control to each other in turn. If the Situation's Guard fields
  pass, the Situation activates. As each Situation activates, it has an
  Effect on the State of the story.

  Situations may Push new Series onto the Plot in a new Slot. Situations
  may Pop the current Slot off the Stack. A Situation may Replace a new
  Situation from the current Series in the current Slot.

  Situations have scripts that run in response to various events:

  - accept: when the Guard field accepts the current state.
  - activate: when the Situation activates.
  - enter: when the state engine enters the Situation.
  - tap: when the Situation is tapped.
  - exit: when the state engine exits the Situation.
  - deactivate: when the Situation is deactivated.
  - reject: when the Guard field rejects the current state.

  Situations may also trigger and respond to custom events.

  # Scenario: Series of Navigation Situations
  #   Given a Navigation Series
