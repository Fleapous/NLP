import spacy
from spacy import displacy
from spacy.matcher import Matcher
import pandas as pd
import re
from datetime import datetime
from word2number import w2n
import requests
from bs4 import BeautifulSoup

nlp_trf = spacy.load('en_core_web_trf')

week_days = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'}

months = {'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November',
          'December'}

bangladesh_divisions = pd.read_csv('bangladesh_divisions.csv', header=None)
bangladesh_divisions = bangladesh_divisions.drop(columns=[0, 2, 3])
bangladesh_divisions = bangladesh_divisions.rename(columns={1: 'division'})
bangladesh_divisions.index = range(1, len(bangladesh_divisions) + 1)

bangladesh_districts = pd.read_csv('bangladesh_districts.csv', header=None)
bangladesh_districts = bangladesh_districts.drop(columns=[0, 3, 4, 5, 6])
bangladesh_districts = bangladesh_districts.rename(columns={1: 'division_idx', 2: 'district'})
bangladesh_districts.index = range(1, len(bangladesh_districts) + 1)

bangladesh_upazilas = pd.read_csv('bangladesh_upazilas.csv', header=None)
bangladesh_upazilas = bangladesh_upazilas.drop(columns=[0, 3, 4])
bangladesh_upazilas = bangladesh_upazilas.rename(columns={1: 'district_idx', 2: 'upazila'})
bangladesh_upazilas.index = range(1, len(bangladesh_upazilas) + 1)

priority_of_places_of_accident = {
    'plane': 10,
    'airport': 10,
    'bus stand': 10,
    'crossing': 6,
    'intersection': 6,
    'bridge': 6,
    'tunnel': 6,
    'flyover': 6,
    'railroad': 4,
    'rail': 4,
    'highway': 3,
    'expressway': 3,
    'bypass': 3,
    'road': 0,
    'water': 0,
}

places_of_accident = list(priority_of_places_of_accident.keys())

vehicles_set = {
    "oil tanker",
    "road roller",
    "power tiller",
    "excavator",
    "train",
    "airplane",
    "pedestrian",
    "bus",
    "car",
    "noah",
    "human hauler",
    "trolley",
    "chander gari",
    "auto rickshaw",
    "cng",
    "easy-bike",
    "truck",
    "garbage truck",
    "trailer",
    "motorcycle",
    "microbus",
    "scooter",
    "construction vehicle",
    "bicycle",
    "ambulance",
    "pickup",
    "lorry",
    "paddy cutter vehicles",
    "bulkhead",
    "crane",
    "wrecker",
    "tractor",
    "cart",
    "leguna",
    "nosimon",
    "three-wheeler",
    "four-wheeler",
    "votvoti",
    "kariman",
    "mahindra",
    "van",
    "rickshaw",
    "autorickshaw",
    "boat",
    "trawler",
    "vessel",
    "launch",
    "tanker",
    "motorcycles",
    "motorbike"
}

accidents_matcher = Matcher(nlp_trf.vocab)
patternAccident = [{"LOWER": {"IN": places_of_accident}, }]
accidents_matcher.add("AccidentType", [patternAccident])

vehicles_list = list(vehicles_set)
vehicles_list.append('vehicle')
reason_matcher = Matcher(nlp_trf.vocab)
pattern_reason = [{"LEMMA": {"IN": vehicles_list}, }]
reason_matcher.add("ReasonType", [pattern_reason])


def parse_date(date_str):
    try:
        # Remove 'Publish-' or 'Update-' and leading/trailing spaces
        date_str = date_str.split('-', 1)[-1].strip()
        # Parse the date string into a datetime object
        date_obj = datetime.strptime(date_str, '%B %d, %Y, %I:%M %p')
        return date_obj
    except ValueError:
        return None  # Return None if the date string cannot be parsed


def scrape_news(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title
        title = soup.find('h2').text.strip()

        # Extract publication date, update date, and location
        post_meta = soup.find('ul', class_='post-meta hidden-xs')
        meta_items = post_meta.find_all('li', class_='news-section-bar')

        publish_date_str = None
        update_date_str = None
        location = None

        for item in meta_items:
            text = item.get_text(strip=True)
            if 'Publish-' in text:
                publish_date_str = text
            elif 'Update-' in text:
                update_date_str = text
            elif 'fa-map-marker' in item.find('span', class_='icon').attrs.get('class', []):
                location = text

        # Parse dates
        publish_date = parse_date(publish_date_str) if publish_date_str else None
        update_date = parse_date(update_date_str) if update_date_str else None

        # Extract article text
        article_text_divs = soup.find_all('div', class_='news-article-text-block text-patter-edit ref-link')
        html_text = ''
        raw_text = ''

        for article_text_div in article_text_divs:
            paragraphs = article_text_div.find_all('p')
            for p in paragraphs:
                # Remove <a> tags within <p> tags
                for a in p.find_all('a'):
                    a.extract()

                # Add HTML and raw text
                html_text += str(p) + '\n'
                raw_text += p.get_text(strip=True) + '\n'

        # Return the extracted data as a dictionary
        return {
            'publication_date': str(publish_date),
            'update_date': update_date,
            'meta_location': location,
            'title': title,
            'HTML_text': html_text,
            'raw_text': raw_text,
            'article_url': url
        }
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
        return None


def processArticles(articles_df, nlp_processor):
    res_df = pd.DataFrame(columns=['<url>',
                                   '<publication date metadata>',
                                   '<location metadata>',
                                   '<title>',
                                   '<raw_text>',
                                   '<number_of_accidents_occured>',
                                   '<is_the_accident_data_yearly_monthly_or_daily>',
                                   '<day_of_the_week_of_the_accident>',
                                   '<exact_location_of_accident>',
                                   '<area_of_accident>',
                                   '<division_of_accident>',
                                   '<district_of_accident>',
                                   '<subdistrict_or_upazila_of_accident>',
                                   '<is_place_of_accident_highway_or_expressway_or_water_or_others>',
                                   '<is_country_bangladesh_or_other_country>',
                                   '<is_type_of_accident_road_accident_or_train_accident_or_waterways_accident_or_plane_accident>',
                                   '<total_number_of_people_killed>',
                                   '<total_number_of_people_injured>',
                                   '<is_reason_or_cause_for_the_accident_ploughed_or_ram_or_hit_or_collision_or_breakfail_or_others>',
                                   '<primary_vehicle_involved>',
                                   '<secondary_vehicle_involved>',
                                   '<tertiary_vehicle_involved>',
                                   '<any_more_vehicles_involved>',
                                   '<available_ages_of_the_deceased>',
                                   '<accident_datetime_from_url>',
                                   ])

    # Convert the dictionary to a DataFrame with a single row if it's a dict
    if isinstance(articles_df, dict):
        articles_df = pd.DataFrame([articles_df])

    for index, article in articles_df.iterrows():
        res_df.loc[index] = processArticle(article, nlp_processor)

    return res_df


def processArticle(article, nlp_processor):
    text = article['title'] + '.\n' + article['raw_text']
    doc = nlp_processor(text)

    # <number_of_accidents_occured>
    accidents_num = determineNumOfAccidents(doc)  # returns int

    # <is_the_accident_data_yearly_monthly_or_daily>
    # <day_of_the_week_of_the_accident>
    (mode, day) = determineTime(doc)  # returns (srt, str)

    # <division_of_accident>
    # <district_of_accident>
    # <subdistrict_or_upazila_of_accident>
    (division, district, upazila) = determineRegion(doc)  # returns (str, str, str)

    # <is_place_of_accident_highway_or_expressway_or_water_or_others>
    (place, place_token) = placeOfAccident(doc)  # returns (str, spacy.token.Token)

    # <exact_location_of_accident>
    exact_loc = exactLocationOfAccident(place_token)  # returns str

    # <area_of_accident>
    area = determineLocation(doc)  # returns str

    # <total_number_of_people_killed>
    total_fatalities = extractFatalities(doc)  # returns int

    # <total_number_of_people_injured>
    total_injuries = extractInjuries(doc)  # returns int

    # <primary_vehicle_involved>
    # <secondary_vehicle_involved>
    # <tertiary_vehicle_involved>
    # <any_more_vehicles_involved>
    vehicles = findVehicles(doc)  # returns list of str (max len = 4)
    veh1, veh2, veh3, veh4 = 'NA', 'NA', 'NA', 'NA'
    if len(vehicles) >= 1:
        veh1 = vehicles[0]
    if len(vehicles) >= 2:
        veh2 = vehicles[1]
    if len(vehicles) >= 3:
        veh3 = vehicles[2]
    if len(vehicles) >= 4:
        veh4 = vehicles[3]

    # <available_ages_of_the_deceased>
    ages = findAges(doc)  # returns list of ints

    # <is_country_bangladesh_or_other_country>
    country = determineBangladeshOrOther(doc)  # returns string

    # <is_type_of_accident_road_accident_or_train_accident_or_waterways_accident_or_plane_accident>
    accident_type = determineAccidentType(doc)  # returns str

    # <accident_datetime_from_url>
    accident_time = formatAccidentTime(article['publication_date'])  # returns str

    # <is_reason_or_cause_for_the_accident_ploughed_or_ram_or_hit_or_collision_or_breakfail_or_others>
    reason = determineAccidentReason(doc)  # returns str

    return [article['article_url'],  # <url>
            article['publication_date'],  # <publication date metadata>
            article['meta_location'],  # <location metadata>
            article['title'],  # <title>
            article['raw_text'],  # <raw_text>
            str(accidents_num),  # <number_of_accidents_occured>
            mode,  # <is_the_accident_data_yearly_monthly_or_daily>
            day,  # <day_of_the_week_of_the_accident>
            exact_loc,  # <exact_location_of_accident>
            area,  # <area_of_accident>
            division,  # <division_of_accident>
            district,  # <district_of_accident>
            upazila,  # <subdistrict_or_upazila_of_accident>
            place,  # <is_place_of_accident_highway_or_expressway_or_water_or_others>
            country,  # <is_country_bangladesh_or_other_country>
            accident_type,
            # <is_type_of_accident_road_accident_or_train_accident_or_waterways_accident_or_plane_accident>
            str(total_fatalities),  # <total_number_of_people_killed>
            str(total_injuries),  # <total_number_of_people_injured>
            reason,  # <is_reason_or_cause_for_the_accident_ploughed_or_ram_or_hit_or_collision_or_breakfail_or_others>
            veh1,  # <primary_vehicle_involved>
            veh2,  # <secondary_vehicle_involved>
            veh3,  # <tertiary_vehicle_involved>
            veh4,  # <any_more_vehicles_involved>
            str(ages),  # <available_ages_of_the_deceased>
            accident_time  # <accident_datetime_from_url>
            ]


def determineTime(doc):
    mode = ''  # D / M / Y
    day = 'NA'  # day of the week
    for i in doc:
        if i.ent_type_ != 'DATE' and i.ent_type_ != 'TIME':
            continue
        if i.text in week_days:
            mode = 'D'
            day = i.text
            break
        elif i.text in months:
            mode = 'M'
        else:
            if mode != 'M':
                mode = 'Y'
    return (mode, day)


def determineRegion(doc):
    division = 'NA'
    district = 'NA'
    upazila = 'NA'
    for i in doc:
        if i.ent_type_ != 'GPE' and i.ent_type_ != 'LOC':
            continue
        if bangladesh_upazilas['upazila'].isin([i.text]).any():
            upazila = i.text
            break;
        if bangladesh_districts['district'].isin([i.text]).any():
            district = i.text
        if bangladesh_divisions['division'].isin([i.text]).any():
            division = i.text
    return disambiguateNAs(division, district, upazila)


def disambiguateNAs(division, district, upazila):
    if upazila != 'NA':
        filtered_upazilas = bangladesh_upazilas[bangladesh_upazilas['upazila'] == upazila]
        if len(filtered_upazilas) == 1:
            district_idx = filtered_upazilas['district_idx'].item()
            district = bangladesh_districts.loc[district_idx]['district']
            division_idx = bangladesh_districts.loc[district_idx]['division_idx'].item()
            division = bangladesh_divisions.loc[division_idx]['division']
    if district != 'NA':
        division_idx = bangladesh_districts[bangladesh_districts['district'] == district]['division_idx'].item()
        division = bangladesh_divisions.loc[division_idx]['division']
    return (division, district, upazila)


def verb_of_object(tok):
    verbs = []
    for i in tok.ancestors:
        if i.pos_ == "VERB":
            verbs.append(i)
    return verbs


def verb_in_sent(tok):
    verbs = []
    for i in tok.sent:
        if i.pos_ == "VERB":
            verbs.append(i)
    return verbs


def placeOfAccident(doc):
    place = 'NA'
    place_token = None
    priority = -1
    # has_
    matches = accidents_matcher(doc)
    for match_id, start, end in matches:
        tok = doc[start]
        verbs = verb_in_sent(tok)
        for verb in verbs:
            if verb.lemma_ in ["occur", "happen", "crash", "hit", "ram", "die", "lead", "kill"]:
                curr_place = tok.text.lower()
                curr_prior = priority_of_places_of_accident[curr_place]
                if curr_prior > priority:
                    priority = curr_prior
                    place_token = tok
                    place = curr_place
                elif curr_prior == priority:
                    for child in tok.children:
                        if child.ent_type_ in ["GPE", "FAC", "LOC"]:
                            priority = curr_prior
                            place_token = tok
                            place = curr_place
                            break
    return place, place_token


def exactLocationOfAccident(tok):
    ret = 'NA'
    if tok is not None:
        if re.match(r"[a-zA-Z]*obj", tok.dep_):
            sent = tok.sent
            for chunk in sent.noun_chunks:
                if chunk.root == tok:
                    ret = chunk.text
                    break
        else:
            idx = tok.i - 1
            doc = tok.doc
            l = [tok.text]
            while (doc[idx].ent_type_ in ["GPE", "FAC", "LOC"]):
                l.append(doc[idx].text)
                idx -= 1
            l.reverse()
            ret = ' '.join(l)
    return ret


def extractFatalities(doc):
    # Initialize variables to store the total number of people died and current sentence count
    total_fatalities = 0
    for sentence in doc.sents:
        # Iterate through each token in the sentence
        for token in sentence:
            # Check if the token is a verb or adjective indicating death
            if token.lemma_ in ["die", "kill", "dead", "fatality"] and token.pos_ in ["VERB"]:
                # Get the subject of the verb (typically the person or people who died)
                subject = [child for child in token.children if child.dep_ in ["nsubj", "nsubjpass", "dobj"]]
                # If a subject is found
                if subject:
                    subject_text = subject[0].text

                    # Check if the subject can be written as a number
                    try:
                        num_value = w2n.word_to_num(subject_text)
                        total_fatalities += num_value

                        return total_fatalities
                    except ValueError:
                        if any(child.dep_ == "nummod" for child in subject[0].children):
                            nummod_child = [child for child in subject[0].children if child.dep_ == "nummod"][0]
                            nummod_text = nummod_child.text
                            # Check if the nummod has a compound children
                            compound_child = [child for child in nummod_child.children if child.dep_ == "compound"]
                            if compound_child:
                                compound_text = " ".join([child.text for child in compound_child] + [nummod_text])
                                try:
                                    total_fatalities += w2n.word_to_num(compound_text)
                                    return total_fatalities
                                except ValueError:
                                    pass  # If conversion fails, continue to the next check
                            else:
                                try:
                                    total_fatalities += w2n.word_to_num(nummod_text)
                                    return total_fatalities
                                except ValueError:
                                    pass  # If conversion fails, continue to the next check
                        elif any(child.dep_ == "cc" for child in subject[0].children):
                            total_fatalities += 2

                            return total_fatalities
                        else:
                            total_fatalities += 1

                            return total_fatalities
            elif token.lemma_ in ["die", "kill", "dead", "fatality"] and token.pos_ in ["ADJ"]:
                # Check if the head token of the adjective is an auxiliary (AUX)
                if token.head.pos_ == "AUX":
                    # Get the subject of the aux
                    subject = [child for child in token.head.children if child.dep_ in ["nsubj", "nsubjpass", "dobj"]]
                    if subject:
                        # Check if the nsubj has a nummod
                        if any(child.dep_ == "nummod" for child in subject[0].children):
                            nummod_child = [child for child in subject[0].children if child.dep_ == "nummod"][0]
                            nummod_text = nummod_child.text
                            # Check if the nummod has a compound children
                            compound_child = [child for child in nummod_child.children if child.dep_ == "compound"]
                            if compound_child:
                                compound_text = " ".join([child.text for child in compound_child] + [nummod_text])
                                try:
                                    total_fatalities += w2n.word_to_num(compound_text)
                                    return total_fatalities
                                except ValueError:
                                    pass  # If conversion fails, continue to the next check
                            else:
                                try:
                                    total_fatalities += w2n.word_to_num(nummod_text)
                                    return total_fatalities
                                except ValueError:
                                    pass  # If conversion fails, continue to the next check
                        # Check if the nsubj has a cc
                        elif any(child.dep_ == "cc" for child in subject[0].children):
                            total_fatalities += 2
                            return total_fatalities
                        else:
                            total_fatalities += 1
                            return total_fatalities

    return total_fatalities


def extractInjuries(doc):
    # Initialize variables to store the total number of people injured
    total_injuries = 0

    for sentence in doc.sents:
        # Iterate through each token in the sentence
        for token in sentence:
            # Check if the token is a verb indicating injury
            if token.lemma_ in ["injure", "wound", "hurt", "sustained"] and token.pos_ == "VERB":
                # Get the subject of the verb (typically the person or people who were injured)
                subject = [child for child in token.children if child.dep_ in ["nsubj", "nsubjpass", "dobj"]]

                if subject:
                    subject_text = subject[0].text

                    # Check if the subject can be written as a number
                    try:
                        num_value = w2n.word_to_num(subject_text)
                        total_injuries += num_value
                        return total_injuries
                    except ValueError:
                        if any(child.dep_ == "nummod" for child in subject[0].children):
                            nummod_child = [child for child in subject[0].children if child.dep_ == "nummod"][0]
                            nummod_text = nummod_child.text
                            # Check if the nummod has a compound child
                            compound_child = [child for child in nummod_child.children if child.dep_ == "compound"]
                            if compound_child:
                                compound_text = " ".join([child.text for child in compound_child] + [nummod_text])
                                try:
                                    total_injuries += w2n.word_to_num(compound_text)
                                    return total_injuries
                                except ValueError:
                                    pass  # If conversion fails, continue to the next check
                            else:
                                try:
                                    total_injuries += w2n.word_to_num(nummod_text)
                                    return total_injuries
                                except ValueError:
                                    pass  # If conversion fails, continue to the next check
                        elif any(child.dep_ == "cc" for child in subject[0].children):
                            total_injuries += 2
                            return total_injuries
                        else:
                            total_injuries += 1
                            return total_injuries

            # Specific handling for adjectives related to injuries
            elif token.lemma_ in ["injure", "wound", "hurt", "sustained"] and token.pos_ == "ADJ":
                # Check if the head token of the adjective is an auxiliary (AUX)
                if token.head.pos_ == "AUX":
                    # Get the subject of the aux
                    subject = [child for child in token.head.children if child.dep_ in ["nsubj", "nsubjpass", "dobj"]]
                    if subject:
                        # Check if the nsubj has a nummod
                        if any(child.dep_ == "nummod" for child in subject[0].children):
                            nummod_child = [child for child in subject[0].children if child.dep_ == "nummod"][0]
                            nummod_text = nummod_child.text
                            # Check if the nummod has a compound child
                            compound_child = [child for child in nummod_child.children if child.dep_ == "compound"]
                            if compound_child:
                                compound_text = " ".join([child.text for child in compound_child] + [nummod_text])
                                try:
                                    total_injuries += w2n.word_to_num(compound_text)
                                    return total_injuries
                                except ValueError:
                                    pass  # If conversion fails, continue to the next check
                            else:
                                try:
                                    total_injuries += w2n.word_to_num(nummod_text)
                                    return total_injuries
                                except ValueError:
                                    pass  # If conversion fails, continue to the next check
                        # Check if the nsubj has a cc
                        elif any(child.dep_ == "cc" for child in subject[0].children):
                            total_injuries += 2
                            return total_injuries
                        else:
                            total_injuries += 1
                            return total_injuries

    return total_injuries


def findAges(doc):
    ages = []
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            last_token = ent[-1]

            # Concatenate digits from the token text until a non-digit character is encountered
            age_text = ''
            for char in last_token.text:
                if char.isdigit():
                    age_text += char
                else:
                    if age_text:
                        try:
                            age = int(age_text)
                            ages.append(age)
                            break
                        except ValueError:
                            pass
                    age_text = ''

            for child in last_token.children:
                if child.dep_ == "appos":
                    try:
                        age = int(child.text)
                        ages.append(age)
                    except ValueError:
                        pass
    return ages


def findVehicles(doc, max_depth=3):
    vehicle_list = []
    for token in doc:
        if token.is_space and len(vehicle_list) != 0:
            return vehicle_list

        if token.text.lower() in vehicles_set:
            current_token = token.head
            for _ in range(max_depth):
                if current_token.text.lower() in ["crashed", "hit", "run", "lost", "ran", "collided", "collision",
                                                  "smashed", "rolled", "crash", "crushed"]:
                    vehicle_list.append(token.text.lower())
                    if len(vehicle_list) >= 4:
                        return vehicle_list
                    break
                if current_token == current_token.head:
                    break
                current_token = current_token.head

    return vehicle_list


def determineNumOfAccidents(doc):
    accident_verbs = {"occur", "happen", "crash", "hit", "ram", "die", "lead", "kill"}

    seen_places = set()
    count = 0

    for sent in doc.sents:
        has_accident_verb = any(token.lemma_ in accident_verbs for token in sent if token.pos_ == "VERB")

        if has_accident_verb:
            sentence_places = {entity.text for entity in sent.ents if entity.label_ in {"GPE", "LOC"}}

            if sentence_places - seen_places:
                seen_places.update(sentence_places)
                count += 1

    return count


def determineLocation(doc):
    accident_verbs = {"occur", "happen", "crash", "hit", "ram", "die", "lead", "kill"}

    for sent in doc.sents:
        has_accident_verb = any(token.lemma_ in accident_verbs for token in sent if token.pos_ == "VERB")

        if has_accident_verb:
            for entity in sent.ents:
                if entity.label_ in {"GPE", "LOC"}:
                    return entity.text
    (division, district, upazila) = determineRegion(doc)
    if upazila != 'NA':
        return upazila
    if district != 'NA':
        return district
    if division != 'NA':
        return division
    return 'NA'


def determineBangladeshOrOther(doc):
    (division, district, upazila) = determineRegion(doc)
    if (division != 'NA' or district != 'NA' or upazila != 'NA'):
        return 'Bangladesh'
    return 'Other'


def determineAccidentType(doc):
    matcher = Matcher(nlp_trf.vocab)
    accident_keywords = {
        "road": ["expressway", "crossing", "bypass", "bus stand", "bus stop", "parking", "bridge", "road",
                 "intersection", "highway", "avenue", "drive", "street", "roundabout", "freeway", "motorway", "alley"],
        "train": ["train", "railway", "railroad", "rail", "locomotive", "metro", "subway", "tram", "monorail"],
        "plane": ["plane", "aircraft", "flight", "jet", "airline", "air", "airfield", "airport", "aviation", "airbus"],
        "waterways": ["boat", "ship", "vessel", "ferry", "waterway", "marine", "water", "yacht", "sailbaot",
                      "cruise ship", "submarine"],
    }

    for accident_type, keywords in accident_keywords.items():
        pattern = [{"LEMMA": {"IN": keywords}}]
        matcher.add(accident_type, [pattern])

    match_count = {key: 0 for key in accident_keywords}

    matches = matcher(doc)
    for match_id, start, end in matches:
        match_type = nlp_trf.vocab.strings[match_id]
        match_count[match_type] += 1

    determined_type = max(match_count, key=match_count.get)

    if match_count[determined_type] == 0:
        return "other"

    return determined_type


def formatAccidentTime(publication_date):
    dt = datetime.strptime(publication_date, "%Y-%m-%d %H:%M:%S")

    formatted_date = dt.strftime("%Y%m%d %H:%M")
    return formatted_date


def determineAccidentReason(doc):
    matches = reason_matcher(doc)
    verb = None
    found = False
    for match_id, start, end in matches:
        tok = doc[start]
        if re.match(r"[a-zA-Z]*subj", tok.dep_):
            for anc in tok.ancestors:
                if anc.pos_ == 'VERB':
                    verb = anc
                    found = True
                    break
        if found:
            break

    if not verb:
        return 'NA'

    prep = None
    for tok in verb.subtree:
        if tok.dep_ == 'prep' and tok.head == verb and tok.text not in {'on', 'in', 'at'}:
            prep = tok

    res = 'NA'
    if prep:
        res = verb.lemma_ + ' ' + ' '.join([tok.text for tok in prep.subtree])
    elif verb:
        res = verb.lemma_
    return res
