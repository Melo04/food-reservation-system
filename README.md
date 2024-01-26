## __Food Reservation System__
TSE2101 Software Engineering Fundamentals Assignment ( Trimester 1, 23/34, 2310 )

## __Compile and Run Instructions__
1. In your terminal, clone the repository by typing ```git clone https://github.com/Melo04/food-reservation-system.git```
2. After that, type in ```py -3 -m venv .venv``` to create a virtual environment
3. Type in ```.venv\Scripts\activate``` to activate the virtual environment
4. Type in ```pip install -r requirements.txt``` to install all the required packages
5. Make sure that you have [Node.js](https://nodejs.org) installed on your local machine. If not, download it from [here](https://nodejs.org/en/download/).
6. Type in ```npm install``` to install the required packages for tailwindcss
7. Type in ```touch .env``` to create a .env file in the root directory
8. In .env file, add the following lines
```
MAIL_USERNAME='abcd' (add your own mail username to enable forgot password feature else leave it blank)
MAIL_PASSWORD='abcd' (add your own mail password to enable forgot password feature else leave it blank)
STRIPE_PUBLISHABLE_KEY = pk_test_51OCfhxI9ysZrioEOxypihfuI4gL4H9QTfw1DaXMzI2U4gvr75904h6zhsjXx0QjqChZtaL60idisv9QOckZzmijW00PFlHe8DW
STRIPE_SECRET_KEY = sk_test_51OCfhxI9ysZrioEOEOZ9WsjSie9zS2WkAnQgsTRlI9UfIabM7AMovAwSWY6Toz8IWXvXyJKc4g2dTs5Fcf6H63ZJ002lOFU2MP
```
9. Type in ```flask run --debug``` to run the application

## __Credentials__
1. Parent <br>
    Username: parent1, parent2 <br>
    Password: parent123
2. Canteen Worker <br>
    Username: worker1, worker2 <br>
    Password: worker123
3. Student <br>
    Username: student1, student2 <br>
    Password: student123
4. Admin <br>
    Username: admin1, admin2 <br>
    Password: admin123

## __Stripe Checkout__
Intall Stripe by running ```pip install stripe``` in your ternimal.

__Credit cards for testing:__
1. 4242 4242 4242 4242 (always success)
2. 4000 0000 0000 0002 (always declined)

For full list of card numbers, visit https://stripe.com/docs/testing?testing-method=card-numbers#cards.

## __Group Members__
1. 1201103207 - Melody Koh Si Jie
2. 1201103431 - Chay Wen Ning
3. 1211307724 - Goh Shi Yi
4. 1211308798 - Choo Yun Yi