import argparse
import numpy as np
from chainer import Chain,Variable,optimizers,serializers
import chainer.links as L
import chainer.functions as F


class seq2seq(Chain):
    def __init__(
            self,
            request_vocabularies_length,
            response_vocabularies_length,
            embedding_vector_size,):

        super(seq2seq,self).__init__(
            embedx=L.EmbedID(request_vocabularies_length,embedding_vector_size),
            embedy=L.EmbedID(response_vocabularies_length,embedding_vector_size),
            H=L.LSTM(embedding_vector_size,embedding_vector_size),
            W=L.Linear(embedding_vector_size,response_vocabularies_length),
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

def main(epochs,request_file,response_file):
    request_vocabularies={}
    request_lines=open(request_file).read().split('\n')
    for i in range(len(request_lines)):
        line=request_lines[i].split()
        for word in line:
            if word not in request_vocabularies:
                request_vocabularies[word]=len(request_vocabularies)

    request_vocabularies['<eos>']=len(request_vocabularies)
    request_vocabularies_length=len(request_vocabularies)

    response_vocabularies={}
    response_lines=open(response_file).read().split('\n')

    for i in range(len(response_lines)):
        line=response_lines[i].split()

        for word in line:
            if word not in response_vocabularies:
                response_vocabularies[word]=len(response_vocabularies)

    response_vocabularies['<eos>']=len(response_vocabularies)
    response_vocabularies_length=len(response_vocabularies)

    embedding_vector_size=100

    model=seq2seq(
        request_vocabularies_length,
        response_vocabularies_length,
        embedding_vector_size,
    )
    optimizer=optimizers.Adam()
    optimizer.setup(model)

    for epoch in range(epochs):
        for i in range(len(request_lines)-1):
            request_line=request_lines[i].split()
            reverse_request_line=request_line[::-1]

            response_line=response_lines[i].split()

            model.H.reset_state()
            model.cleargrads()

            loss,acc = model(
                reverse_request_line,
                response_line,
                request_vocabularies,
                response_vocabularies
            )
            loss.backward()
            loss.unchain_backward()
            optimizer.update()
        print('epoch: {} loss: {} accuracy: {}'.format(str(epoch),loss, acc.data))
        outfile="seq2seq-"+str(epoch)+".model"
        serializers.save_npz(outfile,model)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--epochs',default=100)
    parser.add_argument('--request_file',default='request.txt')
    parser.add_argument('--response_file', default='response.txt')

    args=parser.parse_args()

    main(args.epochs,args.request_file,args.response_file)