import argparse
import sys
import re
import numpy as np
import MeCab
from chainer import Chain, Variable, serializers
import chainer.functions as F
import chainer.links as L

def extract_words(text):

    tagger=MeCab.Tagger("-Owakati")
    tagger.parse("")
    wakati=tagger.parse(text)

    words=[]
    ws=re.compile(" ")

    for word in ws.split(wakati):
        words.append(word)

    return words

class seq2seq(Chain):
    def __init__(
            self,
            request_vocabularies_lenght,
            response_vocabularies_lenght,
            embedding_vector_size,
                 ):
        super(seq2seq,self).__init__(
            embedx=L.EmbedID(request_vocabularies_lenght,embedding_vector_size),
            embedy=L.EmbedID(response_vocabularies_lenght,embedding_vector_size),
            H=L.LSTM(embedding_vector_size,embedding_vector_size),
            W=L.Linear(embedding_vector_size,response_vocabularies_lenght),
        )
    def __call__(
            self,
            reverse_request_line,
            response_line,
            request_vocabularies,
            response_vocabularies
    ):
        self.H.reset_state()

        for i in range(len(reverse_request_line)):
            word_id=request_vocabularies[reverse_request_line[i]]
            x_k=self.embedx(Variable(np.array([word_id],dtype=np.int32)))
            h=self.H(x_k)

        x_k=self.embedx(Variable(np.array([request_vocabularies['<eos>']],dtype=np.int32)))
        h=self.H(x_k)

        tx=Variable(np.array([response_vocabularies[response_line[0]]],dtype=np.int32))
        accum_loss=F.softmax_cross_entropy(self.W(h),tx)
        accum_acc=F.accuracy(self.W(h),tx)


        for i in range(len(response_line)):
            word_id=response_vocabularies[response_line[i]]
            x_k=self.embedy(Variable(np.array([word_id],dtype=np.int32)))

            if i==len(response_line)-1:
                next_word_id=response_vocabularies['<eos>']
            else:
                next_word_id=response_vocabularies[response_line[i+1]]
            tx=Variable(np.array([next_word_id],dtype=np.int32))
            h=self.H(x_k)

            loss=F.softmax_cross_entropy(self.W(h),tx)
            accum_loss+=loss
            acc=F.accuracy(self.W(h),tx)
            accum_acc+=acc

        return accum_loss,accum_acc

def mt(model,words,id2wd,request_vocabularies,response_vocabularies):
    for i in range(len(words)):
        if words[i] not in request_vocabularies:
            print("None Word!!",words[i])
            sys.exit(0)

        word_id=request_vocabularies[words[i]]
        x_k=model.embedx(Variable(np.array([word_id],dtype=np.int32)))
        h=model.H(x_k)

    x_k=model.embedx(Variable(np.array([request_vocabularies['<eos>']],dtype=np.int32)))
    h=model.H(x_k)
    word_id=np.argmax(F.softmax(model.W(h)).data[0])

    output=''

    if word_id in id2wd:
        output=output+id2wd[word_id]
    else:
        output=output+word_id
    loop=0

    while word_id != response_vocabularies['<eos>']:
        x_k=model.embedy(Variable(np.array([word_id],dtype=np.int32)))
        h=model.H(x_k)
        word_id=np.argmax(F.softmax(model.W(h)).data[0])

        if word_id in id2wd:
            output=output+id2wd[word_id]
        else:
            output=output+word_id
        loop+=1

    print(output)

def constructVocabularies(corpus,message):
    vocabularies={}
    id2wd={}

    lines = open(corpus).read().split('\n')

    for i in range(len(lines)):
        line = lines[i].split()

        for word in line:
            if word not in vocabularies:
                if message == "U":
                    vocabularies[word] = len(vocabularies)
                elif message == "R":
                    id2wd[len(vocabularies)] = word
                    vocabularies[word] = len(vocabularies)

    if message == "U":
        vocabularies['<eos>'] = len(vocabularies)
        vocabularies_length = len(vocabularies)
        return vocabularies, vocabularies_length
    elif message == "R":
        id2wd[len(vocabularies)] = '<eos>'
        vocabularies['<eos>'] = len(vocabularies)
        vocabularies_length = len(vocabularies)
        return vocabularies, vocabularies_length, id2wd

def main(request_file, response_file, model_file):
    request_vocabularies, request_length = constructVocabularies(request_file, message="U")
    response_vocabularies, response_length, id2wd=constructVocabularies(response_file, message="R")

    embedding_vector_size=100
    model = seq2seq(request_length, response_length, embedding_vector_size)
    serializers.load_npz(model_file, model)

    while True:
        utterance = input()
        if utterance == "exit":
            print("Bye!!")
            sys.exit(0)

        words = extract_words(utterance)
        words.remove('\n')

        words = words[::-1]
        mt(model, words, id2wd, request_vocabularies, response_vocabularies)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--request_file', default='request.txt')
    parser.add_argument('--response_file', default='response.txt')
    parser.add_argument('--model_file',default='seq2seq-50.model')
    args=parser.parse_args()

    main(args.request_file, args.response_file, args.model_file)
