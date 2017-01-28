#!/bin/python
# -*- coding: utf-8 -*-
import ner
class Stanford():
    """
    Clase que se conecta al servidor NER Stanford y devuelve el texto anotado.
    """

    def __init__(self, ner_host='localhost', ner_port=9191, ner_output_format='inlineXML',pos_port=9190):
        if ner_output_format not in ('slashTags', 'xml', 'inlineXML'):
            raise ValueError('Formato de salida %s invalido.' % ner_output_format)
        self.ner_tagger = ner.SocketNER(host=ner_host,port=ner_port)
        self.pos_tagger = ner.SocketNER(host=ner_host,port=pos_port)
        
    def tag(self,text):
        """
        Retorna texto anotado
        """
        return self.ner_tagger.tag_text(text)
    
    def pos(self,text):
        """
        Retorna texto anotado
        """
        return self.pos_tagger.tag_text(text)
    
    def nouns(self,text):
        """
        Retorna proper nouns
        """
        nouns = []
        text = self.pos_tagger.tag_text(text)
        for par in text.split(' '):
            if len(par.split('_')) > 1:
                word = par.split('_')[0]
                tag = par.split('_')[1]
                if word and tag and tag[0] == 'n' and tag[1] == 'p':
                    nouns.append(word.upper())
        return nouns
    
    def entities(self,text):
        """
        Retorna entidades
        """
        entidades = []
        text = self.simplifyText(text)
        text = self.removeURL(text)
        text = self.tag(text)
        text = self.removeNothingSymbol(text)
        text = self.pos(text)
        actual_class = None
        for par in text.split(' '):
            if len(par.split('_')) > 1:
                word = par.split('_')[0]
                tag = par.split('_')[1]
                if '<PERS' in word:
                    actual_class = 'PERS'
                    continue
                elif '<LUG' in word:
                    actual_class = 'LUG'
                    continue
                elif '<ORG' in word:
                    actual_class = 'ORG'
                    continue
                elif '<OTROS' in word:
                    actual_class = 'LABEL'
                    continue
                elif '</' in word or '<0>' in word or '</0>' in word:
                    actual_class = None
                    continue

                if actual_class is None:
                    #if '@' in word:
                     #   actual_class = 'PERS'
                    if 'np' in tag or '#' in word:
                        actual_class = 'LABEL'
                    else:
                        actual_class = '0'

                entidades.append((word,actual_class))
                #print word,tag,actual_class

                if actual_class == '0' or actual_class == 'LABEL':
                    actual_class = None
        
        return entidades
    
    def simplifyText(self,text):
        """
        Saca tildes, Saca espacios extras
        """
        from unidecode import unidecode
        import re
        text = re.sub(' +',' ',text)
        return unidecode(text)
    
    def removeURL(self,text):
        import re
        return re.sub(r'https?:\/\/.*[\r\n]*', '', text)
    
    def removeNothingSymbol(self,text):
        import re
        text = re.sub('<0>', '', text)
        return re.sub('</0>', '', text)
    
    def loadStreetNames(self,filename,dicc_loc={}):
        import re
        from io import open
        with open(filename, encoding="utf-8") as locations_file:
            for line in locations_file:
                for exp in line.split('\t'):
                    exp = self.simplifyText(exp)
                    exp = re.sub(r'[^\w]', ' ', exp)
                    for word in exp.split(' '):
                        dicc_loc[word.strip().upper()] = exp
        return dicc_loc
    
    def loadGeoPlaces(self,filename,dicc_loc={}):
        from io import open
        with open('UY.txt', encoding="utf-8") as locations_file:
            for line in locations_file:
                tabs = line.split('\t')
                for word in tabs[1].split(' '):
                    word = self.simplifyText(word)
                    dicc_loc[word.strip().upper()] = tabs[2]
        return dicc_loc
    
    def replaceLabelsUsingLists(self,pairs,dicc_loc = {},dicc_per = {},dicc_org = {}):
        result = []
        count_loc = 0
        count_pers = 0
        dicc_clases = {}
        for (word,tag,id_tweet) in pairs:
            if tag == 'LABEL':
                if dicc_loc.get(word.strip().upper()):
                    tag = 'LUG'
                    count_loc +=1
                else:
                    tag = 'OTROS'
            if '@' in word:
                tag = 'PERS'
                count_pers +=1
            elif '#' in word:
                tag = 'OTROS'
            dicc_clases[tag] = dicc_clases.get(tag,0)+1
            result.append((word,tag,id_tweet))
        print 'Se sustituyeron',count_loc, ' lugares y ',count_pers, ' personas.'
        for key in dicc_clases.keys():
            print key,dicc_clases[key]
        return result
    
    def generateTrainAndTestFile(self,pairs,train_filename,test_filename,size = 0.7):
        train_file_content = ''
        test_file_content = ''
        limit = len(pairs)*size
        count = 0
        for (word,label,id_tweet) in pairs:
            count+=1
            try:
                if word != ' ' and word != '' and word != '\n' and label != ' ' and label != '' and label != '\n':
                    if count < limit:
                        train_file_content += word + '\t' + label + '\n'
                    else: 
                        test_file_content += word + '\t' + label + '\n'
            except:
                print word ,'\t' , label , '\n',type(word),type(label)
        try:
            with open(train_filename, "w") as text_file:
                text_file.write(train_file_content)
            with open(test_filename, "w") as text_file:
                text_file.write(test_file_content)
        except:
            raise
