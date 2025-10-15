from flask import Flask,request,jsonify
import requests,re,json,logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s')

VideoSearchEngine = lambda query:{'query':query,'url':f"https://www.youtube.com/results?q={query}",'video_data':[],
    '_fetch_html':lambda self:(lambda r:r.text if r.status_code == 200 else logging.error(f"Failed:Error"))(requests.get(self['url'])),
    '_extract_video_data':lambda self,html:(lambda match:json.loads(match.group(1))['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'] if match else [])(re.search(r'ytInitialData[^{]*(.*?);\s*<\/script>',html,re.DOTALL)),'_parse_video_results':lambda self,content:[self['video_data'].append({'videoId':item['videoRenderer']['videoId'],'title':item['videoRenderer']['title']['runs'][0]['text'],'thumbnail':item['videoRenderer']['thumbnail']['thumbnails'][0]['url'],'duration':item['videoRenderer']['lengthText']['simpleText'],'viewCount':item['videoRenderer']['viewCountText']['simpleText'].replace("weergaven","").replace(".","").replace(" ",""),'uploader':{'name':item['videoRenderer']['longBylineText']['runs'][0]['text'],'url':f"https://www.youtube.com{item['videoRenderer']['longBylineText']['runs'][0]['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']}"}}) for item in content if 'videoRenderer' in item],'_search':lambda self:(lambda html:{'ok':True,'by':'@Temp_Sketch','count_results':len(self['video_data']),'results':self['video_data']} if self['_parse_video_results'](self,self['_extract_video_data'](self,html)) or self['video_data'] else {'ok':False,'by':'@Temp_Sketch','result':'Search Not ,no results found.'}) (self['_fetch_html'](self)) if self['query'] else {'ok':False,'by':'@Temp_Sketch','result':'Search failed please enter a song name.'}}
@app.route('/search',methods=['GET'])
def search():
    query = request.args.get('search')
    engine = VideoSearchEngine(query)
    result = engine['_search'](engine)
    return jsonify(result)
app.run(debug=True)
