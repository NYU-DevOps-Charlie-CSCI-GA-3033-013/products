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
	Given the following products
        | id | name                  | category             | discontinued | price |
        |  1 | iPhone 7              | electronics          | False        | 800   |
        |  2 | ActiveCare Hair Dryer | bathroom appliances  | False        | 200   |
        |  2 | Apple MacBook Pro     | electronics          | False        | 2100  |
    	When I visit "/products"
    	Then I should see "iPhone 7"
    	And I should see "ActiveCare Hair Dryer"
    	And I should see "Apple MacBook Pro"



