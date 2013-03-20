# detectLSI.py uses the LSI method from the gensim package to implement
# "bag of words" detection. This is an alternative to the "strings" detector.
# It is a python module and is imported and used by the runBow paver task
# defined in pavement.py.

import logging

import json

from gensim import corpora, models, similarities

#logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class LsiDetector:
  def __init__(self):
    f=open('detectors/bow/tags.json', 'r')
    s=f.read()
    f.close()

    self.tags=json.loads(s)
    self.dict=corpora.dictionary.Dictionary('detectors/bow/words.dict')
    self.corpus=corpora.MmCorpus('detectors/bow/corpus.mm')
    self.index=similarities.MatrixSimilarity.load('detectors/bow/similarity.index')
    self.lsi=models.LsiModel(self.corpus, num_topics=2)

  def classify(self, doc):
    bow=self.dict.doc2bow(doc)
    vec=self.lsi[bow]
    sims=self.index[vec]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    top=sims[0]
    print(top)
    docid=top[0]
    tag=self.tags[docid]
    return tag
