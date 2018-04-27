with open('data/question2.txt','r') as f1, open('data/ques2.txt','w') as f2:
    for line in f1:
        if line != '\n':
            label_num, question = line.split("\t")
            label, number = label_num.split("||#")
            l1, l2 = label.split("-")
            if l2 == '19':
                l2='11'
            if l2 == '':
                continue
            f2.write(l1+"-"+l2+"||#"+number+"\t"+question)