Feature: Add artist page

  Scenario: Submitting an empty artist form
    Given I'm an admin user
    When I go to the artist add page
    And I should see a form
    And I press Submit
    Then I should see error message
