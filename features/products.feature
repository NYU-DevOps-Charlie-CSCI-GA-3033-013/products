Feature: The products service back-end
    As a Products Owner
    I need a RESTful catalog service
    So that I can keep track of all my products

Background:
    Given the server is started
    Given the following products
        | id | name                  | category             | discontinued | price |
        |  1 | iPhone 7              | electronics          | False        | 800   |
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


Scenario: Update a product
	When I retrieve "/products" with id "1"
	    And I change "category" to "phones"
	    And I update "/products" with id "1"
	    And I retrieve "/products" with id "1"
	    Then I should see "phones"
        

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


Scenario: Search for a product with discontinued status
    When I search "/products" with discontinued "False"
        Then I should see "iPhone 7"
        And I should see "ActiveCare Hair Dryer"
        And I should see "Apple MacBook Pro"
        