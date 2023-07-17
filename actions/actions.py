from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pickle as pk
import os
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
import string
import datetime as dt
import wikipediaapi

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
# absolute path to this file's root directory
PARENT_DIR = os.path.join(FILE_DIR, os.pardir)
# absolute path of directory_of_interest
dir_of_interest = os.path.join(PARENT_DIR, "files")

cv_path = os.path.join(dir_of_interest,  "cv.pkl")
rg_path = os.path.join(dir_of_interest,  "rg.pkl")
vectors_path = os.path.join(dir_of_interest,  "vectors.pkl")

# loading necessary files
rg = pk.load(open(rg_path, 'rb'))


# portion for preprocess_text code
# the stop words for removing
victim = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
            'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
            'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
            'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
            'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
            'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
            'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
            'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't",
            'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn',
            "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't",
            'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't",
            'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't", "ff",
            "suffering", "I", "and"
        }


# the Preprocessing function use to preprocess the text input and the train samples
def preprocess_text(text):
    text = text.lower()

    text = text.translate(str.maketrans('', '', string.punctuation))

    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)

    tokens = [word for word in tokens if word not in victim]


    return tokens





class ActionGetDiagnosis(Action):
    def name(self) -> Text:
        return "action_get_diagnosis"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get user input from the tracker
        user_input = tracker.latest_message.get("text")

        # Preprocess user input
        preprocessed_symptoms = preprocess_text(user_input)
        preprocessed_symptoms = " ".join(preprocessed_symptoms)

        # vectorization process -- cv
        from sklearn.feature_extraction.text import CountVectorizer
        cv = CountVectorizer(max_features=5000, stop_words="english")

        # vector part -- vector
        vectors = cv.fit_transform(rg["All_Symptoms"])

        # Vectorize preprocessed symptoms
        symptom_vector = cv.transform([preprocessed_symptoms])

        # Calculate cosine similarity between vectors and symptom vector
        similar = cosine_similarity(vectors, symptom_vector)

        # to get the index of the precautions row
        index = similar.argmax()

        # Get the diagnosis from the 'rg' dataframe based on the index
        diagnosis = rg.loc[index, "diagonis"]
        disease = rg.loc[index, "Disease"]

        # Send the diagnosis as a response to the user
        dispatcher.utter_message(text=f"According to your symptoms, you may have {disease}. || \n"
                                      f"The diagnosis of {disease} is {diagnosis}. || \n Did you find this helpful?")

        return []

class ActionDiseaseInfo(Action):
    def name(self) -> Text:
        return "action_disease_info"


    # def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    #     disease = tracker.get_slot("disease")
    #     wiki_wiki = wikipediaapi.Wikipedia('en')
    #     page = wiki_wiki.page(disease)
    #     if page.exists():
    #         info = page.summary[0:1000]
    #     # info = self.get_disease_info(disease)
    #
    #         dispatcher.utter_message(response="action_disease_info", disease=disease, info=info)
    #         dispatcher.utter_message(text="did you get the info that you want")
    #
    #     else:
    #         dispatcher.utter_message("I'm sorry, I couldn't find information about that disease. Please try a different"
    #                                  "disease or use the disease with a correct spelling")
    #
    #     return []

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        disease = tracker.get_slot("disease")
        wiki_wiki = wikipediaapi.Wikipedia('en')
        page = wiki_wiki.page(disease)

        if page.exists():
            info = page.summary[0:1000]
            dispatcher.utter_message(
                text=f"Here is some information about {disease}:\n{info}"
            )
            # dispatcher.utter_message(response="utter_ask_more_info")
        else:
            # dispatcher.utter_message(response="utter_no_info")
            dispatcher.utter_message(
                text="sorry, try another disease"
            )

        return []

class ActionGettime(Action):


    def name(self) -> Text:
        return "action_give_time"

    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        # Send the diagnosis as a response to the user
        dispatcher.utter_message(text=f"The current time is - {dt.datetime.now()}")

        return []
