# -*- encoding: utf8 -*-
import re
import requests
import unicodedata
from tokenizer.tokenizer import Tokenizer
from sklearn.externals import joblib
import datetime
import pandas as pd
import time
import os
import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score
from sklearn.svm import SVC
from pyvi.pyvi import ViTokenizer
from sklearn.metrics import confusion_matrix


# tokenizer = Tokenizer()
# tokenizer.run()

def load_model(model):
    print('loading model ...',model)
    if os.path.isfile(model):
        return joblib.load(model)
    else:
        return None

def list_words(mes):
    words = mes.lower().split()
    return " ".join(words)

def review_to_words(review, filename):
    words = review.lower().split()
    with open(filename, "r") as f:
        dict_data = f.read()
        array = dict_data.splitlines()
    meaningful_words = [w for w in words if not w in array]
    return " ".join(meaningful_words)

def regex_email(str):
    emails = re.findall(r'[\w\.-]+@[\w\.-]+', str)
    email = "emails"
    for x in emails:
        str = str.replace(x, email)
    return str

def regex_phone_number(str):
    reg = re.findall("\d{2,4}\D{0,3}\d{3}\D{0,3}\d{3,4}",str)
    # print a
    for x in reg:
        str = str.replace(x,"phone_number")
    return str

def regex_link(str):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str)
    for x in urls:
        str = str.replace(x,"url")
    return str


def clean_doc(question):

    question = regex_email(question)
    question = regex_phone_number(question)
    question = regex_link(question)
    # question = review_to_words(question,'dict/stop_word.txt')

    if type(question)!= unicode:
        question = unicode(question, encoding='utf-8')
    # question = accent(question)
    # question = tokenizer.predict(question)  # tu them dau . vao cuoi cau

    rm_junk_mark = re.compile(ur'[?,\.\n]')
    normalize_special_mark = re.compile(ur'(?P<special_mark>[\.,\(\)\[\]\{\};!?:“”\"\'/])')
    question = normalize_special_mark.sub(u' \g<special_mark> ', question)
    question = rm_junk_mark.sub(u'', question)
    question = re.sub(' +', ' ', question)  # remove multiple spaces in a string
    return question

def accent(req):
    data = {'data': req}
    r = requests.post('http://topica.ai:9339/accent', data=data)
    result = r.content
    try:
        result = unicode(result)
    except:
        result = unicode(result, encoding='utf-8')
    # print result
    # result = result.split(u'\n')[1]
    return result


def read_top_term(file):
    with open(file, 'r') as f:
        a = f.read()
        top_term = a.splitlines()
    return top_term


def add_term(str):
    top_term = read_top_term('top_term/word_in_1_class.txt')
    str = str.lower().split()
    words = [w for w in str]
    a = []
    for i in words:
        if i in top_term:
            for j in range(0,5):
                a.append(i)
    ques = words + a
    return " ".join(ques)

def build_data(list_ques):
    list_q = []
    for q in list_ques:
        q = add_term(q)
        list_q.append(q)
    return list_q

def load_data(filename):
    yn_label = []
    col1 = []; col2 = []; col3 = []
    with open(filename, 'r') as f:
        for line in f:
            if line !='\n':
                label_num, question = line.split("\t")
                label, number = label_num.split("||#")
                if label == '':
                    continue
                question = clean_doc(question)
                # print question
                col1.append(label)
                col2.append(number)
                col3.append(question)
                if filename == 'data/ques3.txt':
                    if label=='0' or label=='3' or label=='4' or label=='15' or label=='16' or label=='20' or label=='22' or label=='26' or label=='27' or label=='30' or label=='31':
                        for i in range(100):
                            col1.append(label)
                            col2.append(number)
                            col3.append(question)
        if filename == 'data/ques3.txt':
            with open('data/ques4.txt','r') as f3:
                for line in f3:
                    if line != '\n':
                        label_num, question = line.split("\t")
                        label, number = label_num.split("||#")
                        l1,l2 = label.split("-")
                        if l2 == '':
                            continue
                        question = clean_doc(question)
                        yn_label.append(l1)
                        col1.append(l2)
                        col2.append(number)
                        col3.append(question)

            # col4.append(q)
        # col4 = build_data(col3)
        d = {"label": col1, "question": col3}
        train = pd.DataFrame(d)
        if filename == 'data/ques3.txt':
            joblib.dump(train,'model2/train16d.pkl')
        else:
            joblib.dump(train,'model2/test16d.pkl')
    return train

def training():
    train = load_model('model2/train16d.pkl')
    if train is None:
        train = load_data('data/ques3.txt')
    print "---------------------------"
    print "Training"
    print "---------------------------"
    vectorizer = load_model('model2/vectorizer16d.pkl')
    if vectorizer is None:
       vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_df=0.7, min_df=2, max_features=1000)
    train_text = train["question"].values
    vectorizer.fit(train_text)
    X_train = vectorizer.transform(train_text)
    # X_train = X_train.toarray()
    y_train = train["label"]
    joblib.dump(vectorizer, 'model2/vectorizer16d.pkl')
    s = set(y_train)
    print s
    print len(s)
    fit1(X_train, y_train)

# def fit1(X_train,y_train):
#     uni_big = SVC(kernel='rbf', C=1000)
#     uni_big.fit(X_train, y_train)
#     joblib.dump(uni_big, 'model2/uni_big7.pkl')

def fit1(X_train,y_train):
    uni_big = SVC(kernel='rbf', C=1000, probability=True)
    uni_big.fit(X_train, y_train)
    joblib.dump(uni_big, 'model2/uni_big16d.pkl')

def test_file():
    uni_big = load_model('model2/uni_big16d.pkl')
    if uni_big is None:
        training()
    uni_big = load_model('model2/uni_big16d.pkl')
    vectorizer = load_model('model2/vectorizer16d.pkl')
    test = load_model('model2/test16d.pkl')
    if test is None:
        test = load_data('data/test2.txt')
    test_text = test["question"].values
    X_test = vectorizer.transform(test_text)
    # X_test = X_test.toarray()
    y_test = test["label"]

    y_pred = uni_big.predict(X_test)
    print " accuracy: %0.3f\n" % f1_score(y_test, y_pred, average='weighted')
    # print "confuse matrix: \n", confusion_matrix(y_test, y_pred,
    #                                              labels=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11",
    #                                                      "12", "14", "15", "16", "17", "18","20", "21","22","23","24","25","26","27","30","31"])
    print "confuse matrix: \n", confusion_matrix(y_test, y_pred,
                                                 labels=["0", "2", "3", "4","6", "8", "10",
                                                         "15", "16", "18", "20", "21", "22",
                                                         "24", "26", "27", "30", "31"])
    with open('result/fail16d.txt',"w") as f:
        list_y_test = test["label"].tolist()
        y_pred=y_pred.tolist()
        q = test["question"].tolist()
        f.write(" accuracy: %0.3f\n" % f1_score(y_test, y_pred, average='weighted'))
        for i in range(len(list_y_test)):
            if list_y_test[i] != y_pred[i]:
                f.write(y_pred[i] + "\t" + list_y_test[i] + "\t" + q[i].encode('utf-8')+"\n")


# def write_file_confuse(y_test,y_pred):

def predict_ex(mes):
    uni_big = load_model('model2/uni_big7.pkl')
    if uni_big == None:
        training()
    uni_big = load_model('model2/uni_big7.pkl')
    vectorizer = load_model('model2/vectorizer7.pkl')
    mes = unicodedata.normalize("NFC",mes.strip())
    # test_message = ViTokenizer.tokenize(mes).encode('utf8')
    # mes = mes + ''
    print type(mes)
    test_message = clean_doc(mes)
    print test_message
    # test_message = list_words(test_message)
    clean_test_reviews = []
    clean_test_reviews.append(test_message)
    d2 = {"message": clean_test_reviews}
    test2 = pd.DataFrame(d2)
    test_text2 = test2["message"].values
    test_data_features = vectorizer.transform(test_text2)
    test_data_features = test_data_features.toarray()
    # s = uni_big.predict(test_data_features)[0]
    s = uni_big.predict_proba(test_data_features)[0]
    print uni_big.classes_
    s=list(s)
    s2=[]

    for i in s:
        j = "{:.14f}".format(float(i))
        s2.append(j)
    g = sorted(zip(s2, uni_big.classes_),reverse=True)
    return str(g)
if __name__ == '__main__':
    test_file()
