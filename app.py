#/usr/bin/env python3
# 0.0.0.0:5000
from flask import Flask, render_template, request
import urllib3
import json
import hashlib
import sys
import urllib.request
import urllib.parse
# See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
# Making unverified HTTPS requests is strongly discouraged, however, if you understand the risks and wish to disable these warnings, you can use disable_warnings():
#urllib3.disable_warnings()
app = Flask(__name__)
app.config['DEBUG'] = True
http = urllib3.PoolManager()
#
#curl -X POST https://boilerpipe-api-sample.arukascloud.io/extract
# -H "Content-Type: application/json"
#  -d '{"url": "https://www.google.co.jp/"}'
def get_fulltext(target_url):
    url = "https://boilerpipe-api-sample.arukascloud.io/extract"
    data = {'url':target_url}
    encoded_data = json.dumps(data).encode('utf-8')
    try :
      r = http.request(
         'POST',
         url,
         body=encoded_data,
         headers={'Content-Type': 'application/json',
                  'Cache-Control': 'no-cache'})
      data = r.data.decode('utf-8')
      http.clear()
      return data
    except :
      print(sys.exc_info()[0])


def create_summary(target_url):
    url = "https://docker-summpy.arukascloud.io/summarize"
    headers ={
      "pragma":"no-cache",
    }

    #
    fulltext=get_fulltext(target_url)
    print("result of get_fulltext["+url+"]")
    print(fulltext)
    print(hashlib.md5(fulltext.encode('utf-8')).hexdigest())
    try :
      data = urllib.parse.urlencode({'sent_limit':3,'text':fulltext})
      data = data.encode('ascii')
      ret=""
      with urllib.request.urlopen(url, data) as f:
          ret=ret+f.read().decode('utf-8')
      print(ret)
      return json.loads(ret)
    except :
      print(sys.exc_info()[0])
      #exit()
@app.route("/summary", methods=['POST', 'GET'])
def summary():
    lines=[]
    target_url=""
    if request.method == 'POST':
        target_url=request.form['target_url']
        summarydata = create_summary(target_url)
        print(dir(summarydata))
        if 'summary' in summarydata:
            lines=summarydata['summary']
    return render_template('summary.html',lines=lines,target_url=target_url)



@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
   app.run(host='0.0.0.0')
