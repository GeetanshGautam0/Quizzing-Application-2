# Standard for question IO
# For QAS v2.00.00 >> v2.99.99

import qa_appinfo as QAInfo

def convRawToDict(__raw: str) -> dict: # Functional function [Unoptimized]  
    out: dict = {}
    
    seps = QAInfo.QuestionSeperators
    newlineSep = seps.get('N')
    spaceSep = seps.get('S')
    QASep = seps.get('QA')
    
    for i in __raw.split('\n'):
        i = i.strip()
        if len(i) > 0:
            
            if QASep in i:
                k = i.split(QASep)[0].strip()
                v = i.replace(k, '', 1).strip(); v = v.replace(QASep, '')

                if len(k) > 0 and len(v) > 0:
                    k = k.replace(spaceSep, ' '); v = v.replace(spaceSep, ' ')
                    k = k.replace(newlineSep, '\n'); v = v.replace(newlineSep, '\n')
                    
                    out[k] = v

    return out

def convertToQuestionStr(question: str, answer: str) -> str: # Convinience function
    question = question.strip(); answer = answer.strip()
    
    if not len(question) > 0 or not len(answer) > 0: return
    
    # Declerations
    out = ""
    
    seps = QAInfo.QuestionSeperators
    newlineSep = seps.get('N')
    spaceSep = seps.get('S')
    QASep = seps.get('QA')
    
    question = question.replace(newlineSep, '').replace(spaceSep, '').strip()
    answer= answer.replace(newlineSep, '').replace(spaceSep, '').strip()
    
    if not len(question) > 0 or not len(answer) > 0: return
    
    # Replace
    question=question.replace('\n', newlineSep); question=question.replace(' ', spaceSep)
    answer=answer.replace('\n',newlineSep); answer=answer.replace(' ', spaceSep)
        
    question = question.strip(); answer = answer.strip()
    
    # Concat
    out = f"{question}{QASep}{answer}"
    
    return out

def dictToSaveStr(data: dict) -> str:
    out = ""
    
    print(data)
    
    for i in data:
        qa = convertToQuestionStr(i, data.get(i))
        out += f"{qa}\n"
    
    return out