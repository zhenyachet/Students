from flask import Flask, request, render_template, redirect
from neo4j import GraphDatabase


driver = GraphDatabase.driver(uri="bolt://localhost:7687", auth=("neo4j", "456987"))
session = driver.session()

app = Flask(__name__)


@app.route('/')
def hello_world():
    # # # batch upload from csv
    query = """
    load csv with headers from "file:///Students.csv" as students create (a1:Student {name: students.name, age:tointeger(students.age), sex:students.sex,nationality:students.nationality})
    """
    session.run(query)
    query2 = """
    load csv with headers from "file:///Flats.csv" as flats create (a1:Flat {name: flats.name, numberOfRooms:tointeger(flats.numberOfRooms)})
    """
    session.run(query2)

    query = """
        match (f:Flat) return count(f) as number_of_flats
    """
    results1 = session.run(query)
    number_of_flats = 0
    for result in results1:
        number_of_flats = result["number_of_flats"]

    query2 = """
        match (s:Student) return s.name as name
    """
    results2 = session.run(query2)
    list_of_names_students = []
    for result in results2:
        list_of_names_students.append(result["name"])
    query3 = """
        match (f:Flat) return ID(f) as flat
    """
    results3 = session.run(query3)
    list_of_ids_flats = []
    for result in results3:
        list_of_ids_flats.append(result["flat"])


    for i in range(len(list_of_ids_flats)):
        query4 = f"MATCH(s:Student),(f:Flat) WHERE s.name = '{list_of_names_students[i]}' AND ID(f) = {list_of_ids_flats[i]} CREATE (s)-[r:lives_in]->(f) RETURN type(r)"
        result = session.run(query4)

    # # delete the settled students
    n = len(list_of_ids_flats)
    unsettled_students = list_of_names_students[n:]
    query = """match(s: Student)-[: lives_in]->(f:Flat)
    with f as flat, s as student, count(s) as rels, avg(s.age) as avg_age, collect(
            s) as students where rels < flat.numberOfRooms return flat, students Order by student.sex asc
    """
    session.run(query)

    # find the appartment for the rest of the students
    for student in unsettled_students:
        query = """ match (f:Flat)<-[r2]-(s:Student) 
                    match (s4:Student{name:"%s"}) 
                    with f as flat, avg(s.age) as avg_age , count(r2) as rels, s4.age as age_of_person, (apoc.coll.occurrences(collect(s.sex), s4.sex) * 4) as result_of_sex,(apoc.coll.occurrences(collect(s.nationality), s4.nationality) * 4) as result_of_nationality, abs(s4.age - avg(s.age))*(-0.25) as result_of_age 
                    where rels<flat.numberOfRooms return flat,rels, avg_age, result_of_age,result_of_sex, result_of_nationality, (result_of_sex+ result_of_age+result_of_nationality)as weight
                    order by weight desc
                    limit 1
        """ % student
        results = session.run(query)
        flat_name = ''
        for result in results:
            dictionary = (result.data())
            flat_name = dictionary['flat']['name']


        query = f"""
        MATCH
        (a:Student),
        (b:Flat)
        WHERE a.name = '{student}' AND b.name = '{flat_name}'
        CREATE (a)-[r:RELTYPE]->(b)
        RETURN type(r)
        """
        session.run(query)

    return 'Hello World!'


if __name__ == '__main__':
    app.run()
