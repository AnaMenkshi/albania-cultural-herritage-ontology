with open("final_merged_output.ttl", "w", encoding="utf-8") as final:
    with open("cultural_heritage_ontology.ttl", "r", encoding="utf-8") as onto:
        final.write(onto.read() + "\n")
    with open("heritage_output.ttl", "r", encoding="utf-8") as indivs:
        final.write(indivs.read())
