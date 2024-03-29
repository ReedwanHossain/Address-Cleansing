from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


def bkoi_addess_cleaner(addr):
    input_address = re.sub(
        r'(post code|post|zip code|postal code|postcode|zipcode|postalcode|dhaka)(\s*)(-|:)*(\s*)(\d{4})(\s*)', '', addr)
    input_address = input_address.replace('#', ' ')
    input_address = input_address.replace('\\', '')
    input_address = input_address.replace(',', ' ')
    return input_address


def bkoi_address_matcher(a1, a2, inA1, inA2):
    data = []
    status = None
    data.append(a1)
    data.append(a2)
    # Vectorise the data
    vec = TfidfVectorizer()
    # `X` will now be a TF-IDF representation of the data, the first row of `X` corresponds to the first sentence in `data`
    X = vec.fit_transform(data)
    # print(X)
    # Calculate the pairwise cosine similarities (depending on the amount of data that you are going to have this could take a while)
    S = cosine_similarity(X)
    score = S[0][1]
    print(score)
    if score >= 0.97:
        status = "exact"
    elif score < 0.97 and score >= 0.75:
        status = "approximate"
    else:
        status = "not matched"

    response_obj = {
        'address 1': inA1.strip(),
        'address 2': inA2.strip(),
        'match status': status,
        'match percentage': str(int(score*100))+"%",
    }
    return response_obj
# if __name__=="__main__":
#   addr1='54, 1/a-7 new eskaton road 1/a-7'
#   addr2='54, new eskaton road apt 1/a-7 dhaka 1000'
#   addr1=bkoi_addess_cleaner(addr1)
#   addr2=bkoi_addess_cleaner(addr2)
#   print(addr1+"   "+addr2)
#   print (bkoi_address_matcher(addr1,addr2))
