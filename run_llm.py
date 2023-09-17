import flaskapp.ml.llm as llm


# q = "Create a table named patient_test_1 with patients that are between 20 and 30 years old based on demographics and have a BMI between 20 and 25. It should contain SEQN, age, BMI, height and weight."


# q = "Create a table named patient_test_2 with patients that are male and have a BMI between 20 and 25. The table should include any sports related survey answers. The table should have the following columns: SEQN, patient age, patient BMI and all sport survey answers."

q = "Create a table named patient_test_3 with patients between the ages of 20 and 30 based on demographics. The table should include body measurements of height, weight, waist circumference and hip circumference. It should also have PAQ670 and PAQ655 from the physical activity survey"


# q = "Create a table named patient_aggregate that contains the average BMI of patients based on the patient measurement source table for each age between 20 and 30 based on demographics. The aggregate table should have the following columns: age, average BMI."

# q = "Create a new table named combined_patients which contains only the SEQN, age, and BMI columns for patients that are in the patient_test_1 table and patient_test_2 table."

llm.create_table(q)
