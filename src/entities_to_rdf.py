#!/usr/bin/env python
# coding: utf-8

# In[14]:
import json

import rdflib
from rdflib import Graph, RDF, URIRef, Literal
from rdflib import Namespace
from rdflib.namespace import DCTERMS, SKOS, PROV, PROF, FOAF


class SocialSemanticWeb(Graph):
    # URL is at [0] and the graph URI is at [1]
    __socmed_sites = {'facebook': ['https://facebook.com/', None],
                      'instagram': ['https://instagram.com/', None],
                      }
    
    # establish the namespaces -- A.K.A import the Ontologies
    SSO = Namespace('http://david.jefts/sso/')
    FOAF = Namespace('http://xmlns.com/foaf/0.1/')
    SIOC = Namespace('http://rdfs.org/sioc/ns#')
    EDU = Namespace('https://schema.org/EducationalOccupationalCredential')
    
    def __init__(self, user, fb_information):
        super(SocialSemanticWeb, self).__init__()
        self.bind('sso', self.SSO)
        self.bind('foaf', self.FOAF)
        self.bind('sioc', self.SIOC)
        self.namespace_manager = self.namespace_manager
        
        # add social medias to graph
        for site in self.__socmed_sites:
            self.__socmed_sites[site][1] = self.social_service_to_rdf(self.__socmed_sites[site][0])
            
        # user node instantiation
        self.user_uri = URIRef(self.SSO + user.name.replace(' ', '-'))
        print(self.user_uri)  # = rdflib.term.URIRef(u'http://david.jefts/sso/John-Keck')
        self.add((self.user_uri, RDF.type, self.FOAF.Person))
        
        # user accounts initialization
        # Facebook Account:
        self.online_account_to_rdf(self.user_uri, fb_information['permalink'],
                                   user.fb_username, self.__socmed_sites['facebook'][1])
    
    def social_service_to_rdf(self, social_media):
        site_uri = URIRef(social_media)
        self.add((site_uri, RDF.type, self.FOAF.Document))
        return site_uri
    
    def online_account_to_rdf(self, user_uri, user_homepage, account_username, service_uri):
        account_uri = URIRef(user_homepage)
        self.add((account_uri, RDF.type, self.FOAF.OnlineAccount))
        self.add((account_uri, self.FOAF.accountName, Literal(account_username)))
        self.add((account_uri, self.FOAF.accountServiceHomepage, service_uri))
        self.add((user_uri, self.FOAF.account, account_uri))
        return account_uri
    
    def online_friend_to_rdf(self, user_uri, friend_uri, friend_name, account_link, friend_username, service_uri):
        # TODO: ensure friend doesn't exist in graph already
        # user node instantiation
        self.add((friend_uri, RDF.type, self.FOAF.Person))
        
        # Friend's FB Account:
        self.online_account_to_rdf(friend_uri, account_link, friend_username, service_uri)
        
        # connect friend to user
        self.add((friend_uri, RDF.type, self.FOAF.Person))
        self.add((friend_uri, self.FOAF.name, Literal(friend_name)))
        self.add((user_uri, self.FOAF.knows, friend_uri))
        self.add((friend_uri, self.FOAF.knows, user_uri))
        return friend_uri
    
    def facebook_friend_to_rdf(self, user_uri, friend_uri, friend_name, account_link, friend_username):
        return self.online_friend_to_rdf(user_uri, friend_uri, friend_name, account_link, friend_username,
                                         self.__socmed_sites['facebook'][1])
    
    def diploma_to_rdf(self, degree, school):
        degree_uri = URIRef(degree + ' - ' + school)
        school_uri = URIRef(school)
        self.add((degree_uri, RDF.type, self.EDU))
        self.add((school_uri, RDF.type,))
        self.add((degree_uri, self.EDU.recognizedBy, school_uri))
        self.add((user_fb_uri, self.FOAF.hasCredential,))
    
    def get_namespaces(self):
        namespaces = {}
        for prefix, namespace in self.namespace_manager.namespaces():
            namespaces[prefix] = namespace
        return namespaces
    
    def print_namespaces(self):
        return json.dumps(self.get_namespaces(), indent = 2)
    
    def save(self):
        """
        Saves the graph to "SemanticSecurity/src/graph.ttl"
        """
        self.serialize(destination = "graph.ttl", format = 'turtle', encoding = 'utf-8')
    
    def __str__(self):
        """
        Serializes the graph using RDF Turtle Format
        :return: string representation of the knowledge graph
        """
        out = "--- Knowledge Graph ---\n"
        # Format support can be extended with plugins,
        #    but "xml", "n3", "turtle", "nt", "pretty-xml", "trix", "trig" and "nquads" are built in."""
        out += self.serialize(format = 'turtle', encoding = 'utf-8').decode("utf-8")
        return out


if __name__ == "__main__":
    g = Graph()
    g.bind("foaf", FOAF)
    
    JKeck = URIRef('https://www.facebook.com/john.keck.125')
    DJefts = URIRef('https://www.facebook.com/david.jefts')
    demonSlayer = URIRef('https://www.imdb.com/title/tt9335498/')
    JOrtiz = URIRef('https://www.facebook.com/juan.ortizcouder')
    siocNamespace = Namespace('http://rdfs.org/sioc/ns#')
    
    JKeckName = Literal('John W Keck')
    DJeftsName = Literal('David Jefts')
    JOrtizName = Literal("Juan Ortiz")
    DSname = Literal('Demon Slayer')
    age = Literal(56)
    
    g.add((JOrtiz, RDF.type, FOAF.Person))
    g.add((JOrtiz, FOAF.name, JOrtizName))
    g.add((JOrtiz, FOAF.knows, DJefts))
    g.add((JOrtiz, FOAF.knows, JKeck))
    
    g.add((JKeck, RDF.type, FOAF.Person))
    g.add((JKeck, FOAF.name, JKeckName))
    g.add((JKeck, FOAF.knows, DJefts))
    g.add((JKeck, FOAF.knows, JOrtiz))
    
    g.add((DJefts, RDF.type, FOAF.Person))
    g.add((DJefts, FOAF.name, DJeftsName))
    g.add((DJefts, FOAF.knows, JKeck))
    g.add((DJefts, FOAF.knows, JOrtiz))
    
    g.add((JKeck, siocNamespace.likes, demonSlayer))
    g.add((demonSlayer, FOAF.name, DSname))
    
    # print(g.serialize(format="turtle").decode("utf-8"))
    
    # print("--- printing raw triples ---")
    # for s, p, o in g:
    #    print((s, p, o))
    
    # print all the data in the Notation3 format
    print("--- printing mboxes ---")
    print(g.serialize(format = 'n3').decode("utf-8"))
