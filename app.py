from flask import Flask, request, render_template, redirect
from neo4j import GraphDatabase


driver = GraphDatabase.driver(uri="bolt://localhost:7687", auth=("neo4j", "456987"))
session = driver.session()

app = Flask(__name__)


@app.route('/')
def hello_world():
    query = """
        match (f:Flat) return count(f) as number_of_flats
    """
    results1 = session.run(query)
    number_of_flats = 0
    for result in results1:
        number_of_flats = result["number_of_flats"]

    query2 = """
        match (s:Student) return ID(s) as student
    """
    results2 = session.run(query2)
    list_of_ids_students = []
    for result in results2:
        list_of_ids_students.append(result["student"])
    print(list_of_ids_students)
    query3 = """
        match (f:Flat) return ID(f) as flat
    """
    results3 = session.run(query3)
    list_of_ids_flats = []
    for result in results3:
        list_of_ids_flats.append(result["flat"])

    print(list_of_ids_flats)

    for i in range(len(list_of_ids_flats)):
        query4 = f"MATCH(s:Student),(f:Flat) WHERE ID(s) = {list_of_ids_students[i]} AND ID(f) = {list_of_ids_flats[i]} CREATE (s)-[r:RELTYPE]->(f) RETURN type(r)"
        result = session.run(query4)

    # delete the settled students
    n = len(list_of_ids_flats)
    unsettled_students = list_of_ids_students[n:]

    # query = """match(s: Student)-[: RELTYPE]->(f:Flat)
    # with f as flat, s as student, count(s) as rels, avg(s.age) as avg_age, collect(
    #         s) as students where rels < flat.numberOfRooms return flat, students Order by student.sex asc
    # """
    # results = session.run(query)
    # for result in results:
    #     print(result)
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
