from wsgiref import simple_server
from flask import Flask, request, render_template , jsonify
from flask import Response
import os
from flask_cors import CORS, cross_origin
import json
import time
import logging
from SRC.course_info import CourseInfo
from SRC.mongodboperation import MongoDB
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from SRC.run import Run
import fake_useragent
import threading
import json 


logging_str = "[%(asctime)s: %(levelname)s: %(module)s]: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=logging_str)

master_db = "Ineuronscrapper"


# To avoid the time out issue on heroku
class threadClass:

    def __init__(self, db_name , run_type , url = None):
        self.db_name = db_name
        self.run_type = run_type
        self.url = url
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution
    
    def run(self):
        global master_db_name
        scrapper = Run(self.db_name , self.run_type , self.url)
        logging.info("Thread run completed")
        logging.debug(scrapper)
        
        

os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')

app = Flask(__name__)

CORS(app)
@app.route("/", methods=['GET' , 'POST'])
@cross_origin()
def home():
    mongodb_master_collection = MongoDB('Ineuronscrapper','details')
    master_data_course = set() 
    master_data_response = []
    
    if request.method == 'POST':
        
        
        category = request.form['category']
        attribute = request.form['attribute']
        course = request.form['course']
        option = request.form['option']
        
        if option == "category" and category =="None" and attribute == "None" and course == "None":
            master_data = mongodb_master_collection.find_many()
            master_data_category = {i['category'] for i in master_data }
            master_data_dict = dict(zip([ 'Category-'+str(i) for i in range(len(master_data_category))],master_data_category))
                                                      
            return jsonify(master_data_dict)
       
        elif option == "allcourse" and category != None and attribute == "None" and course == "None":
            master_data_course = mongodb_master_collection.find_many({'category': category })
            master_data_course_e ={x['course_name'] for x in master_data_course}
            master_data_course_response =dict(zip([ 'Category-'+str(i) for i in range(len(master_data_course_e ))],master_data_course_e ))
            
            return jsonify(master_data_course_response)
                                          
        
        elif option == "attribute" and category == "None" and attribute != None and course != None:
            master_data_course = mongodb_master_collection.find_one({'course_name' : course})
            
            master_data_course_response ={"course_name" : course , "attribute" : master_data_course[attribute]}
                                          
            return jsonify(master_data_course_response) 
       

    else:
        master_data = mongodb_master_collection.find_many()
        master_data_category = {i['course_name'] for i in master_data }
        master_data_dict = dict(zip(["course-"+str(i) for i in range(len(master_data_category))],master_data_category))
        
        
        return jsonify( master_data_dict)
    
@app.route("/scrap", methods=['GET' , 'POST'])
@cross_origin()
def scrap():
    try:
        base_scraper = threadClass(db_name=master_db , run_type="" , url=None)
    
    except Exception as e:
        logging.error(e)
        return Response(status=500)

    return Response(status=200)


CORS(app)
@app.route("/scrapone", methods=['POST'])
@cross_origin()
def scrapone():
    url = request.form['url']
    result = threadClass(db_name=master_db , run_type="SRV_ONE" , url=url)
    time.sleep(15)
    mongodb_master_collection = MongoDB('Ineuronscrapper','details')
    result = mongodb_master_collection.find_one({'course_link': url , "category" : "test"})
    if result != None:
        result['course_features'] = " ".join((result['course_features']))
        result['what_youll_learn'] = ",".join((result['what_youll_learn']))
        result['requirements'] = ",".join((result['requirements']))
        result['course_curriculum'] = ",".join((result['course_curriculum'])).replace("\n","")
        result.pop('_id')
        
        return jsonify(result)
    else:
        return jsonify({"Scraping": "Course will be updated in 15 mins"})

port = int(os.getenv("PORT", 5000))
if __name__ == "__main__":
    host = '0.0.0.0'
    # port = 5000
    httpd = simple_server.make_server(host, port, app)
    # print("Serving on %s %d" % (host, port))
    httpd.serve_forever()