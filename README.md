# Hey There ! What's my Share ?

whats-my-share is a Django project which helps to track bills and other shared expenses, so that everyone gets paid back in the end.
It mainly consists of two applications :
   * [Accounts](https://github.com/arpansharma/whats-my-share/tree/main/whats_my_share/accounts) that keeps track of users and groups.
   * [Expense](https://github.com/arpansharma/whats-my-share/tree/ft/docker-config/whats_my_share/expense) that keeps track of all the expenses and their entries in a ledger.


## Requirements
### Tested with Docker version 20.10.1, build 831ebea on Ubuntu Focal 20.04 (LTS)
   * You need to have [Docker](https://www.docker.com/) installed and running on your machine.

## Steps to run whats-my-share
1. Clone this repository to your machine using the command `git clone git@github.com:arpansharma/whats-my-share.git`
2. Step into the cloned repository using the command `cd whats-my-share`
3. Once inside the project directory :
   * run command `sudo docker-compose build` to build the docker image.
   * run command `sudo docker-compose up -d` to run the container in the background.
   * run command `sudo docker-compose exec web python manage.py migrate` in order to migrate the database.
4. In order to view application logs :
   * run command `sudo docker ps -a` to list all the running containers.
   * Grab the `<container_id>` for which you need to see the logs and run command `sudo docker logs -f
    <container_id>`
5. In order to login in to the admin dashboard :
   * run command `sudo docker-compose exec web python manage.py createsuperuser` and register with desired credentials.
   * Navigate to [localhost](localhost:8000/admin) to login with the credentials.
6. In order to test the APIs :
   * import this [API Collection](https://github.com/arpansharma/whats-my-share/blob/main/Whats%20My%20Share.postman_collection.json) into Postman.
   * Create a user and authenticate a User in order to recieve a Token.
   * Use that Token in all other APIs.

# Limitations / Trade-Offs
1. Currently the project is not configured to use environment variables with Docker but can be done in the future for more flexibility.
2. It doesn't have the feature to simplify-debts across different groups for an individual person.
   * [Splitwise](https://medium.com/@mithunmk93/algorithm-behind-splitwises-debt-simplification-feature-8ac485e97688) does it in a very efficient manner.
3. It doesn't have the support to add profile/group picture or images for a bill.
   * In future this can be done through getting a signed URL from a file storage service such as S3,
    pushing the in-memory image to S3 and then saving the corresponsing URL in the database.
4. Gunicorn and Nginx are not congifured to use with Docker File.
   * We can bind gunicorn to the application port and spawn desired workers and then place Nginx on top of it to server a large number of requests.
5. Unit Tests can be added using factory-boy and pytest for covering test-cases.
