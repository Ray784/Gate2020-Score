from flask import Flask, request
import requests, urllib.request, io
from bs4 import BeautifulSoup

app = Flask(__name__)


start_temp = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no"><link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous"><link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"><title>Gate Score Calculator</title><style>body{margin: 5px;overflow-x: hidden;overflow-y: scroll;padding-left: 30px;font-family: poppins;cursor: context-menu;}html {scroll-behavior: smooth;}.center{display: block;margin: auto;}.card{padding: 20px;margin: 10px;border-radius: 2px;background-color: white;box-shadow: 0 10px 16px 0 rgba(0,0,0,0.2);transition: 0.3s;}.card-title{text-decoration: underline;}.display{height: 300px;}</style></head><body><br><br><div class="container"><div class="row"><div class="card col-md">'
end_temp = '</div></div></div><script src="https://cdn.jsdelivr.net/gh/google/code-prettify@master/loader/run_prettify.js"></script><script src="https://code.jquery.com/jquery-3.4.1.slim.min.js" integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n" crossorigin="anonymous"></script><script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script><script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script></body></html>'
form = '<form action="/score" method = "POST"><div class="form-group"><label for="input2">Name</label><input type="text" class="form-control" id="input2" name="user-name" required></div><div class="form-group"><label for="input1">Gate Responses url</label><input type="text" class="form-control" id="input1" name="response-url" required><small id="response-help" class="form-text text-muted">We will not share your response url.</small></div><button type="submit" class="btn btn-primary">Submit</button></form>'

@app.route('/')
def index():
    return start_temp + form + end_temp;

@app.route('/usrdata')
def getData():
	with open("data.txt","a") as file:
		return Response(file.read(), mimetype='text/plain')

@app.route('/score', methods = ['POST'])
def getScore():
    score_tag = ''
    url = request.form['response-url'];
    name = request.form['user-name'];
    if(url == ''):
        return start_temp + form + '<br></div><div class="card col-md-12">' + 'Invalid' + end_temp;
    res = urllib.request.urlopen(url).getcode()
    if(res == 200):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        ga_1m = [4, 1, 1, 4, 2]
        ga_2m = [4, 3, 1, 2, 3]
        cs_1m = [1, 1, 3, 3, 2, 3, 4, 4, 4, 3, 3, 3, 1, 1, 4, 3]
        cs_1m_nat = [[0.125, 0.125], [7, 7], [5, 5], [1034, 1034], [13.5, 13.5], [19, 19], [13, 13], [7, 7], [6, 6]]
        cs_2m = [1, 3, 2, 2, 2, 4, 1, 2, 1, 2, 1, 1, 2, 3, 1, 2]
        cs_2m_nat = [[12, 12], [2.15, 2.18], [14, 14], [0.5, 0.5], [55, 55], [511, 511], [81, 81], [99, 99], [5.25, 5.25], [6, 6], [7, 7], [154.5, 155.5], [4, 4], [44, 44]]

        questions_table = soup.findAll("table", {"class": "questionRowTbl"})
        answers_table = soup.findAll("table", {"class": "menu-tbl"});

        answer = ['' for i in range(65)]

        for i in range(len(questions_table)):
            answer_td = []
            question = []
            for question_img in questions_table[i].findChildren("img"):
                question.append(question_img['name'])

            qnum = int(question[0].split('.')[0].split('_')[6]) - 1
            if(question[0].split('.')[0].split('_')[4] == 'cs'):
                qnum += 10

            if(len(question) == 5):
                answer_td = answers_table[i].findChildren("td", {"class": "bold"})
                ans = (answer_td[len(answer_td)-1].text).strip()
                if(ans != '--'):
                    answer[qnum] = question[int(ans)].split('.')[0].split('_')[7]
                else:
                    answer[qnum] = ans

            elif(len(question) == 1):
                answer_td = questions_table[i].findChildren("td", {"class": "bold"})
                answer[qnum] = (answer_td[len(answer_td)-1].text).strip()

        i = 0
        pos_score_1m = 0
        pos_score_2m = 0
        unanswered_1m = 0
        unanswered_2m = 0
        neg_score_1m = 0
        neg_score_2m = 0
        for val in ga_1m:
            if(answer[i] == '--'):
                unanswered_1m += 1
            elif(int(answer[i]) == val):
                pos_score_1m += 1
            else:
                neg_score_1m += 1
            i+=1

        for val in ga_2m:
            if(answer[i] == '--'):
                unanswered_2m += 1
            elif(int(answer[i]) == val):
                pos_score_2m += 1
            else:
                neg_score_2m += 1
            i+=1

        for val in cs_1m:
            if(answer[i] == '--'):
                unanswered_1m += 1
            elif(int(answer[i]) == val):
                pos_score_1m += 1
            else:
                neg_score_1m += 1
            i+=1

        for val in cs_1m_nat:
            if(answer[i] == '--'):
                unanswered_1m += 1
            elif(((val[0] <= float(answer[i])) and (float(answer[i]) <= val[1]))):
                pos_score_1m += 1
            i+=1

        for val in cs_2m:
            if(answer[i] == '--'):
                unanswered_2m += 1
            elif(int(answer[i]) == val):
                pos_score_2m += 1
            else:
                neg_score_2m += 1
            i+=1

        for val in cs_2m_nat:
            if(answer[i] == '--'):
                unanswered_2m += 1
            elif(((val[0] <= float(answer[i])) and (float(answer[i]) <= val[1]))):
                pos_score_2m += 1
            i+=1


        pos = pos_score_1m + (2*pos_score_2m)
        neg = (neg_score_1m/3) + (2*neg_score_2m/3)

        score_tag = "Analysis: <br>"+"Number of 1 mark questions correctly answered: "+str(pos_score_1m)+"<br>Number of 1 mark questions wrongly answered and marks deducted: "+str(neg_score_1m)+"<br>Number of 1 mark questions unanswered: "+str(unanswered_1m)+"<br><br>"+"Number of 2 mark questions correctly answered: "+str(pos_score_2m)+"<br>Number of 2 mark questions wrongly answered and marks deducted: "+str(neg_score_2m)+"<br>Number of 2 mark questions unanswered: "+str(unanswered_2m)+"<br><br>"+"positive score: "+str(pos)+"<br>negative score: "+str(neg)+"<br><br>"+"final score: "+str(pos - neg)+"<br>"
        with open("data.txt","a") as file:
        	file.write('name: '+name+"\nurl: "+url+"\nscore: "+str(pos-neg));
        return start_temp+form+ '<br></div><div class="card col-md-12">'+score_tag+end_temp
    else:
        return start_temp+form + '<br></div><div class="card col-md-12">' +("Error: "+str(res)+"Url down try again later")+end_temp