from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

FUSEKI_ENDPOINT = "http://localhost:3030/albanian_cultural_heritage_ds/sparql"
PREFIXES = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ex: <http://www.semanticweb.org/ana/ontologies/2025/4/albania/>
"""

def run_sparql(query):
    full_query = PREFIXES + query
    response = requests.post(FUSEKI_ENDPOINT, data={'query': full_query},
                             headers={'Accept': 'application/sparql-results+json'})
    if response.status_code != 200:
        raise Exception(f"SPARQL query failed: {response.text}")
    return response.json()['results']['bindings']

def get_entity_uri(name):
    query = f"""
    SELECT ?s WHERE {{
        ?s (rdfs:label|ex:hasName) ?label .
        FILTER(CONTAINS(LCASE(STR(?label)), LCASE("{name}")))
    }} LIMIT 1
    """
    results = run_sparql(query)
    return results[0]['s']['value'] if results else None

def get_label(uri):
    query = f"""
    SELECT ?label WHERE {{
        OPTIONAL {{ <{uri}> rdfs:label ?label }}
        OPTIONAL {{ <{uri}> ex:hasName ?label }}
        FILTER(BOUND(?label))
    }} LIMIT 1
    """
    results = run_sparql(query)
    return results[0]['label']['value'] if results else uri.split('/')[-1]

def get_entity_info(uri):
    query = f"""
    SELECT ?prop ?val WHERE {{
        <{uri}> ?prop ?val .
        FILTER(!isIRI(?val))
    }}
    """
    results = run_sparql(query)
    info = {}
    for r in results:
        prop = r['prop']['value'].split('/')[-1]
        val = r['val']['value']
        if prop not in info:
            info[prop] = []
        if val not in info[prop]:
            info[prop].append(val)
    return info

def get_entity_types(uri):
    query = f"""
    SELECT ?type WHERE {{
        <{uri}> rdf:type ?type .
        FILTER(?type != owl:NamedIndividual)
    }}
    """
    result = run_sparql(query)
    return [r['type']['value'].split('/')[-1] for r in result]

def get_related_by_property(uri, prop):
    query = f"""
    SELECT ?val WHERE {{ <{uri}> ex:{prop} ?val }} LIMIT 1
    """
    result = run_sparql(query)
    if not result:
        return []
    val = result[0]['val']['value']
    val_str = f"<{val}>" if val.startswith("http") else f'"{val}"'
    query2 = f"""
    SELECT ?s ?label WHERE {{
        ?s ex:{prop} {val_str} .
        OPTIONAL {{ ?s rdfs:label ?label }}
        OPTIONAL {{ ?s ex:hasName ?label }}
        FILTER(?s != <{uri}>)
    }} LIMIT 10
    """
    result2 = run_sparql(query2)
    return [(r['label']['value'] if 'label' in r else r['s']['value'].split('/')[-1]) for r in result2]

def get_related_objects(uri, properties):
    all_related = []
    for prop in properties:
        query = f"""
        SELECT ?obj ?label WHERE {{
            <{uri}> ex:{prop} ?obj .
            OPTIONAL {{ ?obj rdfs:label ?label }}
            OPTIONAL {{ ?obj ex:hasName ?label }}
        }} LIMIT 10
        """
        results = run_sparql(query)
        if results:
            all_related.append((prop, [(r['label']['value'] if 'label' in r else r['obj']['value'].split('/')[-1]) for r in results]))
    return all_related

def get_items_displayed_in_same_museum(uri):
    query = f"""
    SELECT ?museum WHERE {{ <{uri}> ex:exhibitedIn ?museum }} LIMIT 1
    """
    results = run_sparql(query)
    if not results:
        return (None, [])
    museum_uri = results[0]['museum']['value']
    museum_label = get_label(museum_uri)
    query2 = f"""
    SELECT ?item ?label WHERE {{
        ?item ex:exhibitedIn <{museum_uri}> .
        OPTIONAL {{ ?item rdfs:label ?label }}
        OPTIONAL {{ ?item ex:hasName ?label }}
        FILTER(?item != <{uri}>)
    }} LIMIT 15
    """
    items = run_sparql(query2)
    return museum_label, [(r['label']['value'] if 'label' in r else r['item']['value'].split('/')[-1]) for r in items]

@app.route('/', methods=['GET', 'POST'])
def home():
    result_html = ''
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            result_html = "<p style='color:red;'>Please enter a cultural entity name.</p>"
        else:
            uri = get_entity_uri(name)
            if not uri:
                result_html = f"<p>No cultural entity found matching '<strong>{name}</strong>'.</p>"
            else:
                label = get_label(uri)
                types = get_entity_types(uri)
                info = get_entity_info(uri)

                result_html += f"<h3>{label}</h3>"
                result_html += f"<p><strong>Type:</strong> {', '.join(types)}</p>"

                if info:
                    result_html += "<h4>Details:</h4><ul>"
                    for k, vlist in info.items():
                        for v in vlist:
                            result_html += f"<li><b>{k.replace('_',' ').capitalize()}</b>: {v}</li>"
                    result_html += "</ul>"

                data_props = [
                    'hasArchitecturalStyle', 'hasConstructionDate', 'hasCreator', 'hasCulturalContext',
                    'hasCulturalHeritageStatus', 'hasCulturalSignificance', 'hasDateOfDiscovery',
                    'hasEventDuration', 'hasExactDate', 'hasLanguage', 'hasLocationType',
                    'hasMaterial', 'hasName', 'hasPeriodOfUse', 'hasReligion',
                    'hasRestorationDate', 'hasStartDate', 'hasUNESCODesignation', 'hasWebsite',
                    'hasLocation'
                ]

                for related_prop in data_props:
                    related_items = get_related_by_property(uri, related_prop)
                    if related_items:
                        result_html += f"<h4>Related by {related_prop.replace('has','').capitalize()}:</h4><ul>"
                        for item in related_items:
                            result_html += f"<li>{item}</li>"
                        result_html += "</ul>"

                object_props = [
                    'displays', 'commemorates', 'exhibitedIn', 'associatedWithEvent',
                    'locatedIn', 'originatedFrom', 'datedFrom',
                    'hasHistoricalPeriod', 'occurredIn', 'occurredOn', 'isPartOf'
                ]
                object_related = get_related_objects(uri, object_props)
                for prop, items in object_related:
                    if items:
                        result_html += f"<h4>Related via {prop}:</h4><ul>"
                        for item in items:
                            result_html += f"<li>{item}</li>"
                        result_html += "</ul>"

                museum_label, museum_items = get_items_displayed_in_same_museum(uri)
                if museum_label:
                    result_html += f"<h4>Displayed in: {museum_label}</h4>"
                if museum_items:
                    result_html += f"<h5>Other items in this museum:</h5><ul>"
                    for item in museum_items:
                        result_html += f"<li>{item}</li>"
                    result_html += "</ul>"

    return render_template_string("""
<html>
<head><title>Cultural Heritage Explorer</title></head>
<body style="font-family:Arial;">
    <h2>Cultural Heritage Explorer</h2>
    <form method="post">
        <input type="text" name="name" placeholder="Enter cultural entity name" size="40" autocomplete="off" />
        <input type="submit" value="Search" />
    </form>
    <div style="margin-top:20px;">
        {{result_html|safe}}
    </div>
</body>
</html>
""", result_html=result_html)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
