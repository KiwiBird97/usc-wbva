import streamlit as st

import datetime
from datetime import date

import pandas as pd
import sys
from lxml import etree
import requests
import json
from bs4 import BeautifulSoup
import random
import numpy as np

database_name = 'wbva-8071c'

def about_ot():
    content = requests.get('https://catalogue.usc.edu/preview_entity.php?catoid=14&ent_oid=2977')
    soup = BeautifulSoup(content.content, 'html.parser')
    list_of_info = []
    for data in soup.find_all("a"):
        list_of_info.append(data.get_text())

    string = ''

    string = string+'\nDepartment email: ' + list_of_info[185]
    email = string

    return email
    
def pd_to_list(pd_object):
    pd_object=pd_object.to_dict('split')
    pd_list=pd_object['data'][0]
    return pd_list

def courses(year, semester, subject):

    df = pd.DataFrame(columns=['Course Name', "Section", "Type", "Time", "Days", "Registered", "Instructor"])

    # OT classes are only available in the Spring and Fall semesters.
    if semester == 'Spring':
        semester = 1
    elif semester == 'Fall':
        semester = 3

    # Example: Spring 2022 is denoted as 20221.
    content = requests.get('https://classes.usc.edu/term-' + str(year) + str(semester) + '/classes/' + str(subject) + '/')
    soup = BeautifulSoup(content.content, 'html.parser')

    course_table=soup.find_all("div", class_="course-id")

    course_names=[]
    for course_element in course_table:
        name = course_element.find("a", class_="courselink")
        course_names.append(name.get_text())
    df['Course Name']=course_names

    html = pd.read_html('https://classes.usc.edu/term-' + str(year) + str(semester) + '/classes/' + str(subject) + '/', header = 0)

    list_of_data = []
    for index in range(len(html)):
        x = html[index].loc[:,["Section", "Type", "Time", "Days", "Registered", "Instructor"]]
        list_of_data.append(pd_to_list(x))

    # transpose this list of lists first.
    list_of_data_transposed = []
    for index_1 in range(len(list_of_data[0])):
        list_of_elements = []
        for index_2 in range(len(list_of_data)):            
            list_of_elements.append(list_of_data[index_2][index_1])
        list_of_data_transposed.append(list_of_elements)

    # Finally, put the transposed data into a dataframe
    df["Section"] = list_of_data_transposed[0]
    df["Type"] = list_of_data_transposed[1]
    df["Time"] = list_of_data_transposed[2]
    df["Days"] = list_of_data_transposed[3]
    df["Registered"] = list_of_data_transposed[4]
    df["Instructor"] = list_of_data_transposed[5]

    return df

def get_list_of_courses_offered(pandas_df):
    course_names = pandas_df['Course Name'].tolist()
    course_num = []

    for course in course_names:
        course = course.split(':')[0]
        if "Crosslist" in course:
            course = course.replace("Crosslist ","")
        course_num.append(course)
    
    return course_num

# Create a dictionary of courses and their information.
# This operation requires get_list_of_courses_offered, on the above cell.
def course_info_dict(year, semester, subject, pandas_df):
    
    # These types of classes aren't offered in the Summer semester.
    if semester == 'Spring':
        semester = 1
    elif semester == 'Fall':
        semester = 3
    
    # The URL is a string. All other factors must be converted into strings.
    content = requests.get('https://classes.usc.edu/term-' + str(year) + str(semester) + '/classes/' + str(subject) + '/') #change this
    soup = BeautifulSoup(content.content, 'html.parser')

    course_info = soup.find_all("div", class_ = "course-details")

    course_info_list = []
    for course_element in course_info:
        info=course_element.find("div", class_ = "catalogue")
        course_info_list.append(info.get_text())

    list_of_courses = get_list_of_courses_offered(pandas_df)

    course_info_dict = {}

    for index in range(len(list_of_courses)):
        course_info_dict[list_of_courses[index]] = course_info_list[index]
        
    return course_info_dict

def progress():
    courses_taken = st.text_area('Which courses have you taken (or you are currently taking) since your first semester?')
    
    return courses_taken


def main():
    


    st.title('Report & Watch: A Virtual Assistant for Well-Being and Crisis Intervention')
    st.subheader('By Kelvin Dean (DSCI 551)')
    st.write("This an app that helps USC students who are at risk of failure try to bounce back and have another chance at success, particularly when it comes to personal difficulties.")


    st.subheader("Motivations")
    st.write("The at-risk status of students is of significant importance in academics to identify those who have academic deficiencies. It is generally understood that students who are academically deficient fail one or more assignments or exams or do not attend class as often. However, there may be times when personal difficulties cause academic deficiencies. As yet, there are no systematic investigations of the relationship between deficiency status and emotional challenges. Our motivation for creating the WBCIVA (Well-Being and Crisis Intervention Virtual Assistant) is to help students find a better and more efficient plan to succeed in their academic careers.")

    st.header("First things first.")
    st.subheader("This form is not to be use to report an emergency.")
    st.write("If this is a medical or psychological emergency, please contact the Department of Public Safety (DPS) at 213-740-4321. You will receive a response from them within 72 hours.")

    accept_terms = st.checkbox('I accept the terms above and understand that the form I am submitting is not for an emergency.')

    if accept_terms == True:

        idx = random.randint(0,9999999999)
        inquiry_number = idx

        st.header("About You")
        st.subheader("First things first.")
        st.write("Before we get started, please tell us some basic information.")
        st.caption("Required fields are marked with a *.")

        first_aware = ''
        description = ''
        # input_dict = {}
        usc_email = ''
        class_standing = ''

        data_confirm = False
        data_submit = False

        courses_taken = ''
        interests = {}
        at_risk_classes = {}
        at_risk_reasons = {}
        follow_up = {}
        next_step = {}


        course_selection = {}
        

        user = st.selectbox("Is this for you or for another student? *", ('', 'Myself', 'Another student'))

        importance = 'Low'
        if user != '':
            if user == 'Myself':

                importance = 'Low'

                # Name
                your_name_input = st.text_input('What is your name? *')

                student_status = st.selectbox('Which type of student are you? *', ('', 'Undergraduate student', 'Graduate student', 'Law student', 'Alumni', 'Other'))

                usc_email_input = st.text_input('What is your USC email? *') #use upsert incase someone wants to use this another semester

                # Added support for alumni students
                if student_status != '':
                    if usc_email_input[::-1][:8] != 'ude.csu@' and student_status != 'Alumni':
                        st.error('Please input a valid USC email.')
                    elif usc_email_input[::-1][:15] != 'ude.csu.inmula@' and student_status == 'Alumni':
                        st.error('Please input a valid USC alumni email.')
                
                usc_email = usc_email_input
                

                #background
                list_of_disabilities=['Autism', 'Deaf-blindness', 'Deafness', 'Emotional disturbance', 'Hard of hearing', 
                                    'Intellectual disabilities', 'Orthopedic impairment', 'Specific learning disability', 'Speech or language impairment',
                                    'Traumatic brain injury', 'Visual impairment', 'Other', 'None']
                disability_info = st.multiselect('Do you have any of the following disabilities?', list_of_disabilities, default = [])


                #class standing
                class_standing = st.selectbox('Which semester are you currently in? *', ('', 'Incoming Student', 
                                                                                '1st Semester', '2nd Semester', '3rd Semester',
                                                                                '4th Semester', '5th Semester', '6th Semester',
                                                                                '7th Semester', '8th Semester', 'Beyond 8th Semester', 'Graduated'))
                if class_standing == 'Incoming Student':
                    courses_taken = 'N/A'
                else:
                    courses_taken = progress()
                gpa = st.number_input('What is your current GPA?', value = 3.0, min_value = 0.00, max_value = 4.00)


                if (class_standing == '4th Semester' or class_standing == '5th Semester' or class_standing == '6th Semester'
                    or class_standing == '7th Semester' or class_standing == '8th Semester' or class_standing == 'Beyond 8th Semester'):
                    last_semester = st.selectbox('Will this be your final semester?', ('', 'Yes', 'No', 'Not sure'))
                elif (class_standing == 'Graduated'):
                    last_semester = 'Yes'
                else:
                    last_semester = 'No'

                # Secondary Key: At-Risk status
                at_risk_status = st.selectbox('Are you currently at risk of failure in one or more classes? *', ('', 'Yes', 'No'))

                if at_risk_status == "Yes":
                    first_aware_picker = st.date_input("When were you first aware of this concern?", min_value = datetime.date(2007, 1, 1), max_value = datetime.date(2037, 12, 31))
                    first_aware = first_aware_picker.strftime('%Y/%m/%d')
                    at_risk_classes = st.text_area('Please tell us the classes you may be failing in.')
                    at_risk_reasons = st.multiselect('Please tell us the reasons that caused you to be at-risk. Select all that apply.',
                    ('Poor/no attendance', 'Failed to complete/submit assignment(s)', 'Does not participate in class', 'Failed to meet minimum standards', 'Failed midterm exam(s)', 'Other'))

                    if at_risk_reasons != None:
                        st.write("It may be helpful to talk to your professor about the situation to determine what you may need to do to improve your overall grade.")
                        st.write("In addition, there are a number of resources are designed to help you make the most of your academic experience at USC.")
                        your_options = st.selectbox('Please select from the following options below.', ('', 'Kortschak Center', 'Student Health Center', 'Problem still unsolved'))

                        if your_options == 'Kortschak Center':
                            st.write('The Kortschak Center offers individual learning strategy sessions and tutoring in academic disciplines. Please visit https://kortschakcenter.usc.edu/ for more information. The Kortschak Center can be reached at 213-740-7884 or via email at kortschakcenter@usc.edu. Visit their website for virtual drop-in hours.')
                            follow_up = st.selectbox('Did that work?', ('', 'Yes', 'No'))

                            if follow_up == "Yes":
                                st.write('Problem resolved. We hope that helped. You can still take an OT class if you want.')

                            elif follow_up == "No":
                                st.write('Sorry this didn\'t help. We recommend that you take an OT class next semester.')

                            
                        elif your_options == 'Student Health Center':
                            st.write('Please visit https://studenthealth.usc.edu/ for more information about scheduling an appointment, resources, and virtual appointment options.')
                            st.write('If you want to attend group workshops or meet one-on-one, please visit MySHR at https://eshc-pncw.usc.edu/ for more information about scheduling an appointment.')
                            follow_up = st.selectbox('Did that work?', ('', 'Yes', 'No'))

                            if follow_up == "Yes":
                                st.write('Problem resolved. We hope that helped. You can still take an OT class if you want.')

                            elif follow_up == "No":
                                st.write('Sorry this didn\'t help. We recommend that you take an OT class next semester.')
                            
                        elif your_options == 'Problem still unsolved':
                            st.write("Sorry to hear that. Sometimes, things can go unexpected. We want to help you solve this issue.")

                            description = st.text_area('Were there any personal reasons that caused you to almost fail the class?')
                            st.caption('Please describe, in detail, the nature of concern; what you have witnessed; how you first learned of this concern; location; and any other pertinent information.')


                            taking_ot = st.selectbox('Have you previously taken, or are you currently taking OT 100 or OT 101?', ('', 'Yes', 'No'))

                            if taking_ot == "Yes":
                                st.write('If your issue has not been resolved in the previous steps, you should send a message to your support group with at least the following items:')
                                st.write('\"Hi, this is [enter your name here] from [OT XXX]. If you\'re reading this, I\'m going through a difficult time in at least one of my classes for [insert reasons here] and was hoping to talk to you about it. If that\'s OK with you, please feel free to contact me.\"')
                                st.write("To recap, here are the reasons you chose:", at_risk_reasons)
                                st.caption('You should have formed your support group during the 3rd week of classes.')
                                follow_up = st.selectbox('Did that work?', ('', 'Yes', 'No'))

                                if follow_up == "Yes":
                                    st.write('Problem resolved. We hope that helped. You can still take an OT class if you want.')

                                elif follow_up == "No":
                                    st.write('Sorry this didn\'t help. We recommend that you take an OT class next semester.')

                            elif taking_ot == "No":
                                st.write('We want to help you solve this issue.')
                                st.write('Based on your background, GPA, and reasons for failing, we recommend that you take an OT class next semester.')
                
                elif at_risk_status == "No":
                    first_aware = 'N/A'
                    st.write('We\'re glad that you are not failing any of your classes.')
                    description = st.text_area('Are there any personal reasons that could make you fail the class in the future?')
                    st.caption('Please describe, in detail, the nature of concern; what you have witnessed; how you first learned of this concern; location; and any other pertinent information.')

                    follow_up = 'Yes'
                
                if at_risk_status != '' and follow_up != '':
                    st.header('Next Steps')
                    next_step = st.selectbox('Please select from the following options. *', ('', 'No other options', 'Take an OT class', 'Request a leave of absence', 'Talk with a helpline volunteer', 'See other ways to support myself'))
                
                if next_step != 'No other options':
                    if next_step == 'Take an OT class':

                        importance = 'High'

                        course_info = {}

                        st.subheader('OT Courses at USC')
                        st.write('Occupational therapy (OT) teaches you how to adapt. It can help you perform any kind of task at school, work, or in your home. You\'ll learn how to use tools if you need them. You\'ll meet with professors (also known as occupational therapists) who can come up with ways to change your movements so you can get your work done, take care of yourself or your home, play sports, or stay active.')
                        st.write(about_ot())

                        # Year can be from 2007 to 2037, just like in Android. We don't want any overflowing errors.
                        year = st.number_input('Which year are you registering for?', value = 2022, min_value = 2007, max_value = 2037)

                        semester = st.selectbox('Which semester are you registering for?', ('', 'Spring', 'Fall'))
                        semester_caption = st.caption('OT classes with support groups are not available in summer terms.')


                        # PASSED
                        try:
                            st.write('These are the courses offered in ' + str(semester) + ' ' + str(int(year)) + '. Click on the headers to sort.')
                            st.write(courses(year, semester, "ot"))

                            course_table = courses(year, semester, "ot")
                            # course_offered_list=get_list_of_courses_offered(course_table)
                            course_info = course_info_dict(year, semester, "ot", course_table)

                            course_with_info = st.selectbox('Which course would you like to get info on?', course_info)
                            st.caption('Students who are at-risk are recommended to take OT 100 or OT 101. These can be taken in any order.')
                            st.caption('OT classes greater than 200 do not have support groups or connection sessions and should only be taken by students in the OT major.')

                            st.subheader('About ' + str(course_with_info))
                            st.write(course_info[course_with_info])
                        except:
                            st.write('No course information available for that term')

                        course_selection = st.selectbox('Which OT course are you planning to take?', course_info)
                        st.caption('We recommend taking one course at a time, just in case you need more help during your years at USC.')


                        
                        
                        #interests
                        list_of_interests = ['Creating personal goals', 'Building identity & self-care', 'Healthy eating routines','Sleep routines','Exercise routines','Behaviorial health', 'Coping', 'Time management & balance','Cognitive self-building', 'Connection & communication', 'Self-love', 'Other', 'None']
                        # list_of_interests = sorted(list_of_interests)
                        interests = st.multiselect('What do you hope to get out of taking OT courses?', list_of_interests, default = ['None'])
                    
                    elif next_step == 'Request a leave of absence':
                        importance = 'High'
                        st.subheader('Request a leave of absence')
                        if student_status == 'Undergraduate student':
                            st.info('To learn more on how you can file a leave of absence, visit https://loa.usc.edu/. Alternatively, you can submit a ticket and we\'ll get back to you as soon as possible.')
                        else:
                            st.warning('The online Leave of Absence submission process is available only for undergraduate students. All other students should contact their academic department to discuss the Leave of Absence process. If you still want to submit a Leave of Absense request, submit a ticket and the departments will get back to you.')
                    elif next_step == 'Talk with a helpline volunteer':
                        importance = 'Medium'
                        st.warning("Remember, this form is NOT to be used to report an emergency. Think twice before proceeding!")

                        st.subheader('National Suicide Prevention Lifeline')
                        st.write('Call a trained helper at National Suicide Prevention Lifeline at (800) 273-TALK (8255).')

                        st.subheader('National Eating Disorders Association')
                        st.write('Contact a trained helper by phone at (800) 931-2237, by email at info@myneda.org, or visit their website at https://www.nationaleatingdisorders.org/.')       

                        st.subheader('The Trevor Project (for LGBTQ youth, friends and family members)')
                        st.write('Call a trained helper at (866) 488-7386, or text Start to 678678.')
                        
                        st.subheader('National Alliance on Mental Illness')
                        st.write('Call a trained helper at (800) 950-6264, or text NAMI to 741741.')

                        st.subheader('SAMHSA Disaster Distress Helpline')
                        st.write('Call a trained helper at (800) 985-5990, text TalkWithUs to 66746, or visit their website at https://www.samhsa.gov/find-help/disaster-distress-helpline.')

                        st.subheader('Crisis Text Line')
                        st.write('Text HOME to 741741.')
                        
                        st.subheader('Veterans Crisis Line')
                        st.write('Call a trained helper at (800) 273-TALK (8255).')
                        
                        st.subheader('National Alliance for Eating Disorders')
                        st.write('Call a trained helper at (866) 662-1235, or visit their website at https://www.allianceforeatingdisorders.com/.')
                        st.info("If your issue has not been resolved, submit a ticket and we\'ll get back to you as soon as possible.")

                    elif next_step == 'See other ways to support myself':
                        importance = 'Low'

                        st.subheader('Other ways to get support')
                        st.write('These are simple steps that other people have found helpful during difficult times. They\'re small actions, but each one can help you take care of yourself.')
                        st.subheader('Slow down a crisis')
                        st.write('It can be difficult to think clearly when you\'re really upset. These steps can help you get through a crisis.')
                        st.write('* Do not make any important decisions for 24 hours.')
                        st.write('* Contact someone who can help distract you. Say \"Can you distract me for a while?\"')
                        st.write('* Breathe in for 3 seconds, then out for 5 seconds. Repeat.')
                        st.subheader('Change your surroundings')
                        st.write('It can be hard to move when you\'re feeling bad, but changing your location can help change how you\'re feeling. Try it for 10 minutes and see how you feel.')
                        st.write('* Go for a walk outside if you can.')
                        st.write('* Let in some fresh air by opening a window or door.')
                        st.write('* Try sitting in a different room, on a doorstep or even just facing a different direction.')
                        st.subheader('Take care of yourself')
                        st.write('When people are upset, they often don\'t realize what their body needs. Taking care of your physical needs tells your mind that you\'re important.')
                        st.write('* Drink a big glass of water.')
                        st.write('* Eat a nutritious snack or meal.')
                        st.write('* Do something that helps you relax, like taking a shower or getting some rest.')

                        st.info("If your issue has not been resolved, submit a ticket and we\'ll get back to you as soon as possible.")







            
            # Referral section passed successfully.
            elif user == 'Another student':
                importance = 'High'

                your_status = st.selectbox('Are you a/an...', ('', 'Student', 'Alumni', 'Faculty or staff member', 'Family member/non-USC individual'))

                your_name_input = st.text_input('What is your name?')

                your_email_input = st.text_input('What is your USC email?') #use upsert incase someone wants to use this another semester

                if your_email_input[::-1][:8] != 'ude.csu@' and your_status == 'Student':
                    st.error('Please input a valid USC email.')
                elif your_email_input[::-1][:15] != 'ude.csu.inmula@' and your_status == 'Alumni':
                    st.error('Please input a valid USC alumni email.')

                your_email = your_email_input

                usc_name_input = st.text_input('What is the name of the student you are concerned about? *')

                student_status = st.selectbox('Which type of student? *', ('', 'Undergraduate student', 'Graduate student', 'Law student', 'Alumni', 'Other'))

                usc_email_input = st.text_input('What is their USC email? *') #use upsert incase someone wants to use this another semester


                # Added support for alumni students
                if student_status != '':
                    if usc_email_input[::-1][:8] != 'ude.csu@' and student_status != 'Alumni':
                        st.error('Please input a valid USC email.')
                    elif usc_email_input[::-1][:15] != 'ude.csu.inmula@' and student_status == 'Alumni':
                        st.error('Please input a valid USC alumni email.')
                
                usc_email = usc_email_input

                #class standing
                class_standing = st.selectbox('Which semester do you believe is this student currently in? *', ('', 'Incoming Student', 
                                                                                '1st Semester', '2nd Semester', '3rd Semester',
                                                                                '4th Semester', '5th Semester', '6th Semester',
                                                                                '7th Semester', '8th Semester', 'Beyond 8th Semester', 'Graduated'))

                if (class_standing == '4th Semester' or class_standing == '5th Semester' or class_standing == '6th Semester'
                    or class_standing == '7th Semester' or class_standing == '8th Semester' or class_standing == 'Beyond 8th Semester'):
                    last_semester = st.selectbox('Do you think this semester will be the last one before he/she graduates?', ('', 'Yes', 'No', 'Not sure'))
                elif (class_standing == 'Graduated'):
                    last_semester = 'Yes'
                else:
                    last_semester = 'No'

                relationship = st.selectbox('What is your relationship to that student? *', ('', 'Classmate', 'Co-worker/Colleague', 'Family member', 'Friend', 'Roommate', 'Fraternity brother', 'Sorority sister', 'Teammate', 'Other'))
                first_aware_picker = st.date_input("When were you first aware of this concern?", min_value = datetime.date(2007, 1, 1), max_value = datetime.date(2037, 12, 31))
                first_aware = first_aware_picker.strftime('%Y/%m/%d')

                description = st.text_area('Why are you concerned about this particular student?')
                st.caption('Please describe, in detail, the nature of concern; what you have witnessed; how you first learned of this concern; location; and any other pertinent information.')

                st.write('Please contact the student via that email that you are concerned about him/her. Have them complete the form on their own so that they can fully enter the data.')
            
        if user != '':
            if user == "Skip to survey":
                data_confirm = st.checkbox('I want to skip to the survey.')
            elif user == 'Myself' and your_name_input != '' and class_standing != '' and student_status != '' and usc_email != '' and at_risk_status != '' and next_step != '':
                st.write('Are all of your inputs correct?')
                data_confirm = st.checkbox('I affirm that all my inputs are correct.')
            elif user == 'Another student' and usc_name_input != '' and usc_email != '' and class_standing != '' and relationship != '':
                st.write('Are all of your inputs correct?')
                data_confirm = st.checkbox('I affirm that all my inputs are correct.')


            if next_step != '' and data_confirm == True and user != "Skip to survey":
                data_submit = st.button("Submit")
            elif data_confirm == True and user == "Skip to survey":
                data_submit = st.button("Skip to the survey")
        
        # Initialize
        input_dict = {}
        input_dict['Name'] = {}
        input_dict['Disability'] = {}
        input_dict['Type of student'] = {}
        input_dict['Class standing'] = {}
        input_dict['Classes at risk'] = {}
        input_dict['At risk?'] = {}
        input_dict['At-risk reasons'] = {}
        input_dict['Final semester'] = {}
        input_dict['Courses taken'] = {}
        input_dict['Next step'] = {}
        input_dict['Importance'] = {}
        input_dict['OT class'] = {}
        input_dict['Interests'] = {}
        input_dict['First aware'] = {}
        input_dict['Description'] = {}
        data = {}


        if user == "Myself":
            input_dict['Name'] = your_name_input
            input_dict['USC Email'] = usc_email
            input_dict['Disability'] = disability_info
            input_dict['Type of student'] = student_status
            input_dict['Class standing'] = class_standing
            input_dict['Current GPA'] = gpa
            input_dict['At risk?'] = at_risk_status
            input_dict['Classes at risk'] = at_risk_classes
            input_dict['At-risk reasons'] = at_risk_reasons
            input_dict['Final semester'] = last_semester
            input_dict['Courses taken'] = courses_taken
            input_dict['Next step'] = next_step
            input_dict['Importance'] = importance
            input_dict['OT class'] = course_selection
            input_dict['Interests'] = interests
            input_dict['First aware'] = first_aware
            input_dict['Description'] = description

            
        
        # Referrals
        elif user == "Another student":
            input_dict['Reporter\'s name'] = your_name_input
            input_dict['Reporter type'] = your_status
            input_dict['Reporter\'s contact'] = your_email
            input_dict['Name of concerned student'] = usc_name_input
            input_dict['USC Email of concerned student'] = usc_email
            input_dict['Type of student'] = student_status
            input_dict['Class standing'] = class_standing
            input_dict['Final semester'] = last_semester
            input_dict['Relationship'] = relationship
            input_dict['First aware'] = first_aware
            input_dict['Description'] = description





        if data_submit:
            data = {}
            personal_data = {}
            if student_status == 'Alumni':
                usc_email_key = usc_email.replace('@alumni.usc.edu','')
            else:
                usc_email_key = usc_email.replace('@usc.edu','')
            
            personal_data[inquiry_number] = input_dict
            # usc_email_key=usc_email.replace('@usc.edu','')
            ##this is onl for creating the first key
            #data['USC_Students']=personal_data
            #out=json.dumps(data, indent=4)
            out = json.dumps(personal_data, indent = 4)


            # If an error occurs, return it. Do not assume that the form has been submitted without any errors.
            if user == "Myself":                        # Yourself
                response = requests.patch('https://' + str(database_name) + '-default-rtdb.firebaseio.com/students.json', out)
                if response.status_code == requests.codes.ok:
                    st.success("Your response has been successfully recorded. Please make a note of the inquiry number below for your reference.")
                    st.header("Inquiry number: " + str(int(inquiry_number)).zfill(10))
                    st.write("If you are still experiencing difficulty with your emotional or mental well-being after completing this form, you can try again or contact Counseling & Mental Health 24/7 at 213-740-9355.")
                else:
                    st.error("Something went wrong. Please try again.")

            elif user == "Another student":             # Referrals
                response = requests.patch('https://' + str(database_name) + '-default-rtdb.firebaseio.com/referrals.json', out)
                if response.status_code == requests.codes.ok:
                    st.success("Your response has been successfully recorded. Please make a note of the inquiry number below for your reference.")
                    st.header("Inquiry number: " + str(int(inquiry_number)).zfill(10))
                    st.write("If you believe this student is still experiencing difficulty with his/her emotional or mental well-being after you have them complete this form, have them contact Counseling & Mental Health 24/7 at 213-740-9355.")
                else:
                    st.error("Something went wrong. Please try again.")


            # Survey

            # if user == 'Myself' or user == 'Skip to survey':

            #     if class_standing != 'Incoming Student' and data_confirm == True:
                    
            #         if user == "Skip to survey":
            #             survey_or_not = 'Yes'
            #         else:
            #             survey_or_not = st.selectbox("Would you take a quick, anonymous survey about your well-being?", ('', 'Yes', 'No'))

            #         if survey_or_not == 'Yes':

            #             age = st.selectbox("How old are you?", ('', '18-21', '21-25', '26-30', '31-40', '41+'))
            #             gender = st.selectbox("What is your gender?", ('Male', '21-25', '26-30', '31-40', '41+'))
            #             recommend_or_not=st.selectbox("Do you recommend this course?",('Yes','No'),key=classes)
                        
            #             reviews_list.append(review)
            #             recommend_list.append(recommend_or_not)
                        
            #             review_confirm = st.selectbox('Are you sure about your reviews?', ('No', 'Yes'))
            #             if review_confirm == 'Yes':
            #                 for index in range(len(recommend_list)):
            #                     classes = survey_or_not[index]
            #                     review_json = {usc_email_key:reviews_list[index]}
            #                     out_1 = json.dumps(review_json, indent = 4)
            #                     recommend_json = {usc_email_key:recommend_list[index]}
            #                     out_2 = json.dumps(recommend_json, indent = 4)
                                
            #                     # Replace them with your Firebase URL
            #                     response = requests.patch('https://' + str(database_name) + '-default-rtdb.firebaseio.com/courses' + str(classes) + '/reviews/.json', out_1)
            #                     response = requests.patch('https://' + str(database_name) + '-default-rtdb.firebaseio.com/courses' + str(classes) + '/recommendations/.json', out_2)

if __name__ == '__main__':
    main()