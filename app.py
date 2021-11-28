import streamlit as st
import ktrain
import spacy
nlp = spacy.load("en_core_web_sm")
import re
from spacy import displacy
from ktrain import text
from goose3 import Goose

Goo = Goose()




import nltk
Tokenizer  = nltk.data.load('tokenizers/punkt/english.pickle')


# Configure the page
st.set_page_config(page_title="IE", page_icon="", layout="wide")

Model = ktrain.load_predictor("./model")
def UntangleTokens(TokenText, Tokens):
    Pass = True
    for Token in Tokens:
        if TokenText in " ".join(Token[0]):
            Pass = False

    return Pass
    
    
def Censor(Token, TokenText):
    #Step one
    Pass = True
    if Token[1][2:] in ["rd","str","rem"]:
        if len(TokenText.split(" ")) < 2:
            Pass = False
    if Token[1][2:] in ["pop"]:
        if len(TokenText.split(" ")) < 2:
            if TokenText.split(" ") == "patient":
                Pass = False

    if len(TokenText) == 2:
        Pass = False

    if Token[1][2:] in ["product"]:
        if TokenText[:-1] == "the":
            Pass = False

    return Pass
    
if __name__ == '__main__':

    Articles = ""

    TextBoxes, Nargin = st.columns((3.2, 1))
    with TextBoxes:
        URL = st.text_input('Enter a link', "", key=1)
        Text = st.text_input('Enter a text', "", key=2)
    
    if URL:
        Article = Goo.extract(url=URL).cleaned_text
    elif Text:
        Article = Text
    else:
        Article = """Pegcetacoplan is a PEGylated pentadecapeptide developed by Apellis Pharmaceuticals for the treatment of complement-mediated diseases. It binds to complement component 3 and its activation fragment C3b, controlling the cleavage of C3 and the generation of the downstream effectors of complement activation and thus both C3b-mediated extravascular haemolysis and terminal complement-mediated intravascular haemolysis. Pegcetacoplan is the first C3-targeted paroxysmal nocturnal haemoglobinuria therapy to be approved in the USA, where it is indicated for the treatment of adults with PNH, including those switching from C5 inhibitor therapy with eculizumab and ravulizumab. A regulatory assessment of pegcetacoplan for the treatment of PNH is currently underway in the EU and Australia. Pegcetacoplan is also being investigated as a therapeutic option in other complement-mediated diseases, including age related macular degeneration, C3 glomerulopathy and autoimmune haemolytic anaemia. The recommended dosage regimen of pegcetacoplan is 1080 mg twice weekly, administered as a subcutaneous infusion via an infusion pump with a ≥ 20 mL reservoir. This article summarizes the milestones in the development of pegcetacoplan leading to this first approval for the treatment of adults with PNH."""

    

    Left_Margin, Left_Gap, Main_Text, Right_Margin = st.columns((1, 0.4, 1.8, 1))

    st.markdown("""<head>
                    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Titillium Web">
                    <style>
                    body {font-family: "Titillium Web", sans-serif}
                    </style>
                    </head>""", unsafe_allow_html=True)



    st.sidebar.write("""<div style="font-size: 25px; font-family:Titillium Web">IE Demo</div>""",unsafe_allow_html=True)
    st.sidebar.write("""<div style="font-size: 16px; font-family:Titillium Web"><b>Insights Extractor</div>""",unsafe_allow_html=True)
    
    Tagged_Article = ""
    
    Conditions = []
    Products = []

    Article = re.sub(r'-', ' ', Article)
    Article = Article.replace("\n\n", " ")
    Article = re.sub(r'\([^)]*\)', ' ', Article)
    Article = re.sub(r';', '\. ', Article)

    Sentences = nlp(Article)


    for Sen in Tokenizer.tokenize(Article):#Sentences.sents:

        Words = Model.predict(Sen)

        New_Sen = ""

        for Word in text.textutils.tokenize(Sen):  # .text):
            New_Sen += Word + " "

        Tokens = []

        Parsed_Words = []

        for n, i in enumerate(Words):

            # This chunk is meant to process bridgable entities
            if i[1][2:] != "h" and (i, n) not in Parsed_Words and i[1][2:] not in ["product", "area", "con"]:

                Gaps_Allowed = 3

                # Start by creating the combined sentence
                Combined_Sentence = ""
                Combined_Sentence += i[0] + " "

                # Add the word with its index to a list of parsed words to prevent the word from occuring multiple times
                Parsed_Words.append((i, n))

                # Start iterating through the subsequent words
                for n1, i1 in enumerate(Words[n + 1:]):

                    # Check if the subsequent word has the same tag and is not in the parsed words
                    if i1[1][0] != "b":

                        Combined_Sentence += i1[0] + " "
                        Parsed_Words.append((i1, n + 1 + n1))

                        Gaps_Allowed = 3


                    elif i1[1][0] == "b" and i1[1][2:] == i[1][2:]:

                        Combined_Sentence += i1[0] + " "
                        Parsed_Words.append((i1, n + 1 + n1))

                        Gaps_Allowed = 3


                    else:
                        break

                print(Combined_Sentence, i[1])

                Tokens.append((Combined_Sentence, i[1][2:]))

            # This chunk is meant to process non-bridgable entities
            if (i, n) not in Parsed_Words and i[1][2:] in ["product", "area", "con"]:

                Gaps_Allowed = 3

                # Start by creating the combined sentence
                Combined_Sentence = ""
                Combined_Sentence += i[0] + " "

                # Add the word with its index to a list of parsed words to prevent the word from occuring multiple times
                Parsed_Words.append((i, n))

                # Start iterating through the subsequent words
                for n1, i1 in enumerate(Words[n + 1:]):

                    # Check if the subsequent word has the same tag and is not in the parsed words
                    if i1[1][2:] == i[1][2:] and (i1, n + 1 + n1) not in Parsed_Words and i1[1][2:] in ["product",
                                                                                                        "area",
                                                                                                        "con"] and \
                            i1[1][0] != "b":

                        Combined_Sentence += i1[0] + " "
                        Parsed_Words.append((i1, n + 1 + n1))

                    else:
                        break

                print(Combined_Sentence, i[1])

                Tokens.append((Combined_Sentence, i[1][2:]))
                # if i[1][2:].upper() not in Classes:
                #    Classes.append(i[1][2:].upper())
    
        Tags = {
    
            "rd"      : "Outcomes / R&D",
            "product" : "Medicinal Product",
            "area"    : "Medical Condition",
            "str"     : "Strategy",
            "rem"     : "Regulatory Affairs",
            "con"     : "Connectors",
            "pop"     : "Patient Population",
    
                }
                
        TagColors            =  {

                        "Outcomes / R&D"      : "#e1f2fb",
                        "Regulatory Affairs"     : "#9ba4b4",
                        "Patient Population"     : "#dcd6f7",
                        "Strategy"     : "#9ba4b4",
                        "Medicinal Product" : "#ffcb74", #ffcb74
                        "Medical Condition"    : "#f5c0c0", #f5c0c0

                        }
        
        #print(Tokens)
        
        
        Displacy = {}
        Entities = []
        
        for Token in Tokens:
            
            #Find the indices
            try:
                ent = {}
                matches = list(re.finditer(Token[0], New_Sen))
                ent["start"] = matches[0].start() 
                ent["end"]   = matches[0].end()
                ent["label"] = Tags[Token[1]]
    
                Entities.append(ent)
            except:
                pass
                
        options = {"colors": TagColors}

            
        ex = [{
            "text": New_Sen.lower(),
            "ents": Entities,
            "title": None}]
        Tagged_Sentence = displacy.render(ex, style="ent", manual=True, options=options, jupyter=False)
            
        Tagged_Sentence = Tagged_Sentence.replace("""border-radius: 0.35em;""", """border-radius: 0.0em;""")
        Tagged_Sentence = Tagged_Sentence.replace("""class="entity" style=\"""", """class="entity" style="font-size: 14px; line-height: 2.1; """)
        Tagged_Sentence = Tagged_Sentence.replace("""class="entities" style="line-height: 2.5;""", """class="entities" style="font-size: 14px; line-height: 2.1; """)
        Tagged_Sentence = Tagged_Sentence.replace("""</mark>""", """</mark><span style="font-size: 14px; line-height: 2.1">""")
        Tagged_Sentence = Tagged_Sentence.replace("""<mark""", """</span><mark""")
        Tagged_Sentence = Tagged_Sentence.replace("""style=\"""", """style="display:inline; clear:left; width:auto;""")
        Tagged_Sentence = Tagged_Sentence.replace("""\n""", """""")
        #padding: 0.45em 0.6em
        Tagged_Sentence = Tagged_Sentence.replace("""padding: 0.45em 0.6em""", """padding-bottom: 0.45em""")
        Tagged_Sentence = Tagged_Sentence.replace("""margin: 0 0.25em; """, """""")
        Tagged_Sentence = Tagged_Sentence.replace("""clear:left;""", """""")


        Go = False

        for Token in Tokens:
            if Token[1] in ["rd"]:
                Go = True 
        
        if Go:    
            Tagged_Article += Tagged_Sentence + "<br><br>"
        else:
            Tagged_Article += """<div style="font-size: 14px; font-family:Titillium Web">{}</div>""".format(Sen) + "<br>"
            
            
        for Token in Tokens:
            if Token[1].lower() in ["area"] and Token[0].lower() not in Conditions:
                Conditions.append(Token[0].lower())
            if Token[1].lower() in ["product"] and Token[0].lower() not in Products:
                Products.append(Token[0].lower())



    with Main_Text:
        st.write("""<div style="font-size: 25px; font-family:Titillium Web">Main Text</div>""",unsafe_allow_html=True)


        #st.write(
        #    """<div style="font-size: 16px; font-family:Titillium Web; background-color:#e1f2fb">{}</div>""".format(Tagged_Article),
        #    unsafe_allow_html=True)



        st.write(Tagged_Article, unsafe_allow_html=True)

    with Left_Margin:
        st.write("""<div style="font-size: 25px; font-family:Titillium Web">Text's Keywords</div>""",unsafe_allow_html=True)
        st.write("""<div style="font-size: 20px; font-family:Titillium Web">Conditions</div>""",unsafe_allow_html=True)

        colors = {"": "#17D7A0"}
        options = {"ents": {"":""}, "colors": colors}
        
        FullHtml = ""
        for Drug in Conditions:
            Entities = []
            try:
                ent = {}
                ent["start"] = 0
                ent["end"]   = len(Drug)
                ent["label"] = ""
        
                Entities.append(ent)
            except:
                pass
        
            ex = [{
                "text": Drug.capitalize(),
                "ents": Entities,
                "title": None}]
            Tagged_Sentence = displacy.render(ex, style="ent", manual=True, jupyter=False, options=options)
            
            Tagged_Sentence = displacy.render(ex, style="ent", manual=True, options=options, jupyter=False)
                
            #Tagged_Sentence = Tagged_Sentence.replace("""border-radius: 0.35em;""", """border-radius: 0.0em;""")
            Tagged_Sentence = Tagged_Sentence.replace("""class="entity" style=\"""", """class="entity" style="font-size: 14px; line-height: 2.1; """)
            Tagged_Sentence = Tagged_Sentence.replace("""class="entities" style="line-height: 2.5;""", """class="entities" style="font-size: 14px; line-height: 2.1; """)
            Tagged_Sentence = Tagged_Sentence.replace("""</mark>""", """</mark><span style="font-size: 14px; line-height: 2.1">""")
            Tagged_Sentence = Tagged_Sentence.replace("""<mark""", """</span><mark""")
            Tagged_Sentence = Tagged_Sentence.replace("""style=\"""", """style="display:inline; clear:left; width:auto;""")
            Tagged_Sentence = Tagged_Sentence.replace("""\n""", """""")
            #padding: 0.45em 0.6em
            Tagged_Sentence = Tagged_Sentence.replace("""padding: 0.45em 0.6em""", """padding-bottom: 0.45em""")
            #Tagged_Sentence = Tagged_Sentence.replace("""margin: 0 0.25em; """, """""")
            Tagged_Sentence = Tagged_Sentence.replace("""clear:left;""", """""")
            FullHtml += Tagged_Sentence + "    "
            
        st.write(FullHtml.replace("\n",""), unsafe_allow_html=True)

	    #Add a small gap between the theraoeutic areas and the produts

        st.text("")
        st.text("")


        st.write("""<div style="font-size: 20px; font-family:Titillium Web">Products</div>""",unsafe_allow_html=True)

        colors = {"": "#6166B3"}
        options = {"ents": {"":""}, "colors": colors}
        
        FullHtml = ""
        for Drug in Products:
            Entities = []
            try:
                ent = {}
                ent["start"] = 0
                ent["end"]   = len(Drug)
                ent["label"] = ""
        
                Entities.append(ent)
            except:
                pass
        
            ex = [{
                "text": Drug.capitalize(),
                "ents": Entities,
                "title": None}]
            Tagged_Sentence = displacy.render(ex, style="ent", manual=True, jupyter=False, options=options)
            
            Tagged_Sentence = displacy.render(ex, style="ent", manual=True, options=options, jupyter=False)
                
            #Tagged_Sentence = Tagged_Sentence.replace("""border-radius: 0.35em;""", """border-radius: 0.0em;""")
            Tagged_Sentence = Tagged_Sentence.replace("""class="entity" style=\"""", """class="entity" style="font-size: 14px; line-height: 2.1; """)
            Tagged_Sentence = Tagged_Sentence.replace("""class="entities" style="line-height: 2.5;""", """class="entities" style="font-size: 14px; line-height: 2.1; """)
            Tagged_Sentence = Tagged_Sentence.replace("""</mark>""", """</mark><span style="font-size: 14px; line-height: 2.1">""")
            Tagged_Sentence = Tagged_Sentence.replace("""<mark""", """</span><mark""")
            Tagged_Sentence = Tagged_Sentence.replace("""style=\"""", """style="display:inline; clear:left; width:auto;""")
            Tagged_Sentence = Tagged_Sentence.replace("""\n""", """""")
            #padding: 0.45em 0.6em
            Tagged_Sentence = Tagged_Sentence.replace("""padding: 0.45em 0.6em""", """padding-bottom: 0.45em""")
            #Tagged_Sentence = Tagged_Sentence.replace("""margin: 0 0.25em; """, """""")
            Tagged_Sentence = Tagged_Sentence.replace("""clear:left;""", """""")
            FullHtml += Tagged_Sentence + "    "
            
        st.write(FullHtml.replace("\n",""), unsafe_allow_html=True)