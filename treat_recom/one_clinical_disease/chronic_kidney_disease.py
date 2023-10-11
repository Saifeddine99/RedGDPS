def non_critical_chronic_kidney_disease_(hba1c_records,previous_state,current_eGFR,current_UACR,med_dose_last_time):
    full_dose= "full dose"
    half_dose="half dose"
    second_or_third_med_level=['Pio', 'SU']

    proposed_med={}
    next_date="Your next check is after 3 months"
    if(previous_state=="First time"):
        if(30<=current_eGFR<45):
            proposed_med["Metformin"]=half_dose
        else:
            proposed_med["Metformin"]=full_dose
        proposed_med["SGLT2i"]=full_dose
    else:#patient is already getting treatment
        proposed_med=med_dose_last_time
        target_=6.5 ####target(previous_state,med_dose_last_time)
        current_hba1c=hba1c_records[0]

        if(current_hba1c>=target_):
            if("Metformin" in med_dose_last_time and "SGLT2i" in med_dose_last_time and len(med_dose_last_time)==2):
                if(30<=current_eGFR<45):
                    proposed_med["Metformin"]=half_dose
                else:
                    proposed_med["Metformin"]=full_dose
                proposed_med["SGLT2i"]=full_dose
                proposed_med["GLP1RA"]=full_dose
            elif ("Metformin" in med_dose_last_time and "GLP1RA" in med_dose_last_time and "SGLT2i" in med_dose_last_time and len(med_dose_last_time)==3):
                if(30<=current_eGFR<45):
                    proposed_med["Metformin"]=half_dose
                else:
                    proposed_med["Metformin"]=full_dose
                proposed_med["SGLT2i"]=full_dose
                proposed_med["GLP1RA"]=full_dose
                proposed_med["You can choose any item from this list: {}".format(second_or_third_med_level)]=full_dose
            
            elif("Metformin" in med_dose_last_time and not("Basal insulin" in med_dose_last_time) and len(med_dose_last_time)>=4 and "SGLT2i" in med_dose_last_time and "GLP1RA" in med_dose_last_time and not("DPP4i" in med_dose_last_time)):
                drugs=list(med_dose_last_time.keys())
                drugs.remove("Metformin")
                drugs.remove("SGLT2i")
                drugs.remove("GLP1RA")
                logic_drugs=1
                for item in drugs:
                    if(item not in second_or_third_med_level):
                        logic_drugs=0
                proposed_med={}
                if(logic_drugs==1):  
                    proposed_med["Basal insulin"]=full_dose
                else:
                    proposed_med["Can't recommend treatment for this case !"]=""
            
            elif("Basal insulin" in med_dose_last_time):
                proposed_med={}
                proposed_med["Basal insulin"]= full_dose
            
            else:
                proposed_med={}
                proposed_med["Can't recommend treatment for this case !"]=""

        else:
            next_date="Your next check is after 6 months"
            for drug in proposed_med:
                if (drug=="Metformin"):
                    if(30<=current_eGFR<45):
                        proposed_med[drug]=half_dose
                    else:
                        proposed_med[drug]=full_dose
                else:
                    proposed_med[drug]=full_dose
    return(proposed_med,next_date)

def critical_chronic_kidney_disease_(hba1c_records,previous_state,med_dose_last_time):
    full_dose= "full dose"
    second_or_third_med_level=['DPP4i', 'oral GLP1ra', 'SGLT2i', 'Pio', 'SU']

    proposed_med={}
    next_date="Your next check is after 3 months"
    if(previous_state=="First time"):
        proposed_med["DPP4i or GLP1RA"]=full_dose
    else:
        proposed_med=med_dose_last_time
        target_=6.5 ####target(previous_state,med_dose_last_time)
        current_hba1c=hba1c_records[0]
        if(current_hba1c>target_):
            
            if(["DPP4i"] == list(med_dose_last_time.keys()) or ["GLP1RA"] == list(med_dose_last_time.keys())):
                if("DPP4i" in med_dose_last_time):
                    proposed_med["DPP4i"]=full_dose
                else:
                    proposed_med["GLP1RA"]=full_dose
                proposed_med["Pio or Repa"]=full_dose
            
            elif(("Pio" in med_dose_last_time or "Repa" in med_dose_last_time) and ("DPP4i" in med_dose_last_time or "GLP1RA" in med_dose_last_time) and len(med_dose_last_time)==2):
                if("Repa" in med_dose_last_time):
                    second_or_third_med_level.remove("SU")
                if("GLP1RA" in med_dose_last_time):
                    second_or_third_med_level.remove("DPP4i")
                for drug in proposed_med:
                    proposed_med[drug]=full_dose
                proposed_med["You can choose any item from this list: {}".format(second_or_third_med_level)]=full_dose

            elif(not("Basal insulin" in med_dose_last_time) and ("Pio" in med_dose_last_time or ("Repa" in med_dose_last_time and not("SU" in med_dose_last_time))) and ("DPP4i" in med_dose_last_time or (("GLP1RA" in med_dose_last_time)and not("DPP4i" in med_dose_last_time))) and len(med_dose_last_time)>=3):
                drugs=list(med_dose_last_time.keys())
                logic_drugs=1
                if(("GLP1RA"in drugs and "DPP4i"in drugs) or ("Repa"in drugs and "SU" in drugs)):
                    logic_drugs=0 
                if("GLP1RA"in drugs):  
                    drugs.remove("GLP1RA")
                if("Repa"in drugs):  
                    drugs.remove("Repa")

                for item in drugs:
                    if(item not in second_or_third_med_level):
                        logic_drugs=0
                if(logic_drugs==1): 
                    proposed_med={}
                    proposed_med["Basal insulin"]=full_dose
                else:
                    proposed_med={}
                    proposed_med["Can't recommend treatment for this case !"]=""

            elif("Basal insulin" in med_dose_last_time):
                proposed_med={}
                proposed_med["Basal insulin"]= full_dose

            else:
                proposed_med={}
                proposed_med["Can't recommend treatment for this case !"]=""

        else:
            next_date="Your next check is after 6 months"
            for drug in proposed_med:
                proposed_med[drug]=full_dose
    return(proposed_med,next_date)