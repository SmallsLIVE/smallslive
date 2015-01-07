Feature: Add artist page

  Scenario: Submitting an empty artist form
    Given I'm an admin user
    When I go to the artist add page
    And I should see a form
    And I press Submit
    Then I should see an error message

  Scenario: Submitting a valid artist
    Given I'm an admin user
    When I go to the artist add page
    And I should see a form
    And I input Spike for first_name
    And I input Wilner for last_name
    And I input spike@example.com for email
    And I choose no_invite for invite_type radio button
    And I press Submit
    Then the text "Artist Spike Wilner successfully added" should be present
