#  Albanian Cultural Heritage Ontology Project

This project aims to digitally preserve and model the **Intangible Cultural Heritage (ICH) of Albania** using Semantic Web technologies, Natural Language Processing (NLP), and a browser-based interface for querying and exploration.

It includes:
- A formal ontology of Albanian cultural elements
- A SPARQL-based browser for querying individuals and discovering relationships
- NLP tools that automatically create new individuals from natural language text

---

##  Project Structure

```
├── ontology.rdf                    # Main ontology in RDF/XML format
├── cultural_heritage_ontology.ttl # Ontology in Turtle (.ttl) format
├── sparql_service/                # Browser and SPARQL interface for searching and recommendations
├── nlp/
│   ├── NLP.py                     # NLP script using spaCy to generate new individuals from text
│   ├── heritage_output.ttl       # RDF individuals created from NLP
│   ├── merge.py                  # Merges original ontology and NLP individuals
│   └── final_merged_output.ttl   # Final ontology with both original and NLP-generated individuals
```

---

##  Ontology: `ontology.rdf` and `cultural_heritage_ontology.ttl`

This ontology models Albania’s rich intangible heritage including:
- Traditional dances
- Rituals and customs
- Music and oral expressions
- Regional cultural identity

It is based on standards like:
- **CIDOC CRM** (cultural heritage metadata)
- **SKOS** (thesauri and taxonomies)
- **UNESCO ICH ontology** for intangible heritage

---

##  Browser & SPARQL Service (`sparql_service/`)

This folder contains the code to run a lightweight browser-based app that allows:

-  Searching for individuals in the ontology
-  Discovering recommendations based on semantic relations
- Visualizing how cultural elements relate (e.g., dances from the same region)

> ⚠️ Requires [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) running and loaded with `ontology.rdf` in the dataset named albanian_cultural_heritage_ds

---

##  NLP Component (`nlp/`)

### What it does:
- Takes **paragraphs about cultural heritage** as input
- Uses the `spaCy` NLP library to extract named entities and features
- Creates RDF individuals that match the ontology’s structure

### Files:
- `NLP.py`: Runs the NLP and generates new individuals
- `heritage_output.ttl`: Contains individuals extracted from the paragraph
- `merge.py`: Merges the original ontology with NLP output
- `final_merged_output.ttl`: Final merged ontology used in the browser

---

##  How to Use the Project

### Step 1: Load the Ontology in Apache Jena Fuseki
- Run Fuseki
- Create a dataset albanian_cultural_heritage_ds
- Upload `final_merged_output.ttl`

### Step 2: Run the Browser App
- Navigate to the `sparql_service/` folder
- Start your app (e.g., if it's HTML/JS, open `index.html` in a browser)

### Step 3: Use NLP to Add More Individuals (optional)
```bash
cd nlp
python NLP.py            # Generate individuals from new cultural descriptions
python merge.py          # Merge new individuals into the ontology
```
- This will update `final_merged_output.ttl`

---

## Requirements

- Python 3.8+
- [`spaCy`](https://spacy.io/)
- [`rdflib`](https://rdflib.readthedocs.io/) for working with RDF in Python

Install dependencies:
```bash
pip install spacy rdflib
python -m spacy download en_core_web_sm
```

