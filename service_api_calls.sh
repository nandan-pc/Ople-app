#!/bin/bash

# healthcheck ping

print_heading() {
echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo $1
echo "++++++++++++++++++++++++++++++++++++++++++++++"
}


print_operation() {
echo "**********************************************"
echo $1
echo "**********************************************"
}

print_end(){
echo "----------------------------------------------"
}

print_heading "Service Healthcheck"
curl http://localhost:5001/experiments/ping
print_end

print_heading "CRUD operations"

train_dataset_1=$PWD/services/experiments/project/tests/data/pima-indians-diabetes_train_dataset_1.csv
train_dataset_2=$PWD/services/experiments/project/tests/data/pima-indians-diabetes_train_dataset_2.csv

test_dataset_1=$PWD/services/experiments/project/tests/data/pima-indians-diabetes_test_dataset_1.csv
test_dataset_2=$PWD/services/experiments/project/tests/data/pima-indians-diabetes_test_dataset_2.csv


print_operation "Add an experiment  info and upload test and training files : Experiment 1"
curl -X POST -H "content_type:multipart/form-data" \
    -F "name=LR_pima_indians_1" \
    -F "type=classification" \
    -F "train_data=@$train_dataset_1" \
    -F "test_data=@$test_dataset_1" \
    http://localhost:5001/experiments
print_end

print_operation "Add an experiment info and upload test and training files : Experiment 2"
curl -X POST -H "content_type:multipart/form-data" -F \
 "name=LR_pima_indians_2" -F \
 "type=classification"  -F \
 "train_data=@/home/nandan/projects/test/pima-indians-diabetes.csv" \
 -F "test_data=@/home/nandan/projects/test/pima-indians-diabetes_test_dataset_2.csv" \
 http://localhost:5001/experiments
print_end

print_operation "Get experiment details with ID = 1"
curl http://localhost:5001/experiments/1
print_end


print_operation "Get details for all experiments in database"
curl http://localhost:5001/experiments
print_end

print_operation "Update Experiment with ID = 2"
curl -X PUT -H "Content-Type=multipart/form-data"\
 http://localhost:5001/experiments/2\
  -F "name=LR"\
  -F "type=cls"\
  -F "result={'accuracy': 0.1}"\
  -F "start_date=2018-09-05 21:06:41.712553"\
  -F "train_data=@/home/nandan/projects/test/pima-indians-diabetes.csv"\
  -F "test_data=@/home/nandan/projects/test/pima-indians-diabetes.csv"

print_operation "View Update changes to Experiment with ID = 2"
curl http://localhost:5001/experiments/1
print_end

print_operation "Delete Experiment with ID = 2"
curl -X DELETE http://localhost:5001/experiments/2
print_end

print_heading " Training, Testing & Prediction  \n Alogirthm: Logistic Regression \n Dataset: Pima Indians Diabetes \n Task: Classification"

print_operation "Train Experiment with ID = 1"
curl -X POST http://localhost:5001/experiments/train/1
print_end

print_operation "Test Experiment with ID = 1"
curl -X POST http://localhost:5001/experiments/test/1
print_end

print_operation "View Train and Test results for Experiment with ID = 1"
curl http://localhost:5001/experiments/1
print_end


print_operation "Predict for a Data Sample with Experiment 1 Model"
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"sample": {"pregnancies": 0, "glucose": 137, "blood_pressure": 40, "skin_thickness": 35, "insulin": 168, "bmi": 43.1, "diabetes_pedigree_function": 2.88, "age": 33}}' \
  http://localhost:5001/experiments/predict/1
print_end

