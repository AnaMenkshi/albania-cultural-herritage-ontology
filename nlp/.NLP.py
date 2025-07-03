import spacy
from collections import defaultdict
from dateutil.parser import parse as date_parse
from dateutil.parser import ParserError

# Load SpaCy English model
nlp = spacy.load("en_core_web_sm")

# Ontology schema
ontology_schema = {
    "OrthodoxChurch": {
        "data_properties": ["hasName", "hasReligion", "hasCulturalContext", "hasCulturalSignificance",
                            "hasCulturalHeritageStatus", "hasCreator", "hasArchitecturalStyle"],
        "object_properties": ["locatedIn", "associatedWithEvent"]
    },
    "CatholicChurch": {
        "data_properties": ["hasName", "hasReligion", "hasCulturalContext", "hasCulturalSignificance",
                            "hasCulturalHeritageStatus", "hasCreator", "hasArchitecturalStyle"],
        "object_properties": ["locatedIn", "associatedWithEvent"]
    },
    "Mosque": {
        "data_properties": ["hasName", "hasReligion", "hasCulturalContext", "hasCulturalSignificance",
                            "hasCulturalHeritageStatus", "hasCreator", "hasArchitecturalStyle"],
        "object_properties": ["locatedIn", "associatedWithEvent"]
    },
    "Monastery": {
        "data_properties": ["hasName", "hasReligion", "hasCulturalContext", "hasCulturalSignificance",
                            "hasCulturalHeritageStatus", "hasCreator", "hasArchitecturalStyle"],
        "object_properties": ["locatedIn", "associatedWithEvent"]
    },
    "PilgrimageSite": {
        "data_properties": ["hasName", "hasReligion", "hasCulturalContext", "hasCulturalSignificance",
                            "hasCulturalHeritageStatus", "hasCreator", "hasArchitecturalStyle"],
        "object_properties": ["locatedIn", "associatedWithEvent"]
    },
    "AncientCity": {
        "data_properties": ["hasName", "hasCreator", "hasCulturalContext", "hasCulturalSignificance",
                            "hasCulturalHeritageStatus", "hasDateOfDiscovery"],
        "object_properties": ["isPartOf", "locatedIn", "datedFrom", "originatedFrom", "associatedWithEvent"]
    },
    "CastleOrFortress": {
        "data_properties": ["hasName", "hasCreator", "hasCulturalContext", "hasCulturalSignificance",
                            "hasCulturalHeritageStatus", "hasDateOfDiscovery"],
        "object_properties": ["isPartOf", "locatedIn", "datedFrom", "originatedFrom", "associatedWithEvent"]
    },
    "TombOrBurialMound": {
        "data_properties": ["hasName", "hasCreator", "hasCulturalContext", "hasCulturalSignificance",
                            "hasCulturalHeritageStatus", "hasDateOfDiscovery"],
        "object_properties": ["isPartOf", "locatedIn", "originatedFrom", "datedFrom", "associatedWithEvent"]
    },
    "RockArtOrInscription": {
        "data_properties": ["hasName", "hasCreator", "hasCulturalContext", "hasCulturalSignificance",
                            "hasCulturalHeritageStatus", "hasDateOfDiscovery"],
        "object_properties": ["isPartOf", "locatedIn", "originatedFrom", "datedFrom", "associatedWithEvent"]
    },
    "Region": {
        "data_properties": ["hasName", "hasType", "hasLocationType"],
        "object_properties": ["hasHistoricalPeriod"]
    },
    "City": {
        "data_properties": ["hasName", "hasType", "hasLocationType"],
        "object_properties": ["hasHistoricalPeriod"]
    },
    "Date": {
        "data_properties": ["hasExactDate", "hasLabelDate"]
    },
    "HistoricEvent": {
        "data_properties": ["hasName", "hasStartDate", "hasEventDuration"],
        "object_properties": ["OccurredIn", "OccurredOn"]
    }
}

created_individuals = {}

def create_individual(name, ont_class):
    indiv_name = name.replace(" ", "").replace("_", "").replace(",", "").replace(".", "")
    created_individuals[indiv_name] = ont_class
    return indiv_name


def enrich_data_with_keywords(context_text, class_type):
    data = {}
    text = context_text.lower()

    # Religion
    if class_type in ["OrthodoxChurch", "CatholicChurch", "Mosque", "Monastery", "PilgrimageSite"]:
        if "orthodox" in text:
            data["hasReligion"] = "Orthodox Christianity"
        elif "catholic" in text:
            data["hasReligion"] = "Catholicism"
        elif "islamic" in text or "muslim" in text:
            data["hasReligion"] = "Islam"

    # Architectural style
    if "byzantine" in text:
        data["hasArchitecturalStyle"] = "Byzantine"
    elif "islamic architecture" in text or "ottoman" in text:
        data["hasArchitecturalStyle"] = "Islamic"
    elif "roman" in text:
        data["hasArchitecturalStyle"] = "Roman"

    # Creator
    if "commissioned by" in text:
        try:
            after = text.split("commissioned by", 1)[1]
            creator = after.split(".")[0].strip()
            data["hasCreator"] = creator.title()
        except:
            pass
    elif "built by" in text:
        try:
            after = text.split("built by", 1)[1]
            creator = after.split(".")[0].strip()
            data["hasCreator"] = creator.title()
        except:
            pass

    # Cultural context
    if "medieval" in text:
        data["hasCulturalContext"] = "Medieval Period"
    elif "byzantine era" in text or "byzantine rule" in text:
        data["hasCulturalContext"] = "Byzantine Period"
    elif "roman" in text:
        data["hasCulturalContext"] = "Roman Period"
    elif "ottoman" in text:
        data["hasCulturalContext"] = "Ottoman Period"

    # Cultural significance
    if "symbol" in text or "represents" in text or "important" in text:
        data["hasCulturalSignificance"] = "Important cultural monument"

    # Heritage status
    if "unesco" in text:
        data["hasCulturalHeritageStatus"] = "UNESCO World Heritage Site"
    elif "national heritage" in text:
        data["hasCulturalHeritageStatus"] = "National Heritage"

    # Date of discovery
    if "rediscovered" in text:
        try:
            parts = text.split("rediscovered")[1]
            if "in" in parts:
                year = parts.split("in")[1].split()[0]
                if year.isdigit():
                    data["hasDateOfDiscovery"] = year
        except:
            pass

    return data

def classify_entity_by_keywords(ent_text, ent_label=None):
    text = ent_text.lower()
    if "orthodox" in text and "church" in text:
        return "OrthodoxChurch"
    elif "catholic" in text and "church" in text:
        return "CatholicChurch"
    elif "mosque" in text:
        return "Mosque"
    elif "monastery" in text:
        return "Monastery"
    elif "pilgrimage" in text or "shrine" in text:
        return "PilgrimageSite"
    elif "castle" in text or "fortress" in text:
        return "CastleOrFortress"
    elif "tomb" in text or "burial" in text:
        return "TombOrBurialMound"
    elif "rock art" in text or "inscription" in text:
        return "RockArtOrInscription"
    elif "ancient city" in text or "ruins" in text or "city" in text:
        return "AncientCity"
    elif ent_label == "GPE":
        return "Region" if "region" in text else "City"
    elif "war" in text or "battle" in text or "uprising" in text or "awakening" in text:
        return "HistoricEvent"
    return None

def format_turtle_block(subject, class_type, data, obj_data):
    lines = [f":{subject} rdf:type :{class_type} ;"]
    props = []

    for prop in ontology_schema.get(class_type, {}).get("data_properties", []):
        val = data.get(prop)
        if val:
            props.append(f'    :{prop} "{val}"')

    for prop in ontology_schema.get(class_type, {}).get("object_properties", []):
        val = obj_data.get(prop)
        if val:
            obj_indiv = val.replace(" ", "").replace("_", "").replace(",", "").replace(".", "")
            props.append(f'    :{prop} :{obj_indiv}')

    return f"{lines[0]}\n" + " ;\n".join(props) + " ."

def process_text(text):
    doc = nlp(text)
    triples = []
    seen = set()
    obj_links = defaultdict(dict)

    for sent in doc.sents:
        sent_text = sent.text.strip()
        for chunk in sent.noun_chunks:
            ent_text = chunk.text.strip()
            class_type = classify_entity_by_keywords(ent_text)
            if class_type:
                indiv = create_individual(ent_text, class_type)
                data = {"hasName": ent_text}
                enriched = enrich_data_with_keywords(sent_text, class_type)
                data.update(enriched)
                for ent in sent.ents:
                    if ent.label_ == "GPE":
                        obj_links[indiv]["locatedIn"] = ent.text
                    elif ent.label_ == "EVENT":
                        obj_links[indiv]["associatedWithEvent"] = ent.text
                triples.append((indiv, class_type, data, obj_links[indiv]))
                seen.add(ent_text)

    for ent in doc.ents:
        ent_text = ent.text.strip()
        if ent_text in seen:
            continue
        if ent.label_ == "GPE":
            loc_class = "Region" if "region" in ent.text.lower() else "City"
            indiv = create_individual(ent.text.strip(), loc_class)
            triples.append((indiv, loc_class, {
                "hasName": ent.text.strip(),
                "hasLocationType": loc_class
            }, {}))
        elif ent.label_ == "DATE":
            date_data = {"hasLabelDate": ent.text}
            try:
                parsed = date_parse(ent.text, fuzzy=False)
                iso_date = parsed.date().isoformat()
                date_data["hasExactDate"] = iso_date
            except (ParserError, ValueError):
                pass
            indiv = create_individual(ent.text, "Date")
            triples.append((indiv, "Date", date_data, {}))
        elif ent.label_ == "EVENT":
            indiv = create_individual(ent_text, "HistoricEvent")
            triples.append((indiv, "HistoricEvent", {"hasName": ent_text}, {}))

    return triples

# ==== MAIN ====
if __name__ == "__main__":
    input_text = """
The Orthodox Church of Saint Nicholas, located in the city of Voskopoja, was built in the 18th century. 
It is dedicated to the Orthodox Christian religion and reflects the Byzantine architectural style. 
This church, commissioned by local artisans during the Ottoman Empire, is considered a symbol of Albania's Christian cultural identity and heritage.

The Castle of Gjirokastër, a medieval fortress built in the 12th century, dominates the southern city of Gjirokastër. 
It features stone walls, towers, and a clock tower added in the 19th century. 
Constructed during the Byzantine era and later expanded by Ali Pasha of Tepelena, the castle served military and administrative purposes. 
It played a strategic role during the Albanian National Awakening, a major 19th-century historical event.

The Et'hem Bey Mosque, located in Tirana, was built in the early 19th century. 
It is known for its intricate Islamic frescoes and Ottoman architectural style. 
The mosque was commissioned by Molla Bey and completed by his son Haxhi Et'hem Bey. 
It remains a sacred religious building for the Muslim community and represents an important cultural and historical monument in Albania.

The ruins of the ancient city of Butrint, located near the Vivari Channel in southern Albania, date back to the 7th century BC. 
Initially founded as a Greek colony, it evolved into a Roman city and later became a bishopric under Byzantine rule. 
The city includes temples, a basilica, a theatre, and Roman baths. 
It was rediscovered by Italian archaeologist Luigi Maria Ugolini in the 1920s and declared a UNESCO World Heritage Site in 1992 due to its immense historical value.

    """

    entities = process_text(input_text)

    with open("heritage_output.ttl", "w", encoding="utf-8") as f:
        f.write("@prefix : <http://www.semanticweb.org/ana/ontologies/2025/4/albania/>  .\n")
        f.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n\n")
        for subj, cls, data, obj_data in entities:
            turtle_block = format_turtle_block(subj, cls, data, obj_data)
            f.write(turtle_block + "\n\n")

    print(" RDF triples saved in Turtle format to 'heritage_output.ttl'")

