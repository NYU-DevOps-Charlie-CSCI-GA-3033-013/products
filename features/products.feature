Feature: The products service back-end
    As a Products Owner
    I need a RESTful catalog service
    So that I can keep track of all my products

Background:
    Given the server is started
 
Scenario: The server is running
    When I visit the "home page"
    Then I should see "product Demo REST API Service"
    Then I should not see "404 Not Found"

Scenario: List all products
    When I visit "/products"
    Then I should see "iPhone 7"
    And I should see "ActiveCare Hair Dryer"
    And I should see "Apple MacBook Pro"

Scenario: Update a product
    When I retrieve "/products" with id "1001"
    And I change "category" to "big dog"
    And I update "/products" with id "1001"
    Then I should see "big dog"

Scenario: Delete a product
    When I visit "/products"
    Then I should see "iPhone 7"
    And I should see "Apple MacBook Pro"
    When I delete "/products" with id "1001"
    And I visit "/products"
    Then I should see "iPhone 7"
    And I should not see "Apple MacBook Pro"
