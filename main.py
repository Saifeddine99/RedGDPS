import streamlit as st
import pymongo as py
import datetime

st.set_page_config(page_title="RedGDPS", page_icon=":hospital:", layout="centered")

myclient=py.MongoClient("mongodb://localhost:27017")
#Relating data to "clinical_data_ssp"
medical_data_coll=myclient["Clinical_database"]["Medical data"]
medical_hist_coll=myclient["Clinical_database"]["Medical history"]

#----------------------------------------------------------------------------
# For the moment we will suppose that the login process is working well and we're getting the user's UID successfully.
# So instead of charging the UID from demographic DB, the below instructions allow user to manual enter the UID.
st.subheader("UUID:")
uuid=st.text_input("enter your UUID:",label_visibility ="collapsed")
if len(uuid)==0:
    st.warning(": You entered nothing !" ,icon="⚠️")
else:
    st.write("#")
    #--------------------------------------------------------------------------------------------
    # Here we'll check the existance of this UID in the clinical data db:
    # "Previous state" is an imporant variable that allows us to know the number of previous uses:
    occurence=medical_data_coll.count_documents({"uuid":uuid})
    if occurence==0:
        previous_state="First time"
    elif occurence==1:
        previous_state="Second time"
    else:
        previous_state="Two previous times or more"
    #---------------------------------------------------------------------------------------------
    st.write("occurence: ",occurence)
    st.write("previous_state: ",previous_state)
    st.markdown("""---""")
    #--------------------------------------------------------------------------------------------
    from clinical_data_form import clinical_data_
    current_HbA1c,symptoms,current_BMI,height,weight,current_eGFR,current_UACR,CVRFs,frailty,heart_failure,established_CVD,hepatic_steatosis,strokes=clinical_data_()
    #--------------------------------------------------------------------------------------------
    #Here we'll extract the user's current drugs from database + his previous HbA1c records:
    current_drugs={}
    if previous_state!="First time":
        extracted_medication_list = medical_data_coll.find_one(
        {'uuid': uuid},
        sort=[( '_id', py.DESCENDING )]
        )["medication list"]
        for drug_json_file in extracted_medication_list:
            drug=drug_json_file["content"][0]["items"][0]["description"]["items"][0]["value"]["value"]
            dose=drug_json_file["content"][0]["items"][0]["description"]["items"][2]["items"][3]["value"]["value"]
            current_drugs[drug]=dose
    #---------------------------------------------------------------------------------------------------------------
    #Here we'll extract the user's previous HbA1c records from database:
    hba1c_records=[current_HbA1c]
    if previous_state=="Second time":
        extracted_hba1c_records_list = medical_hist_coll.find_one(
        {'uuid': uuid},)["analytics"][0][0]
        previous_hba1c=extracted_hba1c_records_list["content"][0]["data"]["events"][0]["data"]["items"][6]["items"][2]["value"]["magnitude"]
        hba1c_records=[current_HbA1c,previous_hba1c]

    if previous_state=="Two previous times or more":
        cursor = medical_hist_coll.find({'uuid': uuid}).sort("_id", py.DESCENDING).limit(2)
        hba1c_list=[]
        # Iterate through the results
        for document in cursor:
            hba1c_list.append(document)
        
        previous_hba1c=hba1c_list[0]["analytics"][0][0]["content"][0]["data"]["events"][0]["data"]["items"][6]["items"][2]["value"]["magnitude"]
        before_previous_hba1c=hba1c_list[1]["analytics"][0][0]["content"][0]["data"]["events"][0]["data"]["items"][6]["items"][2]["value"]["magnitude"]
        hba1c_records=[current_HbA1c, previous_hba1c, before_previous_hba1c]
    #--------------------------------------------------------------------------------------------
    st.markdown("""---""")
    st.write("#")
    #Here we'll test if form is filled correctly or not:    
    if (current_HbA1c>0) and (current_eGFR>0) and (current_UACR>0) and (current_BMI>0):
        from treat_recom.main_treat_recom import main_get_treat
        from treat_recom.new_medications import new_med
        #This function determines the new recommended treatment + next checking date
        proposed_med,next_date=main_get_treat(frailty,heart_failure,established_CVD,hepatic_steatosis,strokes,symptoms,current_UACR,current_eGFR,current_BMI,current_drugs,hba1c_records,CVRFs,previous_state)
        #This function displays the new recommended treatment + next checking date
        therapeutic_precautions=["Nutrition","Physical activity","self-management education and support"]
        new_med(proposed_med, next_date, therapeutic_precautions)
        col1, col2, col3 = st.columns([4,2,3])
        with col2:
            #This is a download button that allows to download the created new treatment file
            save_to_db_button = st.button('Save to database')

        if save_to_db_button:
            from treat_recom.saving_todb_preprocessing import save_symptoms,save_laboratory_test_results,save_bmi,save_problem_list,save_risk_factors,save_medication_list
            
            laboratory_test_results_list = save_laboratory_test_results(current_HbA1c,current_eGFR,current_UACR)
            json_object_bmi = save_bmi(current_BMI,height,weight)
            problem_list = save_problem_list(frailty,heart_failure,established_CVD,hepatic_steatosis,strokes)
            risk_factors = save_risk_factors(CVRFs)
            medication_list = save_medication_list(proposed_med)
            json_object_encounter_symptoms = save_symptoms(symptoms)

            current_date="<"+str(datetime.date.today())+">"

            medical_data_dict={
                "uuid": uuid,
                "check date": current_date,
                "problem list": problem_list,
                "risk factors": risk_factors,
                "medication list": medication_list,
                "therapeutic precautions": therapeutic_precautions,
                "symptoms": json_object_encounter_symptoms,
            }

            medical_history_dict={
                "uuid": uuid,
                "check date": current_date,
                "analytics": [laboratory_test_results_list, json_object_bmi],
            }

            medical_data_coll.insert_one(medical_data_dict)
            medical_hist_coll.insert_one(medical_history_dict)

            st.write("#")
            st.success(": File saved well" ,icon="✅")
        
    else:
        st.error(
            ": One of the values you entered is invalid, Please check them carefully!",icon="⛔"
            )