#!/bin/bash

print_heading() {
echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo $1
echo "++++++++++++++++++++++++++++++++++++++++++++++"
}

print_end(){
echo "----------------------------------------------"
}

print_heading 'Build the Services'
docker-compose -f docker-compose-dev.yml build
print_end

print_heading 'Setup Database'
docker-compose -f docker-compose-dev.yml run experiments python manage.py recreate_db
print_end

print_heading 'Test Services are working as expected'
docker-compose -f docker-compose-dev.yml run experiments python manage.py test
print_end

print_heading 'Services Up!!'
docker-compose -f docker-compose-dev.yml up -d
print_end

echo "Great! Now you are ready to use Experiment Services"