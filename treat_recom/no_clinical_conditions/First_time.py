medium_dose="medium dose"
full_dose= "full dose"
second_or_third_med_level=['DPP4i', 'SGLT2i', 'oral GLP1ra', 'Pio', 'SU']

def first_time(current_hba1c,symptoms):
    proposed_med={}
    if(current_hba1c<7.0):
        proposed_med["nonpharmacological therapy"]="No specific dose"
    elif (current_hba1c>=7 and current_hba1c<=9):
        proposed_med["Metformin"]=medium_dose
    else:
        proposed_med["Metformin"]=full_dose
        if(symptoms=='YES'):
            proposed_med["Basal insulin"]=full_dose
        else:
            proposed_med["You can choose any item from this list: {}".format(second_or_third_med_level)]=full_dose

    return(proposed_med)