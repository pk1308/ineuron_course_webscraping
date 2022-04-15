

import pymongo
import sys
import time
import logging

from SRC.course_info import CourseInfo
from SRC.mongodboperation import MongoDB


logging_str = "[%(asctime)s: %(levelname)s: %(module)s: %(message)s]"
logging.basicConfig(level=logging.INFO, format=logging_str)

def Run(db_name : str , run_type : str  = "SRV" , url : str = None):
    
    logging.info(f'Running the Scrapper')
    # initialize the mongodb object
    logging.info('Initializing MongoDB')
       
    mongodb_category_collection = MongoDB(db_name =db_name,collection= 'category')
    logging.info(f'MongoDB Initialized{mongodb_category_collection}')
    
    mongodb_course_link_collection = MongoDB(db_name=db_name, collection='course_link')
    logging.info(f'MongoDB Initialized{mongodb_course_link_collection}')


    mongodb_details_collection = MongoDB(db_name=db_name,collection= 'details')

    
    
    # safely close after use of browser
    with CourseInfo() as course_info:
        logging.info('Initializing the Scrapper')
        
        course_info.goto_page()
        logging.info('Base page loaded')
        logging.info('Scrapping the categories')
        
        if run_type == 'local':
        
            Done_data_category =  mongodb_category_collection.find_many()
            Done_data_category_set = {data["category"] for data in Done_data_category }
            
            logging.info(f'Done categories extracted')
            
            courses_categories_dict = course_info.fetch_courses_links_list_with_category()
            
            logging.info(f'Courses categories list extracted')
            
            for category_name , category_links in courses_categories_dict.items():
                if category_name not in Done_data_category_set:
                    Done_data_category_set.add(category_name)
                    logging.info(f'Category {category_name} to insert in database')
                    mongodb_category_collection.insert_one({"category":category_name , "category_links":category_links})
                    logging.info(f'Category {category_name} inserted in database')
                else:
                    logging.info(f"{category_name}Category Already Exist")
                
            category_links = mongodb_category_collection.find_many()
        
        
        
            for categorical_detail in category_links:
                logging.info(f'Category course details for {categorical_detail["category"]} extracted')
                courses_links = course_info.get_courses_links_from_category_link(
                    course_link=categorical_detail['category_links'])
                logging.info(f'Courses links extracted for {categorical_detail["category"]}')
                mongodb_course_link_collection.insert_one({"category_name":categorical_detail['category'] , "course_links":courses_links})
                logging.info(f'Courses links inserted for {categorical_detail["category"]}')
        elif run_type == 'SRV':
            logging.info('Scrapping the courses links on server')
            courses_links = course_info.get_courses_links_from_category_link(
                course_link="https://courses.ineuron.ai/")
            logging.info(f'Courses links extracted')
            mongodb_course_link_collection.insert_one({"category_name":"All Courses" , "course_links":courses_links})
        elif run_type == 'SRV_ONE':
            
            if not course_info.goto_page(url):
                logging.error('page not found')
                return "page no FOUND"
            else :
                logging.info(f'Course details for {"test"} and {url} extracting all the details')
                course = course_info.get_all_info_from_page()
                logging.info(f'Course details for {"test"} and {url} extracted all the details')
                course['category'] = "test"
                course['course_link'] = url
                mongodb_details_collection.insert_one(course)
                logging.info(f"{course['course_name']} inserted in database")
                time.sleep(3)
                return course 
            
        course_link_data = mongodb_course_link_collection.find_many()
        logging.info(f'Courses links data extracted')
        Done_data_courselink =  mongodb_details_collection.find_many()
        logging.info(f'Done course links extracted')
        Done_data_courselink_set = {data['course_link'] for data in Done_data_courselink 
                                    if data['course_link'] is not None}
        Done_data_courselink =  mongodb_details_collection.find_many()
        Done_data_course_set = {data['course_name'] for data in Done_data_courselink 
                                if data['course_name'] is not None}
        logging.info(f'Done courses extracted')
        
        
        for course_link_detail in course_link_data:
            logging.info(f'Course details for {course_link_detail["category_name"]} extracting')
            
            for course_link in course_link_detail['course_links']:
                logging.info(f'checking Course details for {course_link_detail["category_name"]} and {course_link} in database')
                if course_link not in Done_data_courselink_set:
                    logging.info(f'Course details for {course_link_detail["category_name"]} and {course_link} extrating')
                    Done_data_courselink_set.add(course_link)
                    logging.info(f'checking id the course name in Course details for {course_link_detail["category_name"]} and {course_link} ')
                    
                    if not course_info.goto_page(course_link):
                        logging.error('page not found')
                        continue
                    else :
                        logging.info(f'Course details for {course_link_detail["category_name"]} and {course_link} extracting all the details')
                        course = course_info.get_all_info_from_page()
                        logging.info(f'Course details for {course_link_detail["category_name"]} and {course_link} extracted all the details')
                        logging.info(f"Checking{course['course_name']} course name already exist ????")
                        if course['course_name'] not in Done_data_course_set:
                            logging.info(f"{course['course_name']} inserting in database")                            
                            course['category'] = course_link_detail['category_name']
                            course['course_link'] = course_link
                            mongodb_details_collection.insert_one(course)
                            logging.info(f"{course['course_name']} inserted in database")
                            time.sleep(3)
                        else:
                            logging.info(f"{course['course_name']}Course Already Exist")
        
    return True
                
            

if __name__ == '__main__':
    Run(db_name='run_Scrapper' , run_type='SRV_ONE' , url='https://courses.ineuron.ai/Salesforce-Administrator')
   
