from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
from selenium import webdriver
from selenium.webdriver.common.by import By
import logging
import pymongo

logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/getDetails',methods=['POST','GET'])
@cross_origin()
def getDetails():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            yt_url="https://www.youtube.com/"+searchString+"/videos"
            driver=webdriver.Chrome()
            driver.maximize_window()
            driver.get(yt_url)
            driver.execute_script("window.scrollTo(0, 720)") 
            driver.implicitly_wait(5)

            ele=driver.find_elements("id","content")
            data = []

            for i in ele[2:7]:
                try:
                    link = i.find_elements("id","thumbnail")[0].get_attribute("href")
                except:
                    link = 'No link'
                    logging.info(link)

                try:
                    thumbnail = i.find_elements("id","thumbnail")[0].find_element(By.TAG_NAME,"img").get_attribute("src")
                except:
                    thumbnail = 'No Rating'
                    logging.info(thumbnail)

                try:
                    title = i.find_element("id","video-title-link").get_attribute("title")
                except:
                    title = 'No Title'
                    logging.info(title)

                try:
                    views = i.find_element("id","metadata").find_elements(By.TAG_NAME,"span")[1].text
                except:
                    views = 'No Data'
                    logging.info(views)

                try:
                    time = i.find_element("id","metadata").find_elements(By.TAG_NAME,"span")[2].text
                except:
                    time = 'No Data'
                    logging.info(time)

                mydict = {"Search Term": searchString, "Link": link, "Thumbnail": thumbnail, "Title": title,
                          "Views": views, "Time": time}

                data.append(mydict)

            logging.info(data)

            try:    
                client = pymongo.MongoClient("mongodb+srv://abc123:123abc@cluster0.avf5chi.mongodb.net/?retryWrites=true&w=majority")
                db = client['yt_scrap']
                col = db['yt_scrap_data']
                col.insert_many(data)
            except Exception as e:
                logging.info(e)

            return render_template('response.html', data=data[0:(len(data))])

        except Exception as e:
            logging.info(e)
            return 'Something went wrong.'

        finally:
            driver.quit()

    else:
        return render_template('index.html')

if __name__=="__main__":
    app.run()