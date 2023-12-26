## __Food Reservation System__

## __How to run the web app__
1. In your terminal, clone the repository by typing ```git clone https://github.com/Melo04/food-reservation-system.git```
2. After that, type in ```py -3 -m venv .venv``` to create a virtual environment
3. Type in ```.venv\Scripts\activate``` to activate the virtual environment
4. Type in ```pip install -r requirements.txt``` to install all the required packages
5. Type in ```flask run --debug``` to run the web app
6. Type in ```touch .env``` to create a .env file
7. In .env file, add the following lines
```
MAIL_USERNAME='abcd'
MAIL_PASSWORD='abcd'
STRIPE_PUBLISHABLE_KEY = pk_test_51OCfhxI9ysZrioEOxypihfuI4gL4H9QTfw1DaXMzI2U4gvr75904h6zhsjXx0QjqChZtaL60idisv9QOckZzmijW00PFlHe8DW
STRIPE_SECRET_KEY = sk_test_51OCfhxI9ysZrioEOEOZ9WsjSie9zS2WkAnQgsTRlI9UfIabM7AMovAwSWY6Toz8IWXvXyJKc4g2dTs5Fcf6H63ZJ002lOFU2MP
```

## __Credentials__
1. Parent <br>
    id: parent1, parent2, parent3 <br>
    Password: parent123
2. Canteen Worker <br>
    id: worker1, worker2, worker3 <br>
    Password: worker123
3. Student <br>
   id: student1, student2, student3 <br>
   Password: student123
4. Admin <br>
   id: admin1, admin2, admin3 <br>
    Password: admin123

## __Stripe Checkout__
Intall Stripe by running ```pip install stripe``` in your ternimal.

__Credit cards for testing:__
1. 4242 4242 4242 4242 (always success)
2. 4000 0000 0000 0002 (always declined)

For full list of card numbers, visit https://stripe.com/docs/testing?testing-method=card-numbers#cards.

## __Group Members__
1. Melody Koh Si Jie
2. Chay Wen Ning
3. Goh Shi Yi
4. Choo Yun Yi