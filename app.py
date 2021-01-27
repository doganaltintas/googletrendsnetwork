import streamlit as st
import streamlit.components.v1 as components
from pytrends.request import TrendReq
import pandas as pd
from pyvis.network import Network
import pandas as pd

pytrends = TrendReq(hl='en-US', tz=360)


@st.cache()
def load_data(xinputList):   

    def parser(xinput):
        xtemp = xinput.split("vs")
        xtempspace = xinput.split(" ")
        if len(xtemp) == 2 and xtempspace[-1] != "vs":
            return(xinput)
        else:
            return "0"


    xresultList = []
    xinputList = xinputList.lower()
    xinputList = xinputList.replace(" ," ,",")
    xinputList = xinputList.replace(", " ,",")
    xlist = xinputList.split(",")
    for xtext in xlist:
        pytrends.build_payload([f"{xtext} vs"], cat=0, timeframe="all", geo='', gprop='')
        pytrends.interest_over_time()
        df = pytrends.related_queries()
        xresult = pd.DataFrame(df[f"{xtext} vs"]["top"])
        parser(xtext)
        try: 
            xresult["compare"] = xresult["query"].apply(parser)
            xresult = xresult[xresult["compare"] != "0"] 
            xmap = xresult["compare"].str.split("vs",expand=True)
            xmap["power"] = xresult["value"]
            xresultList.append(xmap)
        except:
            pass




    xconcat_1 = pd.concat(xresultList)
    xconcat_2 = pd.concat(xresultList)
    xconcat_1 = xconcat_1.reset_index(drop=True)
    xconcat_2 = xconcat_2.reset_index(drop=True)
    xconcat_1.columns = ["from","to","power"]
    xconcat_2.columns = ["to","from","power"]
    xconcat = pd.concat([xconcat_1,xconcat_2],axis=0) 
    xconcat["from"] = xconcat["from"].str.strip()
    xconcat["to"]= xconcat["to"].str.strip()
    xconcat = xconcat.groupby(["from","to"]).sum().reset_index(drop=False)

    got_net = Network("900px", "700px",heading='Network Map',notebook=True)

    sources = xconcat['from']
    targets = xconcat['to']
    weights = xconcat['power']

    edge_data = zip(sources, targets, weights)

    for e in edge_data:
        src = e[0]
        dst = e[1]
        w = e[2]

        got_net.add_node(src, src, title=src)
        got_net.add_node(dst, dst, title=dst)
        got_net.add_edge(src, dst, value=w)

    neighbor_map = got_net.get_adj_list()

    for node in got_net.nodes:
        node["title"] += " Neighbors:<br>" + "<br>".join(neighbor_map[node["id"]])
        node["value"] = len(neighbor_map[node["id"]])

    got_net.show("output.html")
    


st.sidebar.header("Network Analysis with Google Trends")

path1 = st.sidebar.text_input('Keywords  (please use comma for multiple keywords, e.g.: hadoop,spark,nifi)')  
if st.sidebar.button("Build Network!"):
    if len(path1) > 3:
        load_data(path1)
        HtmlFile = open("output.html", 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code, height = 1000,width=800)
    else: 
        st.sidebar.write("Error: Too short Input")

st.sidebar.markdown("Dogan Altintas")    
st.sidebar.markdown("Istanbul Technical University -  MSc Big Data and Business Analytics")
