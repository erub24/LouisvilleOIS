import pandas as pd
import folium as f 
import numpy as np
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import webbrowser


#a note about bugs, the geocode is sensitive if an address has a typo or is listed
#as block rather than a specific number, it will probably return none. To fix 
#this I added loops that cleans this data, but there might be other geocoding bugs
#that appear with other datasets. If the geocoding is saying latitude can't be
#be found on a none type, check the input address format, that is likely where
#something is going wrong

#also Louisville formats its data in a way that info about multiple-officers
#involved is stakced on top of each other in rows within rows
#This means there are many empty values that don't necessarily represent an
#absence of data just the blank spaces where officer's race is listed



#loads 2020 OIS csv into dataframe
df = pd.read_csv("2020list.csv")
df2= pd.read_csv("2019list.csv")
df3=pd.read_csv("2018list.csv")
df4=pd.read_csv("2017list.csv")
df5=pd.read_csv("2016list.csv")
df6=pd.read_csv("2015list.csv")


#There was an updated version posted on 6/10, one new incident was reported -- this creates a new row in the 2020 df
df = df.append({'#' : '20‐038', 'Incident #' : '80‐20‐029348',\
                    'Date of Occurrence' : 'May', 'Unnamed: 3' : '19',\
                    'Time of Occurrence' : '140', 'Address of incident' : '6900 Bardstown Road',\
                    'Division' : "7", 'Beat' : 'Empty', 'Investigation Type' : 'OIS',\
                    'Case Status':'Open', 'NameS':'Decedric Binford', 'RaceS' : 'B', 'SexS' :'M',\
                    'AgeS' : '18','EthnicityS' :'U', 'Weapon':'Firearm', 'NameO':'Patrick Dahlgren, Trevor Troutman',\
                    'RaceO':'W, W', 'SexO':'M, M', 'AgeO': '39, 25', 'EthnicityO': 'U, U',
                    'Years of Service': '2,2', 'Lethal Y/N' :'N',\
                    'Narrative' :"While on routine patrol officers observed the suspect seated in a vehicle which was blocking the roadway. As officers approached the vehicle they could smell a strong odor of mariunana omitting from the vehicle. Subsequently an unknown amount of marijuana was observed in plain veiw inside the vehicle. The suspect complied when asked to exit the vehicle by officers. During the initial contact the suspect requested to retrieve items from within the vehicle. Upon being granted permission to dp so, the suspect retrieved a handgun from the vehicle. A breif physical altercation ensued between the suspect and Officer Dahlgren. During the altercation the suspect fired one shot strking Officer Dahlgren in the right shoulder. The suspect then fled on foot and as he did so he fired his weapon again at the officers. The officers returned fire striking the suspect. The suspect continued to flee another 100 yards before collapsing in the street where he was taken into custody. The suspect's weapon was recovered at the time he was taken into custody on scene. WVS supported by phyiscal evidence at the scene confirmed the suspect fired multiple times at the officers",\
                    'City' : 'Louisville', 'State': 'KY','Country': 'USA', 'popBox': "<p>The Officer(s) involved: Patrick Dahlgren, Trevor Troutman</p>\
                    <p>Officer(s) Years of Service: 2,2</p> <p>Race of Officer(s): White, White</p> <p>Sex of Officer(s): Male, Male</p>\
                    <p>Age of Officer(s): 39, 25</p> <p><br></p> <p>Victim/Suspect Name: Decedric Binford</p> <p>Victim/Suspect Age: 18</p>\
                    <p>Victim/Suspect Race: Black</p> <p>Victim/Suspect Sex: Male</p> <p>Armed? Firearm</p> <p>Was victim/suspect killed? No</p>\
                    <p><br></p><p>LMPD&#39;s Case File Reports the incident as follows: While on routine patrol officers observed the suspect seated in a vehicle which was blocking the roadway. As officers approached the vehicle they could smell a strong odor of mariunana omitting from the vehicle. Subsequently an unknown amount of marijuana was observed in plain veiw inside the vehicle. The suspect complied when asked to exit the vehicle by officers. During the initial contact the suspect requested to retrieve items from within the vehicle. Upon being granted permission to dp so, the suspect retrieved a handgun from the vehicle. A breif physical altercation ensued between the suspect and Officer Dahlgren. During the altercation the suspect fired one shot strking Officer Dahlgren in the right shoulder. The suspect then fled on foot and as he did so he fired his weapon again at the officers. The officers returned fire striking the suspect. The suspect continued to flee another 100 yards before collapsing in the street where he was taken into custody. The suspect&#39;s weapon was recovered at the time he was taken into custody on scene. WVS supported by phyiscal evidence at the scene confirmed the suspect fired multiple times at the officers</p>\
                    <p><br></p><p><a href='https://www.courier-journal.com/story/news/crime/2020/05/19/louisville-police-man-and-officer-shot-wounded-bardstown-road/5218860002/' rel='noopener noreferrer' target='_blank'>Body Camera Footage</a></p>"}, ignore_index=True)



#creates geocoding tool
locator = Nominatim(user_agent="mapping")


def cleanData(df):
    #fills null values with empty string, this makes it easier for me to clean these values
    df = df.fillna("Empty")
    #iterates through address series and adds city and state info into its value
    #if the value is not filled, it skips (this is because of the csv's format)
    for oldValue in df["Address of incident"]:
        if oldValue != "Empty":
            newValue = str(oldValue) + " Louisville, KY"
            df["Address of incident"].replace(to_replace = oldValue, value = newValue, inplace = True)
    #There were bugs because the last two addresses had block in their streets rather
    #than specific addresses, this removes the block from their names (eg-->
    # 200 Block E. Grey Street becomes 200 E. Grey Street)
    for oldAddress in df["Address of incident"]:
        if "Block" in oldAddress:
            newAddress = oldAddress.replace("Block",'')
            df["Address of incident"].replace(to_replace = oldAddress, value = newAddress, inplace = True)
    return df
def geocodeData(df):      
    #geocodes each address and adds it latitude to new data column, if address is empty
    #the row is kept empty
    df["Latitude"] = df["Address of incident"].apply(lambda addr: locator.geocode(addr, timeout=10000).latitude\
    if addr != "Empty" else 'Empty')
        #geocodes each address and adds it longtiude to new data column, if address is empty
        #the row is kept empty
    df["Longitude"] = df["Address of incident"].apply(lambda addr: locator.geocode(addr, timeout=10000).longitude\
    if addr != "Empty" else 'Empty')
    return df

#creates folium map in Louisville 
m = f.Map(width=800,height=600,location=[38.202503, -85.668573],  tiles='cartodbpositron')




#function to add markers to 2020 feature group and map
def marker2020 (df):
    #creats feature group AKA individual layer that users can check and uncheck to see
    fg= f.FeatureGroup("2020",overlay=True,control=True)
    #iterate through each row and add a marker
    for index, row in df.iterrows():
        if row["Latitude"] != "Empty": #skips all empty values
            f.CircleMarker(location=[row["Latitude"], row["Longitude"]],\
            popup = f.Popup(df["popBox"][index], max_width=400), tooltip = "Click for more info",\
            radius=5, fill_color="blue").add_to(fg)
    fg.add_to(m)
def marker2019 (df):
    #creats feature group AKA individual layer that users can check and uncheck to see
    fg= f.FeatureGroup("2019",overlay=True,control=True)
    #iterate through each row and add a marker
    for index, row in df.iterrows():
        if row["Latitude"] != "Empty": #skips all empty values
            f.CircleMarker(location=[row["Latitude"], row["Longitude"]],\
            popup = f.Popup(df["popBox"][index], max_width=400), tooltip = "Click for more info",\
            radius=5, fill_color="blue").add_to(fg)
    fg.add_to(m)
    
def marker2018 (df):
    #creats feature group AKA individual layer that users can check and uncheck to see
    fg= f.FeatureGroup("2018",overlay=True,control=True)
    #iterate through each row and add a marker
    for index, row in df.iterrows():
        if row["Latitude"] != "Empty": #skips all empty values
            f.CircleMarker(location=[row["Latitude"], row["Longitude"]],\
            popup = f.Popup(df["popBox"][index], max_width=400), tooltip = "Click for more info",\
            radius=5, fill_color="blue").add_to(fg)
    fg.add_to(m)
def marker2017 (df):
    #creats feature group AKA individual layer that users can check and uncheck to see
    fg= f.FeatureGroup("2017",overlay=True,control=True)
    #iterate through each row and add a marker
    for index, row in df.iterrows():
        if row["Latitude"] != "Empty": #skips all empty values
            f.CircleMarker(location=[row["Latitude"], row["Longitude"]],\
            popup = f.Popup(df["popBox"][index], max_width=400), tooltip = "Click for more info",\
            radius=5, fill_color="blue").add_to(fg)
    fg.add_to(m)
def marker2016 (df):
    #creats feature group AKA individual layer that users can check and uncheck to see
    fg= f.FeatureGroup("2016",overlay=True,control=True)
    #iterate through each row and add a marker
    for index, row in df.iterrows():
        if row["Latitude"] != "Empty": #skips all empty values
            f.CircleMarker(location=[row["Latitude"], row["Longitude"]],\
            popup = f.Popup(df["popBox"][index], max_width=400), tooltip = "Click for more info",\
            radius=5, fill_color="blue").add_to(fg)
    fg.add_to(m)
def marker2015 (df):
    #creats feature group AKA individual layer that users can check and uncheck to see
    fg= f.FeatureGroup("2015",overlay=True,control=True)
    #iterate through each row and add a marker
    for index, row in df.iterrows():
        if row["Latitude"] != "Empty": #skips all empty values
            f.CircleMarker(location=[row["Latitude"], row["Longitude"]],\
            popup = f.Popup(df["popBox"][index], max_width=400), tooltip = "Click for more info",\
            radius=5, fill_color="blue").add_to(fg)
    fg.add_to(m)
 

 
#geocode and clean datasets
df=cleanData(df)#2020
df=geocodeData(df)
df2=cleanData(df2)#2019
df2=geocodeData(df2)
df3=cleanData(df3)#2018
df3=geocodeData(df3)
df4=cleanData(df4)#2017
df4=geocodeData(df4)
df5=cleanData(df5)#2016
df5=geocodeData(df5)
df6=cleanData(df6)#2015
df6=geocodeData(df6)


marker2020(df)
marker2019(df2)
marker2018(df3)
marker2017(df4)
marker2016(df5)
marker2015(df6)
f.LayerControl().add_to(m)


title_html = "<h3 align='center' style='font-size:20px'><b>Louisville Metro Police\
    Officer Involved Shootings 2015-2020</b></h3><h2 align='center'\
    style='font-size:15px'><b>Data sourced from Louisville Metro Open Data</b></h2>\
    <h1 align='center' style='font-size:10px'><b>Please note that the description\
    of the shooting is what LMPD alleges. I am working on adding links\
    to other records of these incidents for future versions of this map</b></h3>"
m.get_root().html.add_child(f.Element(title_html))
m
