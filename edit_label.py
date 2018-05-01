def func1():
    with open('data/test.txt','r') as f1, open('data/test2.txt','w') as f2:
        for line in f1:
            if line != '\n':
                label_num, question = line.split("\t")
                label, number = label_num.split("||#")
                if label=='1' or label=='5' or label=='7' or label=='9' or label=='11' or label=='12' or label=='14' or label=='17' or label=='23' or label=='25':
                    label = '18'

                f2.write(label+"||#"+number+"\t"+question)


def func2():
    with open('data/ques2.txt','r') as f1, open('data/ques4.txt','w') as f2:
        for line in f1:
            if line != '\n':
                label_num, question = line.split("\t")
                label2, number = label_num.split("||#")
                l1, label = label2.split("-")

                if label=='1' or label=='5' or label=='7' or label=='9' or label=='11' or label=='12' or label=='14' or label=='17' or label=='23' or label=='25':
                    label = '18'
                f2.write(l1+"-"+label+"||#"+number+"\t"+question)

if __name__ == '__main__':
    func1()
    func2()