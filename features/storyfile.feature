Feature: Story file
  We store a series of situations in a `.story` file.

  Scenario: reading a .story definition
    Given a small navigation story
      """
      This series describes the layout of a small village.

      # = public_house

      The inn where visitors to the village stay. All the men congregate in the hall in the evenings, after the day's labors are done.


      # = main_street

      The main street of the village. Shops and a blacksmith. Horses and carts.


      # = side_street

      ## % This is a comment.

      A side street. Many tradesmen operate their businesses off this street. Shingles hang above each door.

      ## > on_enter
      ## % This is a directive for when the situation is entered.
      foo = 1
      """
    When we read the file
    Then we get a Series object as a result
    And the Series has 3 situations
    And we can access the side_street Situation by name
    And the side_street Situation has the content "A side street. Many tradesmen operate their businesses off this street. Shingles hang above each door."
    And the side_street Situation has an on_enter directive of "foo = 1"
