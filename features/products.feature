Feature: The products service back-end
    As a Products Owner
    I need a RESTful catalog service
    So that I can keep track of all my products

Background:
    Given the server is started
    Given the following products
        | id | name                  | category             | discontinued | price |
        |  1 | iPhone 7              | electronics          | True         | 800   |
        |  2 | ActiveCare Hair Dryer | bathroom appliances  | False        | 200   |
        |  3 | Apple MacBook Pro     | electronics          | False        | 2100  |

 
Scenario: The server is running
    When I visit the "home page"
    Then I should see "product Demo REST API Service"
    Then I should not see "404 Not Found"

Scenario: List all products
    	When I visit "/products"
    	Then I should see "iPhone 7"
    	And I should see "ActiveCare Hair Dryer"
    	And I should see "Apple MacBook Pro"

Scenario: Create a product
	When I post "/products" with name "Blender", category "kitchen appliances", discontinued "false", and price "120"
		Then I should see "Blender" 
		And I should see "kitchen appliances"
		And I should see "false"
		And I should see "120"
		When  I visit "/products"
		Then I should see "Blender" 

Scenario: Update a product
	When I retrieve "/products" with id "1"
	    And I change "category" to "phones"
	    And I update "/products" with id "1"
	    And I retrieve "/products" with id "1"
	    Then I should see "phones"

Scenario: Delete a product
	When I visit "/products"
	Then I should see "iPhone 7"
	And I should see "Apple MacBook Pro"
	When I delete "/products" with id "3"
	And I visit "/products"
	Then I should see "iPhone 7"
	And I should not see "Apple MacBook Pro"

Scenario: Search for a product with price
    When I search "/products" with price "800"
        Then I should see "iPhone 7"


Scenario: Search for a product with price range
    When I search "/products" with minprice "100" and maxprice "1000"
        Then I should see "iPhone 7"
        And I should see "ActiveCare Hair Dryer"


Scenario: Search for a product with category
    When I search "/products" with category "electronics"
        Then I should see "iPhone 7"
        And I should see "Apple MacBook Pro"

Scenario: Search for a product with name
    When I search "/products" with name "iPhone 7"
        Then I should see "iPhone 7"
        And I should not see "Apple MacBook Pro"

Scenario: Search for a product with discontinued status
    When I search "/products" with discontinued "False"
        Then I should not see "iPhone 7"
        And I should see "ActiveCare Hair Dryer"
        And I should see "Apple MacBook Pro"
        